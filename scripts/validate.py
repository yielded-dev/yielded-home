#!/usr/bin/env python3
"""Check the portable catalog, local documentation links, skills and entry points."""

import json
import os
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

sys.dont_write_bytecode = True
from home import ROOT, load_catalog


def validate():
    repos, profiles = load_catalog(ROOT)
    errors = []
    skills = ROOT / ".agents/skills"
    documents = sorted([*ROOT.glob("*.md"), *(ROOT / "docs").rglob("*.md"), *skills.rglob("*.md")])
    for document in documents:
        for target in re.findall(r"\[[^\]\n]*\]\(([^)\s]+)\)", document.read_text()):
            url = urlsplit(target)
            if url.scheme or url.netloc or not url.path:
                continue
            linked = (document.parent / unquote(url.path)).resolve()
            if not linked.is_relative_to(ROOT) or not linked.exists():
                errors.append(f"{document.relative_to(ROOT)}: broken link to {target}")

    skill_dirs = sorted(path for path in skills.iterdir() if path.is_dir())
    for path in skill_dirs:
        receipt = json.loads((path / ".dev-kit-origin.json").read_text())
        if receipt["name"] != path.name or not (path / "SKILL.md").is_file():
            errors.append(f"Check the skill and origin receipt in {path.relative_to(ROOT)}")
    if (ROOT / ".claude/skills").resolve() != skills or (ROOT / "CLAUDE.md").read_text().strip() != "@AGENTS.md":
        errors.append("Claude entry points must resolve to the shared instructions and skills")

    for name in ("bootstrap", "setup", "doctor", "check"):
        script = ROOT / "scripts" / name
        if not os.access(script, os.X_OK):
            errors.append(f"scripts/{name} must be executable")
        subprocess.run(["sh", "-n", str(script)], check=True)
    if errors:
        raise ValueError("\n".join(errors))
    print(f"Validated {len(repos)} repos, {len(profiles)} profiles, {len(documents)} documents and {len(skill_dirs)} skills.")


if __name__ == "__main__":
    try:
        validate()
    except (KeyError, OSError, ValueError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
