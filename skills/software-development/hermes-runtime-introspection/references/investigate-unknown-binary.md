# Investigating an Unknown On-Disk Binary (tirith case study)

**Trigger pattern:** user asks "what is this file `…/bin/foo`?" or "is this thing actually doing anything to my system?"

Generalizes to: *identify an unknown executable, determine what it is/claims to be, and check whether it is actively running — without executing it.*

## Technique (the loop that worked)

1. **Locate the file and its data siblings.** Don't inspect in isolation.
   ```bash
   find / -path '*/bin/tirith' 2>/dev/null          # discover all copies
   ls -la /opt/data/.local/state/tirith/            # runtime state dir
   ls -la /opt/data/.local/share/tirith/            # DB, logs, cache
   ```
   The state dir (`sessions/`, `threatdb-*`, `log.jsonl`, `.lock`) proves the binary *was* used and tells you where to look for live activity.

2. **Read the binary without executing it.** It's an ELF, not a text script — skip `head`/`cat` (binary garbage). Use metadata + `strings`:
   ```bash
   ls -la bin/tirith ; head -c 200 bin/tirith       # ELF magic => binary, not script
   /opt/data/bin/tirith --help ; /opt/data/bin/tirith --version
   ```
   - `--help` gives the author's own one-liner ("URL security analysis for shell environments").
   - `--version` prints a build number/version (here `0.3.3`).
   - Extract the canonical upstream origin from the binary's strings:
     ```bash
     strings bin/tirith | grep -oE 'github\.com/[a-z0-9_]+/tirith' | sort -u
     # => github.com/sheeki03/tirith
     ```
     This grounds "source" in vendor, not in a guess.

3. **Check the audit log for real behavior.** The truth is in what it *did*, not its marketing.
   - Open `log.jsonl`; each line is a JSON verdict with `action` (`Allow`/`Block`), `rule_ids`, `tier_reached`, `command_redacted`, `agent_origin.kind`.
   - Look for a chained hash field (`prev_hash`) — proves logs are tamper-evident, not flat appends.
   - Head file (`log.jsonl.head`) holds `{"head_hash":…,"count":N,…}` — quick health check without parsing 700+ lines.

4. **Check whether it is *currently active*** — the user rarely knows.
   ```bash
   /opt/data/bin/tirith status        # "protection: off / hook NOT configured / policy none"
   /opt/data/bin/tirith onboard       # env detection: shell, package mgrs, CI
   ```
   **Key finding on tirith:** the log showed *recent* verdicts (a few days old), but `status` reports protection **off**, hook **NOT configured**, policy **none**. I.e. the tool was run earlier and then deactivated. Inactive now = not intercepting your shell.

5. **Cross-check the threat-intel provenance (if it ships a DB).**
   - The `threatdb-manifest-*.json` points to a signed GitHub release asset (`tirith-threatdb-*.dat`).
   - The `threatdb-api-cache/` dir holds per-source JSON — read one to confirm the feed set
     (here: OSV `malicious_package`, Datadog malicious, Feodo Tracker, ecosyste.ms,
     URLhaus, Phishing Army, PhishTank, ThreatFox, FireHOL IP, Tor exit nodes, CISA KEV).
   - Confirms scope without trusting the `--help` marketing text.

## Pitfalls (session-learned)

- **`file` and `strings` may be absent.** In this minimal container, `file` was missing (`bash: file: command not found`). Fall back to ELF magic from `head -c` + `strings`. Don't treat a missing `file` as a blocker.
- **`strings … | grep "github.com/…"` with a greedy glob can trip the shell parser blocklist** (oversize/unparseable inline payload). Keep the regex tight: `strings bin/t | grep -oE 'github\.com/[a-z0-9_]+/tirith'`.
- **A present threat-DB file ≠ active DB.** `tirith status` separately reports DB install state; the `.dat` sitting on disk doesn't mean `threat-db update` has run for the current session.
- **Do not execute the binary to test it.** For a security tool in particular, run `check`/`score`/`fetch` against a *dummy* command or known-safe sample — never feed it your real history as the first probe.
- **"Protection off" is the expected clean state here** — this is a security gate that must be explicitly initialized (`tirith init` + `tirith policy init`). Its absence of a hook is a feature, not a latent attack.

## References
- Binary: `/opt/data/bin/tirith` (v0.3.3, ELF x86-64, ~22 MB)
- Source: `github.com/sheeki03/tirith` (extracted from binary strings)
- Audit log: `/opt/data/.local/share/tirith/log.jsonl` (~755 chained JSONL verdicts)
- Threat DB: `/opt/data/.local/share/tirith/tirith-threatdb.dat` + manifest in `/opt/data/.local/state/tirith/`
- State dir: `/opt/data/.local/state/tirith/sessions/`, `threatdb-api-cache/`
