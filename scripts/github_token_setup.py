#!/usr/bin/env python3
"""
github_token_setup.py
One-time GitHub PAT configuration for push operations.

Run: python3 github_token_setup.py

Then enter your GitHub Personal Access Token when prompted.
"""
import os, sys, getpass

def main():
    print("=== GitHub Token Setup ===\n")
    print("To push commits to seowengguan-sudo/hermes-model-routing, you need a GitHub PAT.")
    print("Create one at: https://github.com/settings/tokens")
    print("Recommended scopes: repo, workflow, read:org\n")

    token = getpass.getpass("Enter your GitHub PAT: ").strip()
    if not token:
        print("❌ No token provided.")
        return False

    # Write .git-credentials file
    git_dir = "/opt/data"
    cred_file = os.path.expanduser("~/.git-credentials")

    creds = []
    existing_lines = []
    if os.path.exists(cred_file):
        with open(cred_file, "r") as f:
            existing_lines = [line.strip() for line in f.readlines() if line.strip()]

    # Remove old GitHub entries
    filtered = [line for line in existing_lines if "github.com" not in line]

    # Add new credential
    new_line = f"https://x-access-token:{token}@github.com\n"
    filtered.append(new_line)

    with open(cred_file, "w") as f:
        f.write("\n".join(filtered) + "\n")

    # Configure git to use the credential helper
    import subprocess
    subprocess.run(["git", "-C", git_dir, "config", "credential.helper", "store"], check=False)
    subprocess.run(["git", "-C", git_dir, "config", "--global", "credential.helper", "store"], check=False)

    print(f"\n✅ Credentials saved to {cred_file}")
    print("✅ Git configured with 'store' credential helper")

    # Test push
    print("\n🧪 Testing push...")
    os.chdir(git_dir)
    os.system("git add -A")
    commit_msg = "Auto-sync: initial push after PAT setup"
    ret = os.system(f'git commit -m "{commit_msg}" 2>&1 || true')
    push_result = os.system("git push origin master")

    if push_result == 0:
        print("\n✅ Push successful! Your work is now synced to GitHub.")
        print("📍 Next steps:")
        print("   • All future crons will auto-commit/push via auto_git_push.sh")
        print("   • Or run 'python3 /opt/data/scripts/github_token_setup.py' anytime to update token")
    else:
        print("\n⚠️ Push failed — check network/firewall/WAF restrictions")
        print("💡 If behind corporate firewall, try:")
        print("   git config --global http.proxy http://proxy:port")

    return True

if __name__ == "__main__":
    main()
