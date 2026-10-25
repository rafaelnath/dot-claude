"""Tests for git-guard.py. Run: python3 -m unittest hooks/test_git_guard.py"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "git-guard.py")
HEREDOC = "git commit -m \"$(cat <<'EOF'\n{msg}\n\nSome body text.\nEOF\n)\""


def make_repo(branch):
    path = tempfile.mkdtemp()
    subprocess.run(["git", "init", "-q", "-b", branch, path], check=True)
    return path


def run(command, cwd, tool="Bash"):
    payload = json.dumps({"tool_name": tool, "tool_input": {"command": command}, "cwd": cwd})
    p = subprocess.run([sys.executable, SCRIPT], input=payload, capture_output=True, text=True)
    return p.returncode, p.stderr


class GitGuardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = make_repo("fix/RBM-17-null-sku")
        cls.main = make_repo("main")

    def assertAllowed(self, command, cwd=None):
        code, err = run(command, cwd or self.work)
        self.assertEqual(code, 0, f"expected allowed: {command!r}\n{err}")

    def assertBlocked(self, command, cwd=None, contains=""):
        code, err = run(command, cwd or self.work)
        self.assertEqual(code, 2, f"expected blocked: {command!r}")
        self.assertIn(contains, err)

    # 1. merge
    def test_gh_pr_merge_blocked(self):
        self.assertBlocked("gh pr merge 42 --squash", contains="merging PRs")
        self.assertBlocked("git status && gh pr merge", contains="merging PRs")

    def test_other_gh_allowed(self):
        self.assertAllowed("gh pr create --title x --body y")
        self.assertAllowed("gh pr view 42")

    # 2. force push
    def test_force_push_blocked(self):
        for cmd in ["git push --force", "git push origin main --force", "git push -f",
                    "git push -uf origin x", "git push --force-with-lease",
                    "git push --force-with-lease=main", "git push origin +main",
                    "bash -c 'git push -f'"]:
            self.assertBlocked(cmd, contains="force-push")

    def test_normal_push_allowed(self):
        self.assertAllowed("git push -u origin fix/RBM-17-null-sku")
        self.assertAllowed("git push --follow-tags")

    # 3. branch
    def test_commit_on_main_blocked(self):
        self.assertBlocked('git commit -m "fix(receipt): handle null sku"', cwd=self.main, contains="'main'")

    def test_commit_with_dash_C_checks_target_repo(self):
        self.assertBlocked(f'git -C {self.main} commit -m "fix(receipt): handle null sku"', cwd=self.work,
                           contains="'main'")

    def test_commit_outside_repo_blocked(self):
        self.assertBlocked('git commit -m "fix(receipt): handle null sku"', cwd=tempfile.mkdtemp(),
                           contains="no current branch")

    # 4. amend
    def test_amend_blocked(self):
        self.assertBlocked("git commit --amend --no-edit", contains="amending")
        self.assertBlocked('git commit --amend -m "fix(receipt): handle null sku"', contains="amending")

    # 5. message
    def test_valid_messages_allowed(self):
        for msg in ["fix(RBM-17): handle null sku in lookup", "feat(receipt)!: drop legacy numbering",
                    "chore(deps): bump spring boot"]:
            self.assertAllowed(f'git commit -m "{msg}"')
        self.assertAllowed('git add -A && git commit -am "refactor(journal): extract shared create logic"')
        self.assertAllowed('git commit --message="docs(readme): describe setup"')
        self.assertAllowed(HEREDOC.format(msg="fix(RBM-17): handle null sku in lookup"))

    def test_invalid_messages_blocked(self):
        for msg in ["fixed the receipt bug", "fix: handle null sku", "Fix(receipt): handle null sku",
                    "fix(receipt): Handle null sku", "wip(receipt): stuff", "fix(receipt) handle null sku"]:
            self.assertBlocked(f'git commit -m "{msg}"', contains="subject must match")
        self.assertBlocked(HEREDOC.format(msg="Fixed the receipt bug"), contains="subject must match")

    def test_long_subject_blocked(self):
        msg = "fix(receipt): " + "a" * 60
        self.assertBlocked(f'git commit -m "{msg}"', contains="limit is 72")

    def test_unreadable_message_blocked(self):
        for cmd in ["git commit", "git commit -F msg.txt", "git commit -C HEAD", "git commit --fixup HEAD",
                    "git commit -F - <<'EOF'\nfix(x): y\nEOF"]:
            self.assertBlocked(cmd, contains="inline with -m")

    # unrelated commands
    def test_unrelated_commands_allowed(self):
        for cmd in ["ls -la", "git status", "git log --oneline -5", "git checkout -b fix/x",
                    "echo 'git push --force' > notes.txt"]:
            self.assertAllowed(cmd)

    def test_non_bash_tool_ignored(self):
        code, _ = run("git push --force", self.work, tool="Read")
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
