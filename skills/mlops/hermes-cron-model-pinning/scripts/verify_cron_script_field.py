#!/usr/bin/env python3
"""Verify Hermes cron jobs have no broken `script` field.

Replicates the runner gate from /opt/hermes/cron/scheduler.py
(`script_path = job.get("script"); if script_path:`) and flags any job whose script
is truthy but does not resolve to a real file under HERMES_HOME/scripts/. A broken
script emits a 'Script not found' / 'Script Error' block every tick.

Usage:  python3 verify_cron_script_field.py [jobs.json] [HERMES_HOME]
Exit 0 = clean, 1 = problems found.
"""
import json, os, sys
from pathlib import Path


def main():
    home = Path(os.environ.get("HERMES_HOME", "/opt/data"))
    jobs_path = Path(sys.argv[1]) if len(sys.argv) > 1 else home / "cron" / "jobs.json"
    home = Path(sys.argv[2]) if len(sys.argv) > 2 else home
    scripts_dir = home / "scripts"
    try:
        data = json.loads(jobs_path.read_text())
    except Exception as e:
        print(f"FAIL: cannot read {jobs_path}: {e}")
        return 1

    problems = []
    for job in data.get("jobs", []):
        name = job.get("name", "?")
        script = job.get("script") or ""
        if script:
            raw = Path(script).expanduser()
            path = raw if raw.is_absolute() else (scripts_dir / raw).resolve()
            exists = path.exists() and path.is_file()
            if not exists:
                problems.append(
                    f"{name}: script {script!r} -> not a file ({path}); "
                    f"would emit 'Script not found' every tick"
                )
            else:
                print(f"[{name}] script={script!r} -> OK (runs before agent)")
        else:
            print(f"[{name}] script='' -> no pre-run script; agent runs directly")
        if job.get("no_agent") and script:
            print(f"  note: {name} is no_agent=True with a script -> script IS the job; "
                  f"a failure means no delivery")

    if problems:
        print("\nPROBLEMS:")
        for p in problems:
            print("  -", p)
        print("\nFix: set script to '' (hermes cron edit <id> --script '' "
              "or edit jobs.json directly).")
        return 1
    print("\nPASS: no broken script fields.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
