#!/usr/bin/env python3
"""Clone, prepare, inspect and check the repositories in a Yielded workspace."""

import argparse
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

if sys.version_info < (3, 11):
    sys.exit("yielded-home requires Python 3.11 or newer")

import tomllib

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE = "core"


def string_list(value):
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def load_catalog(root):
    with (root / "repos.toml").open("rb") as stream:
        catalog = tomllib.load(stream)
    repos, profiles = catalog.get("repos"), catalog.get("profiles")
    if not isinstance(repos, dict) or not repos or not isinstance(profiles, dict):
        raise ValueError("repos.toml needs repos and profiles tables")
    for name, repo in repos.items():
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name) or not isinstance(repo, dict):
            raise ValueError(f"Invalid repository entry {name!r}")
        for key in ("remote", "role", "guide"):
            if not isinstance(repo.get(key), str) or not repo[key].strip():
                raise ValueError(f"{name} needs a {key}")
        guide = (root / repo["guide"]).resolve()
        if not guide.is_relative_to(root) or not guide.is_file():
            raise ValueError(f"{name} needs a guide inside yielded-home")
        if not string_list(repo.get("tools")):
            raise ValueError(f"{name}.tools must list the required executables")
        for key in ("setup", "checks"):
            commands = repo.get(key)
            if not isinstance(commands, list) or not commands or not all(map(string_list, commands)):
                raise ValueError(f"{name}.{key} must contain nonempty command argument lists")
    for profile, names in profiles.items():
        if not string_list(names) or len(set(names)) != len(names) or set(names) - repos.keys():
            raise ValueError(f"Invalid repository selection in profile {profile!r}")
    if DEFAULT_PROFILE not in profiles or set(profiles.get("all", [])) != repos.keys():
        raise ValueError(f"Define the default {DEFAULT_PROFILE} profile and include every repo in all")
    return repos, profiles


def checkout_paths(root, repos):
    overrides = {}
    local_file = root / "repos.local.toml"
    if local_file.exists():
        with local_file.open("rb") as stream:
            local = tomllib.load(stream)
        if set(local) != {"paths"} or not isinstance(local["paths"], dict):
            raise ValueError("repos.local.toml needs a single [paths] table")
        overrides = local["paths"]
        for name, path in overrides.items():
            if name not in repos or not isinstance(path, str) or not path.strip():
                raise ValueError(f"Invalid checkout override for {name!r}")

    paths = {}
    for name in repos:
        location = Path(overrides.get(name, f"repos/{name}")).expanduser()
        path = (root / location).resolve()
        if path == root or path in root.parents:
            raise ValueError(f"{name} points at yielded-home or one of its parents")
        if any(path == other or other in path.parents or path in other.parents for other in paths.values()):
            raise ValueError(f"{name} overlaps another component checkout at {path}")
        paths[name] = path
    return paths


def remote_id(url):
    # GitHub's HTTPS, SCP-style SSH and ssh:// URLs identify the same checkout.
    for prefix in ("git@github.com:", "ssh://git@github.com/", "https://github.com/"):
        if url.startswith(prefix):
            return "github.com/" + url[len(prefix):].rstrip("/").removesuffix(".git").lower()
    return url.rstrip("/")


def git(path, *args):
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(path), *args],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def inspect_checkout(path, expected_remote):
    try:
        top = Path(git(path, "rev-parse", "--show-toplevel")).resolve()
        if top != path:
            raise ValueError(f"{path} is inside {top}. Point to a checkout root.")
        origin = git(path, "config", "--get", "remote.origin.url")
    except subprocess.CalledProcessError as error:
        raise ValueError(f"Expected a Git checkout with an origin at {path}") from error
    if remote_id(origin) != remote_id(expected_remote):
        raise ValueError(f"Unexpected origin at {path}. Expected {expected_remote}")
    branch = git(path, "branch", "--show-current") or "detached HEAD"
    commit = git(path, "rev-parse", "--verify", "HEAD")
    state = "dirty" if git(path, "status", "--porcelain") else "clean"
    print(f"  {branch} @ {commit} ({state})", flush=True)


def run(command, cwd, dry_run):
    print(f"  $ {shlex.join(command)}", flush=True)
    if not dry_run:
        subprocess.run(command, cwd=cwd, check=True)


def run_component(name, repo, path, action, dry_run):
    print(f"{name}  {path}", flush=True)
    if path.exists():
        inspect_checkout(path, repo["remote"])
    elif action in ("bootstrap", "setup"):
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--", repo["remote"], str(path)], ROOT, dry_run)
        if not dry_run:
            inspect_checkout(path, repo["remote"])
    elif not dry_run:
        raise ValueError(f"Missing checkout at {path}. Run ./scripts/bootstrap {name}")

    if action == "bootstrap":
        return
    if not dry_run:
        missing = [tool for tool in repo["tools"] if shutil.which(tool) is None]
        if missing:
            raise ValueError(f"Missing tools: {', '.join(missing)}. See {repo['guide']}")
    if action == "doctor":
        print(f"  {repo['role']}\n  Guide: {repo['guide']}", flush=True)
        return
    for command in repo["setup" if action == "setup" else "checks"]:
        run(command, path, dry_run)
    if not dry_run:
        print(f"  {action} passed", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["setup", "bootstrap", "doctor", "check"])
    parser.add_argument("repos", nargs="*", metavar="REPO", help="component repository names")
    parser.add_argument("--profile", help=f"named selection in repos.toml (default: {DEFAULT_PROFILE})")
    parser.add_argument("--dry-run", action="store_true", help="show planned commands without executing them")
    args = parser.parse_intermixed_args()
    if args.repos and args.profile:
        parser.error("choose a profile or explicit repository names")
    if args.dry_run and args.action == "doctor":
        parser.error("doctor already inspects checkouts without running setup or checks")
    try:
        repos, profiles = load_catalog(ROOT)
        paths = checkout_paths(ROOT, repos)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Workspace error: {error}\n")
    profile = args.profile or DEFAULT_PROFILE
    if profile not in profiles:
        parser.error(f"unknown profile {profile!r}. Choose from {', '.join(profiles)}")
    selected = list(dict.fromkeys(args.repos or profiles[profile]))
    unknown = [name for name in selected if name not in repos]
    if unknown:
        parser.error(f"unknown repositories: {', '.join(unknown)}")

    if args.dry_run:
        print("Dry run", flush=True)
    failed = []
    for name in selected:
        try:
            run_component(name, repos[name], paths[name], args.action, args.dry_run)
        except (OSError, ValueError, subprocess.CalledProcessError) as error:
            print(f"{name}: {error}", file=sys.stderr, flush=True)
            failed.append(name)
    if failed:
        print(f"Failed: {', '.join(failed)}", file=sys.stderr)
    return int(bool(failed))


if __name__ == "__main__":
    sys.exit(main())
