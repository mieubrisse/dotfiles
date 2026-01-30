About This Repo
===============
This repository contains the user's dotfiles. Each tool's configuration files live in their own subdirectory (e.g., `bash/`, `git/`, `vim/`, `tmux/`).

The `init.sh` script symlinks these dotfiles into their correct locations in the home directory. This script is idempotent and can be run multiple times safely.

---

**IMPORTANT:** When asked to fix a problem, your solution is NOT to just comment out the code, removing the problem! You must fix the problem, not ignore it.

**IMPORTANT:** Before proposing any fix, critically reflect: "Will this change actually fix the problem?" If you find yourself reasoning that something "should work" or "shouldn't be the issue" while simultaneously proposing a change to it, STOP. That's a signal you don't understand the root cause. Do not propose changes you know won't address the actual problem. Instead:

1. State clearly what you believe the root cause is
2. Explain why your proposed change addresses that root cause
3. If you're uncertain about the root cause, say so and investigate further before making changes

**IMPORTANT:** When you need the user to run a command manually, make it visually obvious. Use attention-grabbing formatting like:

🚨 **ACTION REQUIRED** 🚨

Please run the following command:
```
your-command-here
```

Do not bury required user actions in paragraphs of text. The user may be skimming your output, so make manual steps impossible to miss.

General Principles
==================
- You should write code that is clear, well-factored, and easy to maintain. When a function, class, or file gets long, break it into smaller pieces.
- Function names should start with verbs. For example, `doSomething` or `findThing`
- Write DRY (Don't Repeat Yourself) code. Rather than repeating yourself, use variables and named constants.
- Favor defensive code that checks edge cases and error conditions.
- Use linters to catch potential problems early.
- When given instructions, push for clarity and specificity. Do not start making changes until you understand the task you're trying to complete.
- **IMPORTANT:** If the project contains a devcontainer, any tools the user might need should be captured in the devcontainer. There should be no requirements for the user to install anything on their local machine.

Path Variable Naming Guidance
================================
When naming variables that contain file or directory names or paths, use the following guidance:

- Use "file" or "dir" to indicate whether the variable contains a file or directory path...
- ....combined with with "name" or "path" to indicate whether the variable contains the name of the file/directory, or the path
- Variables with "path" should contain the absolute path by default

For example, in Bash syntax:

- `health_history_filepath` contains the full path to a file containing health history
- `health_history_dirpath` contains the full path to a directory containing health history
- `health_history_filename` contains just the filename of a file containing health history

When it's necessary to work with relative filepaths, add the "abs" and "rel" specifiers to indicate whether the variable contains a relative or absolute path.

For example, in Bash syntax:
- `health_history_rel_filepath` contains the path to a health history file, relative to something else
- `health_history_abs_filepath` contains the absolute path to a health history file

Adapt this naming guidance into the standard naming conventions of the coding language that's being written.

Markdown
========
When writing Markdown headers, do not use `#` for h1. Instead, use the alternate h1 style of following the line with an equivalent-length line of `=`.

For example:

```
My h1 Text
==========
```

Do the same thing for h2: do not use `##`, and do use an equivalent-length line of `-`.

For example:

```
My h2 Text
----------
```

Git Command Rules
=================
The following rules apply to ALL git commands — whether run directly by you, by a subagent you spawn, or proposed to the user.

### Do not use `git -C` to target the current working directory

Do not use `git -C <path>` when `<path>` is the current working directory. Just run `git` directly.

A PreToolUse hook (`block-redundant-git-c.sh`) enforces this by automatically stripping `-C <path>` from any git command where the path matches the current working directory. Using `git -C` to target a genuinely different directory is unaffected.

- Bad: `git -C /Users/odyssey/app/dotfiles status` (when PWD is `/Users/odyssey/app/dotfiles`)
- Good: `git status`
- OK: `git -C /some/other/repo status` (when PWD is a different directory)

### Commit automatically

When working in a Git repository and you're about to finish a task and return control to the user, automatically `git add` and `git commit` your changes. Do not ask for permission or propose the commands — just commit. The user can always amend, reset, or revert if needed.

**Commit message format:** Use a single-line commit message only. Do NOT use multi-line commit messages. Do NOT add "Co-Authored-By", "Authored-by", or any attribution lines. Just a simple `-m "message"` with a succinct, descriptive message.

- Good: `git commit -m "Add user authentication to login flow"`
- Bad: `git commit -m "Add user authentication" -m "Co-Authored-By: ..."`

### Separate git operations

**NEVER chain git commands with `&&`.** Whether executing commands yourself OR proposing commands to the user, always keep `git add`, `git commit`, and `git push` as separate commands.

- Bad: `git add file.txt && git commit -m "message"`
- Good: run `git add file.txt` and `git commit -m "message"` as separate commands

Dependencies
============
When choosing dependencies, use the latest stable released version unless you have a compelling reason to do otherwise.

Bash
======================
When you are generating new Bash files, always start with this header:

```
set -euo pipefail
script_dirpath="$(cd "$(dirname "${0}")" && pwd)"
```

You should then use the declared `script_dirpath` variable inside the script if you need to reference files relative to the script.

When you are referencing variables, always use the full form with curly braces, `${}`. For example, `${my_var}` and not `$my_var`.

Golang
======
When you add or update Go dependencies to a Go project, use `go install`. Do not directly manipulate the `go.mod` file.

When starting a new project from scratch, use this error-handling library: https://github.com/mieubrisse/stacktrace  It provides good stacktrace support that makes debugging easier.

When writing CLI tools, use the Cobra CLI tool library: https://github.com/spf13/cobra

Claude Code
===========
The files `~/.claude/CLAUDE.md` and `~/.claude/settings.json` are symlinks to `claude/CLAUDE.md` and `claude/settings.json` in this repo. When working in the dotfiles repository, read and update the files directly in the `claude/` directory rather than following the symlinks to the home directory.

When updating Claude `settings.json` files, always use `~` instead of hardcoded absolute paths (e.g., `/Users/username/...`). This ensures the settings remain portable across different machines.

🚨 **MANDATORY: USE /prompt-engineer FOR ALL PROMPT FILES** 🚨

When creating or updating CLAUDE.md or SKILL.md files, you **MUST** use the `/prompt-engineer` skill. Do NOT write these files directly. The prompt-engineer skill is specifically designed to optimize AI system prompts and produces significantly higher-quality results.

**This is not optional.** Before writing any content to a CLAUDE.md or SKILL.md file:
1. Invoke `/prompt-engineer`
2. Let it generate or refine the prompt
3. Only then write the result to the file
