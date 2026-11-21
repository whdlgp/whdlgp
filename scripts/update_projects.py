#!/usr/bin/env python3
"""Refresh the public repository cards in the profile README."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html import escape

USERNAME = "whdlgp"
README_PATH = "README.md"
START = "<!-- PROJECTS:START -->"
END = "<!-- PROJECTS:END -->"


def fetch_repositories() -> list[dict]:
    url = (
        f"https://api.github.com/users/{urllib.parse.quote(USERNAME)}/repos"
        "?type=public&sort=updated&direction=desc&per_page=100"
    )
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
            "User-Agent": "profile-readme-updater",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        repositories = json.loads(response.read().decode("utf-8"))

    return [
        repo for repo in repositories
        if not repo["fork"] and not repo["archived"] and repo.get("description")
    ]


def render_projects(repositories: list[dict]) -> str:
    # Updated public repositories with descriptions; no manual project ranking.
    selected = repositories[:8]
    if not selected:
        return "_No public repositories found._"

    rows = []
    for repo in selected:
        name = escape(repo["name"])
        description = escape(repo["description"])
        language = escape(repo.get("language") or "Other")
        url = escape(repo["html_url"], quote=True)
        stars = repo.get("stargazers_count", 0)
        updated = repo.get("pushed_at") or repo.get("updated_at") or ""
        date = updated[:10] if updated else ""
        rows.append(
            "<tr>"
            f'<td width="30%"><a href="{url}"><strong>{name}</strong></a></td>'
            f"<td>{description}</td>"
            f'<td align="center"><code>{language}</code></td>'
            f'<td align="right">{stars} ★</td>'
            "</tr>"
        )

    return (
        '<table><thead><tr><th>Repository</th><th>Description</th>'
        '<th>Language</th><th>Stars</th></tr></thead><tbody>'
        + "".join(rows)
        + "</tbody></table>"
    )


def main() -> None:
    with open(README_PATH, encoding="utf-8") as file:
        readme = file.read()

    if START not in readme or END not in readme:
        raise RuntimeError("Project section markers are missing from README.md")

    repositories = fetch_repositories()
    section = render_projects(repositories)
    before, remainder = readme.split(START, 1)
    _, after = remainder.split(END, 1)
    updated = f"{before}{START}\n{section}\n{END}{after}"

    if updated != readme:
        with open(README_PATH, "w", encoding="utf-8", newline="\n") as file:
            file.write(updated)


if __name__ == "__main__":
    main()
