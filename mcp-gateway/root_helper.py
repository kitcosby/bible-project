#!/usr/bin/env python3
"""Privileged helper for the Lampy MCP gateway (Phase 5).

Installed root-owned at /usr/local/sbin/mcpgw-root-helper.py and reachable
from the unprivileged gateway process ONLY through a setuid launcher
(root_helper_launcher.c, root:root mode 4755) that refuses every caller
except the mcpgw user - the distro ships no sudo, so the launcher is the
gateway's single privileged path, and this file is root-owned precisely
so the invoking account cannot modify the code it elevates. The gateway
(running as mcpgw) passes one JSON request on stdin and reads one JSON
reply on stdout:

  {"op": "write", "root": ..., "subpath": ..., "content_b64": ...}
  {"op": "edit",  "root": ..., "subpath": ..., "old": ..., "new": ...}
  {"op": "exec",  "command": ..., "cwd_root": ..., "cwd_subpath": ...,
   "timeout": 60}

Filesystem ops are confined to the gateway's advertised write roots,
canonicalized here again (the helper does not trust its caller), with
the gateway's secret-file denylist applied to every path component.
exec runs the command with bash as root, in a working directory inside
those roots: it is the general-access path the owner granted, and the
gateway audit-logs every invocation before making it.

Path resolution (bible-project issue #35): paths are resolved by
walking directory FILE DESCRIPTORS from a pinned root fd, never by
canonicalizing a pathname and reusing it. The previous implementation
validated a pathname with Path.resolve() and then operated on that
pathname (stat / mkdir / mkstemp / os.replace by path), so a symlink
swapped into any component between validation and use could redirect
a privileged write outside the allowlisted roots (TOCTOU). Here every
component is opened relative to a held parent dirfd with O_NOFOLLOW;
held fds pin directory inodes, so later pathname swaps cannot move
the operation. Symlinks - which Path.resolve() followed - are still
followed, but under control: relative targets only, spliced into the
walk component by component with the denylist applied to each, ".."
tracked against the held fd stack so it can never pop above the
root, and expansions bounded to kill link loops. Absolute symlink
targets fail closed.
"""
import base64
import binascii
import errno
import json
import os
import re
import secrets
import stat
import subprocess
import sys
from pathlib import Path

ROOTS = {
    "projects": Path("/home/mcpgw/projects"),
    "bible-website": Path("/opt/bible/website"),
    "bible-data": Path("/opt/bible"),
    "stage": Path("/opt/stage"),
    "bible-app-api": Path("/opt/bible-app-api"),
}
DENY_COMPONENT = re.compile(
    r"((^|\.)env($|\.)|\.envrc$|secret|credential|\.key$|\.pem$"
    r"|^id_(rsa|ed25519|toe)|\.password$|\.cred$|tokens\.json$)",
    re.IGNORECASE,
)
MAX_WRITE_BYTES = 1024 * 1024
MAX_OUTPUT_CHARS = 20000
# Upper bound on symlink expansions per resolution (matches the
# kernel's own MAXSYMLINKS); anything beyond it is a link loop.
MAX_LINK_EXPANSIONS = 40


def reply(obj):
    print(json.dumps(obj))
    sys.exit(0)


def fail(msg):
    reply({"ok": False, "error": str(msg)[:500]})


def _check_component(comp):
    if comp == ".git" or DENY_COMPONENT.search(comp):
        fail(f"path component denied: {comp}")


class _Resolution:
    """A path being resolved against a pinned root directory fd.

    Invariant: self.dir_fds holds exactly the open directory fds from
    the root (index 0) down to the current directory (index -1), and
    self.parts holds the display name of each level below the root.
    Because directories are held by fd, renaming or symlink-swapping
    any pathname component after it was opened has no effect on where
    this resolution points.
    """

    def __init__(self, root_name):
        if root_name not in ROOTS:
            fail(f"unknown root {root_name!r}")
        self.root_path = str(ROOTS[root_name])
        # The root itself is operator-configured (trusted, as before);
        # it is opened once and the fd pins its inode for the whole op.
        root_fd = os.open(self.root_path, os.O_RDONLY | os.O_DIRECTORY)
        self.dir_fds = [root_fd]
        self.parts = []
        self.expansions = 0

    def close(self):
        while self.dir_fds:
            try:
                os.close(self.dir_fds.pop())
            except OSError:
                pass

    @property
    def dir_fd(self):
        return self.dir_fds[-1]

    def display_path(self, final=None):
        parts = [self.root_path, *self.parts]
        if final:
            parts.append(final)
        return "/".join(parts)

    def _pop_dir(self):
        if len(self.dir_fds) == 1:
            fail("path escapes the allowlisted root")
        os.close(self.dir_fds.pop())
        self.parts.pop()

    def _symlink_error(self, name, exc):
        """True when a failed open actually means "name is a symlink".
        O_NOFOLLOW reports ELOOP, but with O_DIRECTORY the kernel
        reports ENOTDIR instead (a symlink is not a directory, and it
        may not be followed to check the target) - lstat decides."""
        if exc.errno == errno.ELOOP:
            return True
        return exc.errno == errno.ENOTDIR and self._is_symlink(name)

    def _is_symlink(self, name):
        try:
            return stat.S_ISLNK(os.stat(
                name, dir_fd=self.dir_fd, follow_symlinks=False).st_mode)
        except OSError:
            return False

    def _splice(self, name):
        """Read the symlink `name` in the current directory and return
        its target's components for controlled re-walking. Relative
        targets only; the caller re-checks every spliced component."""
        target = os.readlink(name, dir_fd=self.dir_fd)
        self.expansions += 1
        if self.expansions > MAX_LINK_EXPANSIONS:
            fail("too many symlink expansions")
        if os.path.isabs(target):
            fail("absolute symlink targets are refused")
        return target.split("/")

    def walk_dirs(self, queue, create):
        """Consume the component list `queue` as directories, starting
        from the current directory. With create=True, missing
        components are created (the old atomic_write's
        mkdir(parents=True) behaviour, for write ops only)."""
        while queue:
            comp = queue.pop(0)
            if comp == "" or comp == ".":
                continue
            if comp == "..":
                self._pop_dir()
                continue
            _check_component(comp)
            try:
                fd = os.open(comp,
                             os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                             dir_fd=self.dir_fd)
            except FileNotFoundError:
                if not create:
                    fail(f"no such directory: {comp}")
                try:
                    os.mkdir(comp, 0o777, dir_fd=self.dir_fd)
                except FileExistsError:
                    pass
                except OSError as e:
                    fail(e)
                # Re-open what is there NOW; if a symlink was swapped
                # in under our mkdir, the ELOOP branch below takes it
                # through controlled expansion instead.
                try:
                    fd = os.open(comp,
                                 os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                 dir_fd=self.dir_fd)
                except OSError as e:
                    if self._symlink_error(comp, e):
                        queue[:0] = self._splice(comp)
                        continue
                    fail(e)
            except OSError as e:
                if self._symlink_error(comp, e):
                    queue[:0] = self._splice(comp)
                    continue
                fail(e)
            self.dir_fds.append(fd)
            self.parts.append(comp)

    def open_final(self, name, create):
        """Resolve the final component `name` from the current
        directory. Returns (fd, fstat, final_name): fd is an open
        O_NOFOLLOW descriptor for the entry, or (None, None, name)
        when the entry does not exist. Symlinks in final position -
        including ones spliced in by expansions - are resolved by the
        same controlled walk; on return, self.dir_fds is topped by
        the directory that actually contains the final entry."""
        queue = [name]
        while True:
            if not queue:
                fail("target is a directory")
            comp = queue.pop(0)
            if comp == "" or comp == ".":
                continue
            if comp == "..":
                self._pop_dir()
                continue
            _check_component(comp)
            if queue:
                # Components still follow: this one is a directory.
                self.walk_dirs([comp], create)
                continue
            try:
                fd = os.open(comp,
                             os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                             dir_fd=self.dir_fd)
            except FileNotFoundError:
                return None, None, comp
            except OSError as e:
                if self._symlink_error(comp, e):
                    queue = self._splice(comp)
                    continue
                fail(e)
            return fd, os.fstat(fd), comp


def _resolve_file(root_name, subpath, create):
    """Resolve a write/edit target. Returns (resolution, fd, fstat,
    final_name); fd/fstat are None when the target does not exist."""
    res = _Resolution(root_name)
    try:
        comps = subpath.split("/") if subpath else []
        if not comps:
            fail("target is a directory")
        res.walk_dirs(list(comps[:-1]), create)
        fd, st, name = res.open_final(comps[-1], create)
        return res, fd, st, name
    except BaseException:
        res.close()
        raise


def _resolve_dir(root_name, subpath):
    """Resolve an exec cwd to a _Resolution topped by its dirfd."""
    res = _Resolution(root_name)
    try:
        res.walk_dirs(subpath.split("/") if subpath else [], False)
        return res
    except BaseException:
        res.close()
        raise


def _atomic_write(dir_fd, name, data, mode):
    # The temp file is created inside the held directory fd and
    # renamed over the target name inside that same fd. rename(2)
    # replaces the destination NAME itself - a symlink swapped into
    # that name is what gets replaced, never followed - and because
    # the directory is pinned by fd, the rename cannot leave the
    # allowlisted tree whatever happens to the pathnames.
    # (tempfile.mkstemp has no dir_fd parameter; this O_EXCL loop is
    # the same construction done with os.open.)
    tmp = None
    fd = None
    for _ in range(16):
        cand = ".mcpgw-" + secrets.token_hex(8)
        try:
            fd = os.open(cand,
                         os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                         0o600, dir_fd=dir_fd)
            tmp = cand
            break
        except FileExistsError:
            continue
    if tmp is None:
        fail("could not create a temp file in the target directory")
    try:
        os.fchmod(fd, mode if mode is not None else 0o644)
        with os.fdopen(fd, "wb") as f:
            fd = None
            f.write(data)
        os.replace(tmp, name, src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
    except BaseException:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        try:
            os.unlink(tmp, dir_fd=dir_fd)
        except OSError:
            pass
        raise


def op_write(req):
    try:
        data = base64.b64decode(req["content_b64"], validate=True)
    except (binascii.Error, KeyError):
        fail("content_b64 missing or invalid")
    if len(data) > MAX_WRITE_BYTES:
        fail("content larger than the 1 MB write cap")
    res, fd, st, name = _resolve_file(req["root"], req["subpath"], True)
    try:
        mode = None
        if st is not None:
            if not stat.S_ISREG(st.st_mode):
                if stat.S_ISDIR(st.st_mode):
                    fail("target is a directory")
                fail(f"not a file: {res.display_path(name)}")
            mode = stat.S_IMODE(st.st_mode)
        if fd is not None:
            os.close(fd)
            fd = None
        _atomic_write(res.dir_fd, name, data, mode)
        reply({"ok": True, "bytes": len(data),
               "path": res.display_path(name)})
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        res.close()


def op_edit(req):
    old, new = req.get("old", ""), req.get("new", "")
    if not old:
        fail("old must be non-empty")
    if len(new.encode("utf-8")) > MAX_WRITE_BYTES:
        fail("replacement larger than the 1 MB write cap")
    res, fd, st, name = _resolve_file(req["root"], req["subpath"], False)
    try:
        if fd is None or not stat.S_ISREG(st.st_mode):
            fail(f"not a file: {res.display_path(name)}")
        chunks = []
        while True:
            chunk = os.read(fd, 1 << 20)
            if not chunk:
                break
            chunks.append(chunk)
        # The content is read from the opened fd, never re-read
        # through a pathname.
        try:
            text = b"".join(chunks).decode("utf-8")
        except UnicodeDecodeError:
            fail("not a UTF-8 text file")
        count = text.count(old)
        if count != 1:
            fail(f"old occurs {count} times (exactly 1 required)")
        data = text.replace(old, new).encode("utf-8")
        # Fail closed if the name we are about to replace no longer
        # denotes the exact inode we read (or has become a symlink):
        # the replacement must land on the file whose content was
        # checked, in the directory pinned by the parent dirfd.
        lst = os.stat(name, dir_fd=res.dir_fd, follow_symlinks=False)
        if stat.S_ISLNK(lst.st_mode) or \
                (lst.st_dev, lst.st_ino) != (st.st_dev, st.st_ino):
            fail("target changed while it was being read; refusing")
        _atomic_write(res.dir_fd, name, data, stat.S_IMODE(st.st_mode))
        reply({"ok": True, "bytes": len(data),
               "path": res.display_path(name)})
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        res.close()


def _text(value):
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def op_exec(req):
    command = req.get("command", "")
    if not command.strip():
        fail("command must be non-empty")
    res = _resolve_dir(req.get("cwd_root", "projects"),
                       req.get("cwd_subpath", ""))
    try:
        cwd_fd = res.dir_fd
        cwd_display = res.display_path()
        timeout = max(1, min(int(req.get("timeout", 60)), 600))
        timed_out = False
        try:
            # The child chdirs through /proc/self/fd/<cwd_fd> with the
            # fd passed across exec: it lands in the pinned directory
            # inode itself, not in whatever the pathname points to by
            # the time bash starts.
            proc = subprocess.run(
                ["/bin/bash", "-c", command],
                cwd=f"/proc/self/fd/{cwd_fd}", pass_fds=(cwd_fd,),
                capture_output=True, text=True, timeout=timeout,
            )
            exit_code, out, err = proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired as e:
            timed_out = True
            exit_code, out, err = None, _text(e.stdout), _text(e.stderr)
        reply({
            "ok": True,
            "exit_code": exit_code,
            "timed_out": timed_out,
            "stdout": (out or "")[:MAX_OUTPUT_CHARS],
            "stderr": (err or "")[:MAX_OUTPUT_CHARS],
            "stdout_truncated": len(out or "") > MAX_OUTPUT_CHARS,
            "stderr_truncated": len(err or "") > MAX_OUTPUT_CHARS,
            "cwd": cwd_display,
        })
    finally:
        res.close()


def _become_root():
    # The launcher sets our effective uid to 0 but leaves the real uid
    # as mcpgw, and bash (our exec child) drops euid to ruid at startup
    # unless they already match. Set both to 0 so every child process
    # is unambiguously root. When the helper is invoked WITHOUT the
    # launcher (euid != 0 and setuid refused), fail closed.
    if os.geteuid() == 0:
        try:
            os.setuid(0)
        except OSError:
            pass
    if os.geteuid() != 0 or os.getuid() != 0:
        fail("root helper is not running as root")


def main():
    _become_root()
    try:
        req = json.load(sys.stdin)
    except json.JSONDecodeError:
        fail("request is not JSON")
    op = req.get("op")
    try:
        if op == "write":
            op_write(req)
        elif op == "edit":
            op_edit(req)
        elif op == "exec":
            op_exec(req)
        else:
            fail(f"unknown op {op!r}")
    except Exception as e:  # noqa: BLE001 - report, never crash silently
        fail(e)


if __name__ == "__main__":
    main()
