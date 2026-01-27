---
name: claude-settings-editing
description: Edit Claude Code settings.json files. Use when modifying permissions, hooks, or other Claude configuration.
allowed-tools: Read, Edit, Write
disable-model-invocation: false
---

Claude Settings Editing
=======================

You are a specialist in editing Claude Code `settings.json` configuration files. Apply these rules when adding or modifying permissions, hooks, or other settings.

---

Permission Path Rules
---------------------

### Do Not Use Relative Paths

Relative paths with `.` do not work in permission patterns. Never use patterns like:

- `Read(./**)`
- `Grep(./*)`
- `Edit(./src/**)`

These will silently fail to match.

### Use Absolute Paths

Always specify the full absolute path. When the path is within the user's home directory, use `~` to make the configuration portable across machines.

**Correct:**
```json
"allow": [
  "Read(~/projects/myapp/**)",
  "Grep(~/projects/myapp/**)",
  "Edit(~/projects/myapp/src/**)"
]
```

**Incorrect:**
```json
"allow": [
  "Read(./**)",
  "Grep(./*)",
  "Edit(./src/**)"
]
```

### Use `~` Instead of Hardcoded Home Paths

Do not hardcode absolute paths that include the username. This breaks portability when the settings file is shared or synced across machines.

**Correct:**
```json
"Read(~/projects/myapp/**)"
```

**Incorrect:**
```json
"Read(/Users/john/projects/myapp/**)"
```

---

When to Ask for Clarification
-----------------------------

Ask the user before proceeding if:
- The intended scope of a permission is ambiguous
- A permission pattern could unintentionally grant broad access
- You are unsure whether to add a permission to `allow` or `deny`

---

Verification
------------

Before finalizing changes to a settings.json file:

1. Confirm all permission paths use absolute paths (no `.` relative paths)
2. Confirm home directory paths use `~` instead of hardcoded usernames
3. Validate JSON syntax is correct
4. Check for duplicate entries in allow/deny lists
