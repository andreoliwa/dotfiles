# Hookify Global Rule File Patch

## What the patch does

The hookify plugin's `config_loader.py` has a `load_rules()` function that only scans `.claude/hookify.*.local.md` relative to the current working directory. The patch adds a second glob that also scans `~/.claude/hookify.*.local.md`, so rules defined globally apply in every repository.

## The patch

Find this block in `load_rules()`:

```python
    # Find all hookify.*.local.md files
    pattern = os.path.join('.claude', 'hookify.*.local.md')
    files = glob.glob(pattern)
```

Replace with:

```python
    # Find all hookify.*.local.md files (local project + global ~/.claude/)
    pattern = os.path.join('.claude', 'hookify.*.local.md')
    global_pattern = os.path.join(os.path.expanduser('~'), '.claude', 'hookify.*.local.md')
    files = list(set(glob.glob(pattern) + glob.glob(global_pattern)))
```

## Files to patch

There are two copies, both must be patched:

1. **Marketplace copy** (durable, survives plugin version bumps):
   `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/hookify/core/config_loader.py`

2. **Cache copy** (active, used at runtime — there may be multiple versioned subdirs, patch all of them):
   `~/.claude/plugins/cache/claude-plugins-official/hookify/*/core/config_loader.py`

## Logic for the Invoke task

1. Resolve both file sets using glob: the marketplace path (single file) and the cache path (wildcard over version hash dirs).
2. For each file found:
   a. Read the file content.
   b. Check if the old string is present (idempotency — skip if already patched).
   c. Replace the old string with the new string.
   d. Write the file back.
3. Report which files were patched and which were already up to date.
4. Exit non-zero if any target file is missing entirely (unexpected state).

## Old string (exact match)

```
    # Find all hookify.*.local.md files
    pattern = os.path.join('.claude', 'hookify.*.local.md')
    files = glob.glob(pattern)
```

## New string (exact replacement)

```
    # Find all hookify.*.local.md files (local project + global ~/.claude/)
    pattern = os.path.join('.claude', 'hookify.*.local.md')
    global_pattern = os.path.join(os.path.expanduser('~'), '.claude', 'hookify.*.local.md')
    files = list(set(glob.glob(pattern) + glob.glob(global_pattern)))
```
