#!/usr/bin/env python3
"""TOCTOU regression battery for the descriptor-relative root helper
(bible-project issue #35).

Invokes the fixed root_helper.py the way the gateway does - one JSON
request on stdin, one JSON reply on stdout, via a fresh subprocess per
request - but with the module's ROOTS monkeypatched to a scratch tree
through a small driver shim. The real roots and the deployed helper
are never touched. Must run as root (the helper fails closed
otherwise, by design).

Coverage:
  1  baseline write / edit / exec inside the scratch root
  2  symlink escape (absolute target, and relative ".." target)
  3  denylist reached through symlink expansion (secret, *.env)
  4  ".git" component refused (direct and nested)
  5  RACE: a thread swaps a mid-path directory between a real in-root
     dir and a symlink to an outside dir while writes stream through
     it - zero bytes may ever land outside the root
  6  final-component symlink: outside target never modified; in-root
     relative target still followed (edit + write), as before
  7  exec cwd pinning: normal cwd, in-root symlink cwd, symlink cwd
     escaping the root (refused, never runs outside)
  8  overwrite preserves an existing file's mode; new files are 0644
  9  traversal / unknown-root parity refusals
  10 legitimate in-root mid-path symlink still followed
  11 symlink loop refused (bounded expansions)

Prints one line per check and a SUMMARY; exit 1 on any failure.
"""
import base64
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
HELPER = HERE / "root_helper.py"

DRIVER = r"""
import importlib.util
import pathlib
import sys

spec = importlib.util.spec_from_file_location("root_helper_under_test",
                                              sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.ROOTS = {"scratch": pathlib.Path(sys.argv[2])}
mod.main()
"""

RESULTS = []


def record(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name
          + (f"  [{detail}]" if detail else ""), flush=True)


class Harness:
    def __init__(self):
        self.base = Path(tempfile.mkdtemp(prefix="toctou-test-"))
        self.root = self.base / "root"
        self.root.mkdir()
        self.outside = self.base / "outside"
        self.outside.mkdir()
        (self.outside / "victim.txt").write_text("ORIGINAL-OUTSIDE\n")
        self.driver = self.base / "driver.py"
        self.driver.write_text(DRIVER)

    def cleanup(self):
        shutil.rmtree(self.base, ignore_errors=True)

    def op(self, req, timeout=60):
        proc = subprocess.run(
            [sys.executable, str(self.driver), str(HELPER), str(self.root)],
            input=json.dumps(req), capture_output=True, text=True,
            timeout=timeout)
        lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
        if not lines:
            return {"ok": False,
                    "error": f"no reply (rc={proc.returncode}): "
                             f"{proc.stderr.strip()[-300:]}"}
        try:
            return json.loads(lines[-1])
        except json.JSONDecodeError:
            return {"ok": False, "error": f"bad reply: {lines[-1][:200]}"}

    def write(self, subpath, text):
        return self.op({
            "op": "write", "root": "scratch", "subpath": subpath,
            "content_b64": base64.b64encode(text.encode()).decode()})

    def edit(self, subpath, old, new):
        return self.op({"op": "edit", "root": "scratch",
                        "subpath": subpath, "old": old, "new": new})

    def exec(self, command, cwd_subpath=""):
        return self.op({"op": "exec", "root": "scratch",
                        "command": command, "cwd_root": "scratch",
                        "cwd_subpath": cwd_subpath, "timeout": 30})


def outside_tree(h):
    """Relative paths of everything under the outside dir."""
    found = []
    for dirpath, _dirnames, filenames in os.walk(h.outside):
        for name in filenames:
            found.append(str(Path(dirpath, name).relative_to(h.outside)))
    return sorted(found)


def main():
    if os.geteuid() != 0:
        print("FAIL this battery must run as root "
              "(the helper fails closed otherwise)")
        return 1
    h = Harness()
    try:
        run(h)
    finally:
        failed = [n for n, ok in RESULTS if not ok]
        print(f"SUMMARY total={len(RESULTS)} "
              f"pass={len(RESULTS) - len(failed)} fail={len(failed)}")
        if failed:
            print("FAILED:", "; ".join(failed))
        h.cleanup()
    return 1 if failed else 0


def run(h):
    root, outside = h.root, h.outside

    # ---- 1. baseline -------------------------------------------------
    r = h.write("a/b/hello.txt", "hello world\n")
    record("1 write creates file + parent dirs",
           r.get("ok") is True
           and (root / "a/b/hello.txt").read_text() == "hello world\n",
           str(r)[:140])
    r = h.edit("a/b/hello.txt", "world", "there")
    record("1 edit replaces the unique occurrence",
           r.get("ok") is True
           and (root / "a/b/hello.txt").read_text() == "hello there\n",
           str(r)[:140])
    r = h.exec("pwd -P; echo exec-ok > marker.txt", "a/b")
    record("1 exec runs with the pinned cwd (/proc/self/fd)",
           r.get("ok") is True and r.get("exit_code") == 0
           and r.get("stdout", "").splitlines()[0].strip()
           == str((root / "a/b").resolve())
           and (root / "a/b/marker.txt").read_text().strip() == "exec-ok",
           str(r)[:200])

    # ---- 2. symlink escape -------------------------------------------
    os.symlink(str(outside), root / "esc")
    r = h.write("esc/pwn.txt", "PWN\n")
    record("2 absolute symlink component escape refused",
           r.get("ok") is False and outside_tree(h) == ["victim.txt"],
           str(r)[:140])
    os.symlink("../outside", root / "esc2")
    r = h.write("esc2/pwn2.txt", "PWN\n")
    record("2 relative '..' symlink escape refused",
           r.get("ok") is False and outside_tree(h) == ["victim.txt"]
           and (outside / "victim.txt").read_text() == "ORIGINAL-OUTSIDE\n",
           str(r)[:140])

    # ---- 3. denylist through symlink expansion -----------------------
    (root / "vault/secret_stuff").mkdir(parents=True)
    os.symlink("vault/secret_stuff", root / "slink")
    r = h.write("slink/x.txt", "x")
    record("3 denied 'secret' component via symlink refused",
           r.get("ok") is False
           and not (root / "vault/secret_stuff/x.txt").exists(),
           str(r)[:140])
    (root / "vault/app.env").mkdir()
    os.symlink("vault/app.env", root / "elink")
    r = h.write("elink/x.txt", "x")
    record("3 denied '*.env' component via symlink refused",
           r.get("ok") is False
           and not (root / "vault/app.env/x.txt").exists(),
           str(r)[:140])

    # ---- 4. .git ------------------------------------------------------
    r = h.write(".git/config", "x")
    record("4 '.git' component refused",
           r.get("ok") is False and not (root / ".git").exists())
    r = h.write("sub/.git/x", "x")
    record("4 nested '.git' component refused",
           r.get("ok") is False and not (root / "sub/.git").exists())

    # ---- 5. RACE -------------------------------------------------------
    race_dir = root / "race"
    race_dir.mkdir()
    saved_dir = root / ".race-saved"
    stop = threading.Event()

    def swapper():
        while not stop.is_set():
            try:
                os.rename(race_dir, saved_dir)
            except OSError:
                pass
            try:
                os.symlink(str(outside), race_dir)
            except OSError:
                pass
            time.sleep(0.0005)
            try:
                os.unlink(race_dir)
            except OSError:
                pass
            try:
                os.rename(saved_dir, race_dir)
            except OSError:
                pass
            time.sleep(0.0005)

    t = threading.Thread(target=swapper, daemon=True)
    t.start()
    total, oks, fails, payloads = 60, 0, 0, set()
    try:
        for i in range(total):
            payload = f"payload-{i}\n"
            payloads.add(payload)
            r = h.write("race/f.txt", payload)
            if r.get("ok") is True:
                oks += 1
            elif r.get("ok") is False:
                fails += 1
    finally:
        stop.set()
        t.join(timeout=10)
    record("5 race: every write answered ok-or-refused",
           oks + fails == total, f"ok={oks} refused={fails} of {total}")
    record("5 race: zero bytes landed outside the root",
           outside_tree(h) == ["victim.txt"]
           and (outside / "victim.txt").read_text() == "ORIGINAL-OUTSIDE\n",
           f"outside now: {outside_tree(h)}")
    inroot = []
    for cand in (race_dir / "f.txt", saved_dir / "f.txt"):
        if cand.is_file() and not cand.is_symlink():
            inroot.append(cand.read_text())
    record("5 race: successful writes landed in-root with real payloads",
           len(inroot) >= 1 and all(c in payloads for c in inroot),
           f"in-root copies: {len(inroot)}")
    stray = [str(p) for p in h.base.rglob(".mcpgw-*")]
    record("5 race: no temp files leaked anywhere", stray == [],
           f"stray: {stray[:3]}")

    # ---- 6. final-component symlink -----------------------------------
    os.symlink(str(outside / "victim.txt"), root / "link.txt")
    r = h.write("link.txt", "PWNED\n")
    record("6 write via final symlink to outside refused; victim intact",
           r.get("ok") is False
           and (outside / "victim.txt").read_text() == "ORIGINAL-OUTSIDE\n",
           str(r)[:140])
    (root / "real.txt").write_text("REAL\n")
    os.symlink("real.txt", root / "alias.txt")
    r = h.edit("alias.txt", "REAL", "EDITED")
    record("6 edit through in-root final symlink still followed",
           r.get("ok") is True
           and (root / "real.txt").read_text() == "EDITED\n"
           and (root / "alias.txt").is_symlink(),
           str(r)[:140])
    r = h.write("alias.txt", "W2\n")
    record("6 write through in-root final symlink lands on the target",
           r.get("ok") is True
           and (root / "real.txt").read_text() == "W2\n",
           str(r)[:140])

    # ---- 7. exec cwd pinning -------------------------------------------
    r = h.exec("pwd -P", "a/b")
    record("7 exec cwd is the requested in-root dir",
           r.get("ok") is True
           and r.get("stdout", "").strip()
           == str((root / "a/b").resolve()),
           str(r)[:160])
    os.symlink("a/b", root / "cw")
    r = h.exec("pwd -P", "cw")
    record("7 exec cwd via in-root symlink resolves in-root",
           r.get("ok") is True
           and r.get("stdout", "").strip()
           == str((root / "a/b").resolve()),
           str(r)[:160])
    os.symlink(str(outside), root / "cwdlink")
    r = h.exec("echo PWN > cwdmarker.txt", "cwdlink")
    record("7 exec cwd escaping via symlink refused, never runs outside",
           r.get("ok") is False
           and not (outside / "cwdmarker.txt").exists(),
           str(r)[:140])

    # ---- 8. modes -------------------------------------------------------
    m = root / "m.txt"
    m.write_text("v1\n")
    os.chmod(m, 0o640)
    r = h.write("m.txt", "v2\n")
    record("8 overwrite preserves the existing file's mode",
           r.get("ok") is True
           and stat.S_IMODE(m.stat().st_mode) == 0o640
           and m.read_text() == "v2\n",
           str(r)[:120])
    r = h.write("fresh.txt", "new\n")
    record("8 new file gets mode 0644",
           r.get("ok") is True
           and stat.S_IMODE((root / "fresh.txt").stat().st_mode) == 0o644)

    # ---- 9. traversal parity --------------------------------------------
    r = h.write("../evil.txt", "x")
    record("9 leading '..' traversal refused",
           r.get("ok") is False and not (h.base / "evil.txt").exists())
    r = h.write("a/../../evil.txt", "x")
    record("9 embedded '..' traversal refused",
           r.get("ok") is False and not (h.base / "evil.txt").exists())
    r = h.op({"op": "write", "root": "nope", "subpath": "x.txt",
              "content_b64": base64.b64encode(b"x").decode()})
    record("9 unknown root refused", r.get("ok") is False)

    # ---- 10. legitimate in-root mid symlink ------------------------------
    (root / "realdir").mkdir()
    os.symlink("realdir", root / "mid")
    r = h.write("mid/deep/x.txt", "deep\n")
    record("10 in-root mid-path symlink followed (dirs created)",
           r.get("ok") is True
           and (root / "realdir/deep/x.txt").read_text() == "deep\n",
           str(r)[:140])

    # ---- 11. symlink loop --------------------------------------------------
    os.symlink("loop2", root / "loop1")
    os.symlink("loop1", root / "loop2")
    start = time.time()
    r = h.write("loop1/x.txt", "x")
    record("11 symlink loop refused promptly (bounded expansions)",
           r.get("ok") is False and time.time() - start < 20,
           str(r)[:140])


if __name__ == "__main__":
    sys.exit(main())
