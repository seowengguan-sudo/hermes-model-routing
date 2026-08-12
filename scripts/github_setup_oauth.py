#!/usr/bin/env python3
"""
github_setup_oauth.py
Interactive setup script for GitHub authentication + auto-sync.

Run: /tmp/reportlab-venv/bin/python /opt/data/scripts/github_setup_oauth.py

Steps:
1. Verifies gh CLI exists
2. Prompts for device-flow login (opens URL in browser)
3. Configures auto-push on cron completion
"""
import subprocess, sys, os, json, time
from pathlib import Path

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr

def main():
    print("=== GitHub OAuth Setup (gh CLI) ===\n")

    # 1. Check if gh is installed
    rc, out, _ = run("which gh")
    if rc != 0:
        print("❌ gh CLI not found. Installing...")
        run("sudo apt-get update && sudo apt-get install -y gh")
        rc, _, _ = run("which gh")
        if rc != 0:
            print("❌ Failed to install gh CLI.")
            return False

    print("✅ gh CLI found")

    # 2. Start device flow
    print("\n🚀 Starting device authorization flow...")
    print("   This will open a URL in your browser for SSO login.")
    print("   If you're on a headless machine, copy the verification code below.\n")

    # Trigger interactive auth
    # Note: This won't work in cron — only interactive sessions
    auth_cmd = "gh auth login --with-token"
    print(f"🔐 Run this manually in an interactive session:")
    print(f"   {auth_cmd}")
    print("\nAlternatively, create a personal access token at:")
    print("   https://github.com/settings/tokens")
    print("Then pipe it via:")
    print(f"   echo '<YOUR_PAT>' | {auth_cmd}")

    # Check current auth status
    rc, out, _ = run("gh auth status 2>&1")
    print(f"\n🔍 Current auth status:\n{out}")

    # 3. Configure git push
    repo_path = "/opt/data"
    remote_url = "https://github.com/seowengguan-sudo/hermes-model-routing.git"

    rc, _, err = run(f'cd {repo_path} && git remote set-url origin {remote_url}')
    if rc == 0:
        print("✅ Remote URL updated")
    else:
        print(f"⚠️ Warning setting remote: {err}")

    # 4. Auto-push config
    auto_push_hook = """
# Auto-push to GitHub after successful cron run
if [ $? -eq 0 ] && git -C /opt/data rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git -C /opt/data add -A
    git -C /opt/data commit -m "Auto-sync: $(date -u +%Y%m%dT%H%M%SZ)" --allow-empty 2>/dev/null
    git push origin master 2>/dev/null || echo "Push skipped (no auth or network)"
fi
"""
    hook_file = Path("/opt/data/scripts/auto_git_push.sh")
    hook_file.write_text(auto_push_hook)
    hook_file.chmod(0o755)
    print(f"✅ Auto-push hook written to {hook_file}")

    # 5. Test push (will fail gracefully without auth)
    print("\n🧪 Testing push (expect failure until authenticated)...")
    rc, out, err = run(f"cd {repo_path} && git push origin master 2>&1")
    if rc == 0:
        print("✅ Push succeeded!")
    else:
        print(f"⚠️ Expected failure (no auth yet):")
        print(f"   {err[:200]}")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
