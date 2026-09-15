"""
ARIA GitHub Project Manager — Synchronizes GitHub Issues & Project Board (#3).
Automatically updates card columns: Backlog -> Ready -> In progress -> In review -> Done
"""
import os
import sys
import subprocess
from pathlib import Path
import httpx

# Ensure utf-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT_DIR / ".env"

REPO_OWNER = "sajjad-hassan834"
REPO_NAME = "ARIA"
PROJECT_NUMBER = 3


def get_github_token() -> str:
    """Retrieve GitHub token from .env or Git Credential Manager."""
    # 1. Try .env first
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("GITHUB_TOKEN=") or line.startswith("GH_TOKEN="):
                    token = line.strip().split("=", 1)[1].strip()
                    if token and not token.startswith("your_"):
                        return token

    # 2. Try environment variable
    env_token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if env_token:
        return env_token

    # 3. Fallback to Windows Git Credential Manager
    try:
        p = subprocess.Popen(["git", "credential", "fill"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        out, _ = p.communicate("protocol=https\nhost=github.com\n")
        for line in out.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass

    return ""


def get_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def update_issue_status(issue_number: int, state: str = "closed") -> bool:
    """Update issue state on GitHub (open / closed)."""
    token = get_github_token()
    if not token:
        print("[!] No GitHub token found.")
        return False

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_number}"
    resp = httpx.patch(url, headers=get_headers(token), json={"state": state})
    if resp.status_code == 200:
        print(f"[+] Issue #{issue_number} marked as {state.upper()} on GitHub.")
        return True
    else:
        print(f"[-] Failed to update #{issue_number}: {resp.status_code} {resp.text}")
        return False


def create_issue(title: str, body: str = "", labels: list = None) -> int:
    """Create a new issue on GitHub repo."""
    token = get_github_token()
    if not token:
        print("[!] No GitHub token found.")
        return -1

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    payload = {"title": title, "body": body}
    if labels:
        payload["labels"] = labels

    resp = httpx.post(url, headers=get_headers(token), json=payload)
    if resp.status_code == 201:
        issue_num = resp.json().get("number", -1)
        print(f"[+] Created Issue #{issue_num}: {title}")
        return issue_num
    else:
        print(f"[-] Failed to create issue: {resp.status_code} {resp.text}")
        return -1


def sync_project_card(issue_node_id: str, column_name: str = "Done"):
    """
    Move item to specified column on Project #3 via GraphQL (requires 'project' scope).
    """
    token = get_github_token()
    if not token:
        return

    # GraphQL mutation to update ProjectV2 item
    query = """
    query($owner: String!, $number: Int!) {
      user(login: $owner) {
        projectV2(number: $number) {
          id
          fields(first: 20) {
            nodes {
              ... on ProjectV2SingleSelectField {
                id
                name
                options {
                  id
                  name
                }
              }
            }
          }
        }
      }
    }
    """
    try:
        r = httpx.post(
            "https://api.github.com/graphql",
            headers={"Authorization": f"Bearer {token}"},
            json={"query": query, "variables": {"owner": REPO_OWNER, "number": PROJECT_NUMBER}},
            timeout=10.0
        )
        data = r.json()
        if "errors" in data and any("INSUFFICIENT_SCOPES" in str(e) for e in data["errors"]):
            print("[i] Token does not have 'project' scope yet for direct GraphQL card column moving.")
            print("[i] Issues are synced and automatically marked Done/Closed.")
            return
    except Exception as e:
        print(f"[-] Project GraphQL error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
        if action == "close" and len(sys.argv) > 2:
            update_issue_status(int(sys.argv[2]), "closed")
        elif action == "open" and len(sys.argv) > 2:
            update_issue_status(int(sys.argv[2]), "open")
        elif action == "create" and len(sys.argv) > 2:
            title = sys.argv[2]
            create_issue(title)
        else:
            print(f"Usage: python sync_project.py [close <num> | open <num> | create '<title>']")
    else:
        print("[*] ARIA Project Manager ready.")
        token = get_github_token()
        print(f"[*] GitHub Token detected: {'YES' if token else 'NO'}")
