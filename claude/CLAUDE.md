General Principles
==================
- You should write code that is clear, well-factored, and easy to maintain. When a function, class, or file gets long, break it into smaller pieces.
- Function names should start with verbs, e.g. `doSomething` or `findThing`
- Write DRY (Don't Repeat Yourself) code. Rather than repeating yourself, use variables and named constants.
- Favor defensive code that checks edge cases and error conditions.
- Use linters to catch potential problems early.
- When given instructions, push for clarity and specificity. Do not start making changes until you understand the task you're trying to complete.

Markdown
========
When writing Markdown, do not use `#` for h1 and `##` for h2. Instead, follow the h1 line with a line of `=` equal to the length of the line, like so:

```
My h1 Text
==========
```

Do the same thing for h2, only with `-`.

When modifying Git repositories
===============================
When you're about to finish completing a task and return control to the user, propose a `git` command that will add the files you changed and commit them with a succinct but descriptive commit message explaining what changes were made.

The commit should be a single sentence. There should be no commit body, or "Generated With Claude Code".

Dependencies
============
When choosing dependencies, use the latest stable released version unless you have a compelling reason to do otherwise.

Generating  bash files
======================
When you are generating new Bash files, always start with this header:

```
set -euo pipefail
script_dirpath="$(cd "$(dirname "${0}")" && pwd)"
```

You should then use the declared `script_dirpath` variable inside the script if you need to reference files relative to the script.

Golang
======
When you add or update Go dependencies to a Go project, use `go install`. Do not directly manipulate the `go.mod` file.

When starting a new project from scratch, use this error-handling library: https://github.com/kurtosis-tech/stacktrace . It provides good stacktrace support that makes debugging easier.
