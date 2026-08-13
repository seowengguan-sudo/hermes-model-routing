#!/usr/bin/env python3
"""
enforce_pins.py — Ensure every cron job is pinned to tencent/hy3:free (Nous provider).
Runs alongside catchup.py on every restart. Updates drift-prone jobs automatically.
"""
import json, os, subprocess, shutil

JOBS_FILE = "/opt/data/cron/jobs.json"
TARGET_MODEL = "tencent/hy3:free"
TARGET_PROVIDER = "nous"

def enforce():
    # Backup before mutating
    backup_path = JOBS_FILE + ".bak"
    if not os.path.exists(backup_path):
        shutil.copy2(JOBS_FILE, backup_path)

    with open(JOBS_FILE) as f:
        data = json.load(f)

    updated = False
    for job in data.get("jobs", []):
        current_model = job.get("model")
        current_provider = job.get("provider")

        if current_model != TARGET_MODEL or current_provider != TARGET_PROVIDER:
            print(f"[enforce_pins] Updating {job['name']}: {current_model} -> {TARGET_MODEL}")
            # Use hermes CLI to update safely
            cmd = [
                "/opt/hermes/bin/hermes", "cron", "edit",
                job["id"],
                "--model", TARGET_MODEL,
                "--provider", TARGET_PROVIDER
            ]
            subprocess.run(cmd, capture_output=True, text=True)
            job["model"] = TARGET_MODEL
            job["provider"] = TARGET_PROVIDER
            updated = True

    if updated:
        with open(JOBS_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print("[enforce_pins] All jobs re-pinned successfully.")
    else:
        print("[enforce_pins] All jobs already correctly pinned.")

    return updated

if __name__ == "__main__":
    enforce()
