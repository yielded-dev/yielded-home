"""Exercise the public commands with real local Git clones and no network."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WorkspaceTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.workspace = self.base / "yielded-home"
        self.source = self.base / "upstream"
        self.source.mkdir()
        self.env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
                        GIT_TERMINAL_PROMPT="0", GIT_ALLOW_PROTOCOL="file")
        shutil.copytree(ROOT / "scripts", self.workspace / "scripts")
        (self.workspace / "guide.md").touch()

        self.git(self.source, "init", "-b", "main")
        (self.source / "prepare.py").write_text("from pathlib import Path\nPath('installed').touch()\n")
        (self.source / "check.py").write_text(
            "from pathlib import Path\n"
            "if Path('fail-check').exists():\n"
            "    raise SystemExit(42)\n"
            "Path('checked').touch()\n"
        )
        self.git(self.source, "add", ".")
        self.git(self.source, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.org",
                 "commit", "-m", "Fixture")
        self.write_catalog(self.source.as_uri())

    def write_catalog(self, agent_remote):
        manifest = ['[profiles]', 'core = ["agent"]', 'all = ["agent", "auth"]']
        for name, remote in [("agent", agent_remote), ("auth", self.source.as_uri())]:
            manifest.extend([
                f"[repos.{name}]", f"remote = {json.dumps(remote)}", f'role = "{name}"',
                'guide = "guide.md"', 'tools = ["git", "python3"]',
                'setup = [["python3", "prepare.py"]]', 'checks = [["python3", "check.py"]]',
            ])
        (self.workspace / "repos.toml").write_text("\n".join(manifest))

    def git(self, path, *args):
        return subprocess.run(["git", "-C", str(path), *args], env=self.env, check=True,
                              capture_output=True, text=True).stdout.strip()

    def command(self, name, *args, expected=0):
        # Invoke from outside the home checkout to exercise path resolution.
        result = subprocess.run([str(self.workspace / "scripts" / name), *args], cwd=self.base,
                                env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def test_preview_then_setup_and_check_fresh_clones(self):
        plan = self.command("setup", "--profile", "all", "--dry-run")
        self.assertIn("git clone", plan.stdout)
        self.assertIn("python3 prepare.py", plan.stdout)
        self.assertIn("python3 check.py", self.command("check", "--dry-run", "agent").stdout)
        self.assertFalse((self.workspace / "repos").exists())

        self.command("setup")
        agent = self.workspace / "repos/agent"
        self.assertTrue((agent / "installed").exists())
        self.assertFalse((self.workspace / "repos/auth").exists())
        self.assertIn(self.git(agent, "rev-parse", "HEAD"), self.command("doctor").stdout)
        self.command("check", "agent")
        self.assertTrue((agent / "checked").exists())

    def test_bootstrap_preserves_dirty_linked_worktree_with_ssh_origin(self):
        self.command("bootstrap")
        clone = self.workspace / "repos/agent"
        worktree = self.base / "feature"
        self.git(clone, "worktree", "add", "-b", "work-in-progress", str(worktree))
        self.git(clone, "remote", "set-url", "origin", "git@github.com:yielded-dev/agent.git")
        self.write_catalog("https://github.com/yielded-dev/agent.git")
        (self.workspace / "repos.local.toml").write_text('[paths]\nagent = "../feature"\n')
        edited = worktree / "check.py"
        edited.write_text("local work\n")
        result = self.command("bootstrap", "agent")
        self.assertIn(str(worktree), result.stdout)
        self.assertIn("work-in-progress @", result.stdout)
        self.assertIn("(dirty)", result.stdout)
        self.assertEqual(edited.read_text(), "local work\n")
        self.assertEqual(self.git(worktree, "branch", "--show-current"), "work-in-progress")

    def test_refuses_wrong_repository_and_nested_directory_before_install(self):
        self.command("bootstrap")
        clone = self.workspace / "repos/agent"
        self.git(clone, "remote", "set-url", "origin", "file:///wrong-repo")
        self.assertIn("Unexpected origin", self.command("setup", expected=1).stderr)
        self.assertFalse((clone / "installed").exists())
        (clone / "nested").mkdir()
        (self.workspace / "repos.local.toml").write_text('[paths]\nagent = "repos/agent/nested"\n')
        self.assertIn("checkout root", self.command("setup", expected=1).stderr)

    def test_check_reports_failure_and_checks_the_next_repo(self):
        self.command("bootstrap", "--profile", "all")
        (self.workspace / "repos/agent/fail-check").touch()
        result = self.command("check", "agent", "auth", expected=1)
        self.assertIn("Failed: agent", result.stderr)
        self.assertTrue((self.workspace / "repos/auth/checked").exists())
