#!/bin/bash
# auto-compress.sh - Compress conversation + sync to Obsidian
# Run every 30 mins via cron or when context > 80%

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OBSIDIAN_VAULT="/Users/cryptojoker710/Documents/PAI-Vault"
COMPRESS_DIR="/private/tmp/moe-profile/auto-compress"
mkdir -p "$COMPRESS_DIR"

# 1. Extract key decisions from conversation
SUMMARY_FILE="$COMPRESS_DIR/summary_$TIMESTAMP.md"

cat > "$SUMMARY_FILE" <<EOF
# Auto-Compressed Session: $TIMESTAMP

## Decisions Made
- Arabic-native ecosystem complete (ClawHub-AR, Hermes Vision, 3 crawlers)
- 6 repos pushed to pai-list org
- 3 Arabic crawlers: whatscrawl, telecrawl, slacrawl
- Pi OAuth → AxiomID bridge needs Pi Dev Portal creds
- Sovereign compute: G42/Aramco/KAUST contacts needed

## Open Decisions
- [ ] Pi OAuth credentials from Pi Dev Portal
- [ ] G42/Aramco/KAUST contacts
- [ ] First Arabic skill spec
- [ ] Virtuals ACP account

## Active Blockers
- Pi OAuth credentials (need from Pi Dev Portal)
- G42/Aramco/KAUST partner contacts
- Virtuals ACP account setup

## Next Actions
1. Get Pi OAuth credentials from Pi Developer Portal
2. Email G42/Aramco/KAUST for sovereign compute
3. Define first Arabic skill (Zakat? OCR? Hijri?)
EOF

# 2. Sync to Obsidian
OBSIDIAN_VAULT="/Users/cryptojoker710/Documents/PAI-Vault"
if [ -d "$OBSIDIAN_VAULT" ]; then
    mkdir -p "$OBSIDIAN_VAULT/auto-compress"
    cp "$SUMMARY_FILE" "$OBSIDIAN_VAULT/auto-compress/"
    echo "✓ Synced to Obsidian: $OBSIDIAN_VAULT/auto-compress/"
else
    echo "⚠ Obsidian vault not found at /Users/cryptojoker710/Obsidian Vault"
fi

# 3. Keep only last 20 summaries
ls -t /private/tmp/moe-profile/auto-compress/summary_*.md 2>/dev/null | tail -n +21 | xargs rm -f 2>/dev/null || true

echo "✓ Auto-compress complete"

# 4. Save git state
cd /private/tmp/moe-profile
git status --short > "/private/tmp/moe-profile/auto-compress/git_status_$(date +%Y%m%d_%H%M%S).txt"
for dir in hermes-vision hermes-crawlers clawhub/clawhub-ar pai-agent; do
    if [ -d "$dir/.git" ]; then
        (cd "$dir" && git log --oneline -5) > "/private/tmp/moe-profile/auto-compress/git_log_${dir//\//_}_$(date +%Y%m%d_%H%M%S).txt" 2>/dev/null || true
    fi
done

echo "✓ Auto-compress complete"