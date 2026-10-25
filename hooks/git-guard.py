#!/usr/bin/env python3
"""Claude Code PreToolUse hook (Bash) enforcing the coding workflow's git guardrails.

Blocks:
  1. gh pr merge                      (the user merges PRs)
  2. force pushes                     (--force, -f, --force-with-lease, +refspec)
  3. commits outside workflow branches (<type>/<slug>)
  4. git commit --amend
  5. commit messages that aren't Conventional Commits: <type>(<scope>): <summary>

Reads the hook JSON on stdin. Exit 2 blocks the call and shows stderr to Claude.
"""
import json
import os
import re
import shlex
import subprocess
import sys

TYPES = "feat|fix|refactor|test|docs|chore|perf|build|ci|style|revert"
BRANCH_RE = re.compile(rf"^({TYPES})/[^/\s].*$")
SUBJECT_RE = re.compile(rf"^({TYPES})\([^()\s][^()]*\)!?: [a-z]")
MAX_SUBJECT = 72

SEPARATORS = {";", "&", "&&", "|", "||", "\n", "(", ")"}
SHELLS = {"bash", "sh", "zsh"}
# git global options that take a separate value
GIT_OPTS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}


class Blocked(Exception):
    pass


def tokenize(command):
    lex = shlex.shlex(command, posix=True, punctuation_chars=";&|()<>\n")
    lex.whitespace = " \t\r"
    lex.whitespace_split = True
    return list(lex)


def segments(tokens):
    seg = []
    for tok in tokens:
        if tok in SEPARATORS or (tok and set(tok) <= set(";&|\n")):
            if seg:
                yield seg
            seg = []
        else:
            seg.append(tok)
    if seg:
        yield seg


def strip_env(seg):
    i = 0
    while i < len(seg) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", seg[i]):
        i += 1
    return seg[i:]


def heredoc_body(value):
    """Resolve Claude Code's usual -m "$(cat <<'EOF' ... EOF)" form."""
    m = re.match(r"^\$\(cat <<-?\s*['\"]?(\w+)['\"]?\s*\n(.*?)\n\s*\1\s*\n?\s*\)$", value, re.S)
    return m.group(2) if m else value


def check_command(command, cwd):
    try:
        tokens = tokenize(command)
    except ValueError:
        return  # unbalanced quotes: the shell will reject it anyway
    for seg in segments(tokens):
        seg = strip_env(seg)
        if not seg:
            continue
        prog = os.path.basename(seg[0])
        if prog in SHELLS and len(seg) >= 3 and seg[1] == "-c":
            check_command(seg[2], cwd)
        elif prog == "git":
            check_git(seg[1:], cwd)
        elif prog == "gh":
            check_gh(seg[1:])


def check_gh(args):
    positional = [a for a in args if not a.startswith("-")]
    if positional[:2] == ["pr", "merge"]:
        raise Blocked("merging PRs is not allowed; the user reviews and merges.")


def check_git(args, cwd):
    i = 0
    while i < len(args) and args[i].startswith("-"):
        opt = args[i]
        if opt in GIT_OPTS_WITH_VALUE:
            if opt == "-C" and i + 1 < len(args):
                cwd = os.path.join(cwd, os.path.expanduser(args[i + 1]))
            i += 2
        else:
            i += 1
    if i >= len(args):
        return
    sub, rest = args[i], args[i + 1:]
    if sub == "push":
        check_push(rest)
    elif sub == "commit":
        check_commit(rest, cwd)


def check_push(args):
    for a in args:
        if a in ("--force", "--force-with-lease", "--force-if-includes") or a.startswith("--force-with-lease="):
            raise Blocked("force-pushing is not allowed.")
        if re.match(r"^-[a-zA-Z]*f[a-zA-Z]*$", a):
            raise Blocked("force-pushing is not allowed.")
        if a.startswith("+"):
            raise Blocked("force-pushing via a +refspec is not allowed.")


def check_commit(args, cwd):
    messages = []
    i = 0
    while i < len(args):
        a = args[i]
        nxt = args[i + 1] if i + 1 < len(args) else None
        if a == "--amend":
            raise Blocked("amending commits is not allowed; make a new commit.")
        if a in ("--message",):
            messages.append(nxt)
            i += 2
            continue
        if a.startswith("--message="):
            messages.append(a.split("=", 1)[1])
        elif a in ("--file", "--template", "--reuse-message", "--reedit-message", "--fixup", "--squash") or \
                re.match(r"^--(file|template|reuse-message|reedit-message|fixup|squash)=", a):
            raise Blocked("commit message must be given inline with -m so it can be checked.")
        elif re.match(r"^-[a-zA-Z]+$", a):
            cluster = a[1:]
            for j, ch in enumerate(cluster):
                if ch in "FtCc":
                    raise Blocked("commit message must be given inline with -m so it can be checked.")
                if ch == "m":
                    value = cluster[j + 1:]
                    if value:
                        messages.append(value)
                    else:
                        messages.append(nxt)
                        i += 1
                    break
        elif re.match(r"^-m.+", a):
            messages.append(a[2:])
        i += 1

    check_branch(cwd)

    if not messages or messages[0] is None:
        raise Blocked("commit message must be given inline with -m so it can be checked.")
    subject = heredoc_body(messages[0]).lstrip("\n").split("\n", 1)[0].rstrip()
    if "$(" in subject:
        raise Blocked("commit message must be literal text so it can be checked.")
    problems = []
    if not SUBJECT_RE.match(subject):
        problems.append(f"subject must match '<type>(<scope>): <summary>' with type in [{TYPES.replace('|', ', ')}], "
                        "a scope, and a lowercase summary")
    if len(subject) > MAX_SUBJECT:
        problems.append(f"subject is {len(subject)} characters; the limit is {MAX_SUBJECT}")
    if problems:
        raise Blocked(f"commit message '{subject}': " + "; ".join(problems) + ".")


def check_branch(cwd):
    result = subprocess.run(["git", "-C", cwd, "symbolic-ref", "--short", "-q", "HEAD"],
                            capture_output=True, text=True)
    branch = result.stdout.strip()
    if result.returncode != 0 or not branch:
        raise Blocked("no current branch (detached HEAD or not a git repo); commit only on a <type>/<slug> branch.")
    if not BRANCH_RE.match(branch):
        raise Blocked(f"committing on '{branch}' is not allowed; commit only on a <type>/<slug> branch "
                      f"(types: {TYPES.replace('|', ', ')}).")


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    if data.get("tool_name") != "Bash":
        return 0
    command = (data.get("tool_input") or {}).get("command") or ""
    cwd = data.get("cwd") or os.getcwd()
    try:
        check_command(command, cwd)
    except Blocked as e:
        print(f"git-guard blocked this command: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
