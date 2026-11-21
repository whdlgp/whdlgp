#!/usr/bin/env python3
"""Update the RECENT WORK section in the GitHub profile README."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from html import escape

USERNAME = "whdlgp"
README_PATH = "README.md"
START = "<!-- PROJECTS:START -->"
END = "<!-- PROJECTS:END -->"
MAX_PROJECTS = 6
PER_PAGE = 100
CARD_WIDTH = 855


def fetch_repositories() -> list[dict]:
    """Return up to MAX_PROJECTS recently pushed, non-fork public repositories."""
    selected: list[dict] = []
    page = 1

    while len(selected) < MAX_PROJECTS:
        query = urllib.parse.urlencode(
            {
                "type": "owner",
                "sort": "pushed",
                "direction": "desc",
                "per_page": PER_PAGE,
                "page": page,
            }
        )
        url = f"https://api.github.com/users/{USERNAME}/repos?{query}"
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "profile-readme-updater",
        }
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                repositories = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace").strip()
            raise RuntimeError(
                f"GitHub API returned HTTP {error.code}: {detail or error.reason}"
            ) from error
        except urllib.error.URLError as error:
            raise RuntimeError(f"Could not reach GitHub API: {error.reason}") from error

        if not isinstance(repositories, list):
            raise RuntimeError("GitHub API returned an unexpected response.")

        for repo in repositories:
            if repo.get("fork") or repo.get("archived") or repo.get("disabled"):
                continue
            if repo.get("name", "").casefold() == USERNAME.casefold():
                continue
            if not (repo.get("description") or "").strip():
                continue
            selected.append(repo)
            if len(selected) == MAX_PROJECTS:
                break

        if len(repositories) < PER_PAGE:
            break
        page += 1

    return selected


def render_card(repo: dict) -> str:
    name = escape(str(repo.get("name") or "Unnamed repository"))
    description = " ".join(str(repo.get("description") or "").split())
    if len(description) > 170:
        description = description[:167].rstrip() + "..."
    description = escape(description)
    url = escape(str(repo.get("html_url") or "https://github.com"), quote=True)
    language = escape(str(repo.get("language") or "Other"))
    stars = int(repo.get("stargazers_count") or 0)
    pushed_at = str(repo.get("pushed_at") or "")
    pushed_date = escape(pushed_at[:10]) if len(pushed_at) >= 10 else ""

    details = f"<code>{language}</code> &nbsp; Stars: {stars}"
    if pushed_date:
        details += f" &nbsp; Pushed: {pushed_date}"

    return (
        '<td width="50%" valign="top">'
        f'<strong><a href="{url}">{name}</a></strong><br><br>'
        f"{description}<br><br>"
        f"<small>{details}</small>"
        "</td>"
    )


def render_projects(repositories: list[dict]) -> str:
    if not repositories:
        return "<p>No recent public repositories found.</p>"

    rows: list[str] = []
    for index in range(0, min(len(repositories), MAX_PROJECTS), 2):
        left = render_card(repositories[index])
        right = (
            render_card(repositories[index + 1])
            if index + 1 < min(len(repositories), MAX_PROJECTS)
            else '<td width="50%"></td>'
        )
        rows.append(f"<tr>{left}{right}</tr>")

    return (
        f'<table width="{CARD_WIDTH}" border="1" cellpadding="12" cellspacing="0">'
        + "".join(rows)
        + "</table>"
    )


def update_readme() -> bool:
    with open(README_PATH, encoding="utf-8") as file:
        readme = file.read()

    if readme.count(START) != 1 or readme.count(END) != 1:
        raise RuntimeError(
            "README.md must contain exactly one PROJECTS:START and one PROJECTS:END marker."
        )

    before, remainder = readme.split(START, 1)
    _, after = remainder.split(END, 1)
    updated_section = render_projects(fetch_repositories())
    updated_readme = f"{before}{START}\n{updated_section}\n{END}{after}"

    if updated_readme == readme:
        return False

    with open(README_PATH, "w", encoding="utf-8", newline="\n") as file:
        file.write(updated_readme)
    return True


def main() -> None:
    if update_readme():
        print(f"README.md updated with up to {MAX_PROJECTS} recent repositories.")
    else:
        print("README.md is already up to date.")


if __name__ == "__main__":
    main()
