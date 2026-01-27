#!/bin/bash
# Install sdlc-import from local source (for testing)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
INSTALL_DIR="${HOME}/.claude/skills/sdlc-import"

echo "🔧 Installing sdlc-import from local source..."
echo "   Source: $SKILL_DIR"
echo "   Target: $INSTALL_DIR"

# Backup existing installation
if [ -d "$INSTALL_DIR" ]; then
    BACKUP_DIR="${INSTALL_DIR}.backup-$(date +%Y%m%d-%H%M%S)"
    echo "📦 Backing up existing installation to:"
    echo "   $BACKUP_DIR"
    mv "$INSTALL_DIR" "$BACKUP_DIR"
fi

# Create installation directory
mkdir -p "$(dirname "$INSTALL_DIR")"

# Create symlink to local source
ln -sf "$SKILL_DIR" "$INSTALL_DIR"

echo "✅ Installation complete!"
echo ""
echo "🧪 Testing installation:"

# Verify installation
if [ -L "$INSTALL_DIR" ] && [ -e "$INSTALL_DIR" ]; then
    echo "   ✓ Symlink created successfully"
    echo "   → $INSTALL_DIR -> $SKILL_DIR"
else
    echo "   ✗ Symlink creation failed"
    exit 1
fi

# Verify scripts are accessible
if [ -f "$INSTALL_DIR/scripts/sdlc_import.py" ]; then
    echo "   ✓ Scripts accessible"
else
    echo "   ✗ Scripts not found"
    exit 1
fi

echo ""
echo "📋 Usage in target project:"
echo "   cd ~/source/repos/tripla/autoritas"
echo "   python3 ~/.claude/skills/sdlc-import/scripts/sdlc_import.py --interactive"
echo ""
echo "🔄 To revert to released version:"
if [ -n "$(ls -d ${INSTALL_DIR}.backup-* 2>/dev/null | head -1)" ]; then
    LATEST_BACKUP="$(ls -dt ${INSTALL_DIR}.backup-* | head -1)"
    echo "   rm $INSTALL_DIR"
    echo "   mv $LATEST_BACKUP $INSTALL_DIR"
fi
echo ""
echo "🎯 Now test in Autoritas to verify C1, C3, C4 fixes!"
