# Bash Heredoc Variable Expansion Pitfall

## Problem
When writing verification scripts that use temporary directories, `$TMPDIR` inside single-quoted heredocs won't expand. This causes "Permission denied" or "file not found" errors that are hard to diagnose.

## Examples

### ❌ Broken — single-quoted heredoc
```bash
TMPDIR=$(mktemp -d /tmp/hermes-verify.XXXXXX)
cat > "$TMPDIR/verify.sh" << 'VERIFY'
echo "Writing to $TMPDIR/test.txt"  # <-- $TMPDIR NOT expanded!
echo "test" > "$TMPDIR/test.txt"  # Creates file named "$TMPDIR/test.txt" literally
VERIFY
```

### ✅ Fixed — use explicit paths or double-quote heredoc
```bash
TMPDIR=$(mktemp -d /tmp/hermes-verify.XXXXXX)
cat > "$TMPDIR/verify.sh" << 'VERIFY'
echo "Writing to /tmp/hermes_verify_test.txt"
echo "test" > /tmp/hermes_verify_test.txt
VERIFY
# Or inline the path:
cat > "$TMPDIR/verify.sh" << VERIFY
echo "Writing to $TMPDIR/test.txt"  # <-- double-quote heredoc = variable expands
VERIFY
```

## Lesson
When writing verification scripts, prefer explicit absolute paths (like `/tmp/hermes_verify_test.txt`) over `$TMPDIR` variables inside single-quoted heredocs. Or use double-quoted heredoc delimiters (`<< EOF` instead of `<< 'EOF'`) but be careful about other `$` symbols in the script.

This is a common "tight feedback loop construction" failure — the verification script itself has a bug that masks the real test results.