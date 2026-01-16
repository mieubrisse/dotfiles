**IMPORTANT:** When asked to fix a problem, your solution is NOT to just comment out the code, removing the problem! You must fix the problem, not ignore it.

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

When modifying Git repositories
===============================
### Pushing
Instead of `git push`, use `gp`. You do not have access to `git push`, but you do have access to `gp`.

### Commit Often
When you're about to finish completing a task and return control to the user, propose a `git` command that will...
1. Add the files you changed
2. Commit them with a succinct but descriptive commit message explaining what changes were made. The commit should be a single sentence. There should be no commit body, or "Generated With Claude Code".
3. Push them with the `gp` command (not `git push`).

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

When starting a new project from scratch, use this error-handling library: https://github.com/kurtosis-tech/stacktrace . It provides good stacktrace support that makes debugging easier.

When writing CLI tools, use the Cobra CLI tool library: https://github.com/spf13/cobra
