/* Setuid launcher for the MCP gateway root helper (Phase 5).
 *
 * The Lampy distro ships no sudo, so the gateway's one privileged path
 * is this binary: installed root:root, mode 4755. It refuses every
 * caller except the mcpgw user (uid 1000, the gateway's own account)
 * and execs the root-owned Python helper with a minimal environment.
 * The helper file is root-owned and not writable by mcpgw, so the code
 * that runs with an effective uid of 0 cannot be modified by the
 * account that invokes it. All operation policy (roots, denylist,
 * output caps) lives in the helper, never here.
 */
#include <stdio.h>
#include <unistd.h>

#define MCPGW_UID 1000
#define HELPER "/usr/local/sbin/mcpgw-root-helper.py"

int main(void) {
    if (getuid() != (uid_t)MCPGW_UID) {
        fprintf(stderr, "mcpgw-root-helper: caller is not mcpgw\n");
        return 1;
    }
    char *const argv[] = {"python3", HELPER, (char *)NULL};
    char *const envp[] = {
        "PATH=/usr/local/bin:/usr/bin:/bin",
        "LANG=C.UTF-8",
        (char *)NULL
    };
    execve("/usr/bin/python3", argv, envp);
    perror("mcpgw-root-helper: execve");
    return 1;
}
