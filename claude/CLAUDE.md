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
When you are installing Go dependencies in a project, use `go install`.
