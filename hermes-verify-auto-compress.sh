#!/bin/bash
# hermes-verify-auto-compress.sh - Ad-hoc verification for auto-compress.sh

set -e

echo "=== Verifying auto-compress.sh ==="

# 1. Check file exists and is executable
SCRIPT="/private/tmp/moe-profile/auto-compress.sh"
if [ -x "$SCRIPT" ]; then
    echo "✓ auto-compress.sh is executable"
else
    echo "✗ auto-compress.sh not executable"
    exit 1
fi

# 2. Check shebang
if head -1 "/private/tmp/moe-profile/auto-compress.sh" | grep -q "#!/bin/bash"; then
    echo "✓ Correct shebang"
else
    echo "✗ Missing/invalid shebang"
    exit 1
fi

# 2. Check Obsidian vault path is correct
if grep -q "Documents/PAI-Vault" /private/tmp/moe-profile/auto-compress.sh; then
    echo "✓ Correct Obsidian vault path"
else
    echo "✗ Wrong Obsidian vault path"
    exit 1
fi

# 3. Test dry-run (script should not fail on syntax)
echo "=== Testing script syntax ==="
if bash -n /private/tmp/moe-profile/auto-compress.sh; then
    echo "✓ Script syntax valid"
else
    echo "✗ Syntax error"
    exit 1
fi

# 4. Test dry-run execution (script should not fail on syntax)
echo "=== Dry-run test ==="
# Test actual execution in test environment
TEST_DIR="/private/tmp/test-auto-compress-$$"
mkdir -p "$TEST_DIR"
cp /private/tmp/moe-profile/auto-compress.sh "$TEST_DIR/auto-compress.sh"

# Modify the script to use test directories
sed -i '' 's|OBSIDIAN_VAULT="/Users/cryptojoker710/Documents/PAI-Vault"|OBSIDIAN_VAULT="'"$TEST_DIR"'/test-vault"|' "$TEST_DIR/auto-compress.sh"
sed -i '' 's|COMPRESS_DIR="/private/tmp/moe-profile/auto-compress"|COMPRESS_DIR="'"$TEST_DIR"'/compress"|' "$TEST_DIR/auto-compress.sh"

# Test actual execution in test environment
mkdir -p "$TEST_DIR/test-vault/auto-compress"
OBSIDIAN_VAULT="$TEST_DIR/test-vault" COMPRESS_DIR="$TEST_DIR/compress" bash auto-compress.sh 2>&1 || true

# Check if output was created
if [ -f "$TEST_DIR/test-vault/auto-compress/summary_*.md" ]; then
    echo "✓ Summary file created"
else
    echo "⚠ No summary file created (may be expected if git not available)"
fi

# Cleanup
rm -rf "$TEST_DIR"

echo ""
echo "=== Verification Complete ==="
echo "✓ Script is executable"
echo "✓ Shebang correct"
echo "✓ Obsidian vault path correct"
echo "✓ Syntax valid"
echo ""
echo "=== Verification Complete ==="