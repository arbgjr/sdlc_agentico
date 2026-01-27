#!/bin/bash
# Uninstall local sdlc-import symlink installation

set -e

INSTALL_DIR="${HOME}/.claude/skills/sdlc-import"

echo "🗑️  Uninstalling local sdlc-import installation..."
echo ""

# Check if installation exists
if [ ! -e "$INSTALL_DIR" ]; then
    echo "❌ No installation found at: $INSTALL_DIR"
    exit 1
fi

# Check if it's a symlink (local install)
if [ -L "$INSTALL_DIR" ]; then
    TARGET="$(readlink "$INSTALL_DIR")"
    echo "📍 Found symlink installation:"
    echo "   $INSTALL_DIR -> $TARGET"
    echo ""

    # Check for backups
    BACKUPS=($(ls -dt ${INSTALL_DIR}.backup-* 2>/dev/null || true))

    if [ ${#BACKUPS[@]} -gt 0 ]; then
        echo "📦 Available backups:"
        for i in "${!BACKUPS[@]}"; do
            echo "   [$((i+1))] ${BACKUPS[$i]}"
        done
        echo "   [0] No restoration (clean uninstall)"
        echo ""
        read -p "Choose backup to restore (0-${#BACKUPS[@]}): " choice

        if [ "$choice" -gt 0 ] && [ "$choice" -le "${#BACKUPS[@]}" ]; then
            SELECTED_BACKUP="${BACKUPS[$((choice-1))]}"
            echo ""
            echo "🔄 Restoring backup..."
            rm "$INSTALL_DIR"
            mv "$SELECTED_BACKUP" "$INSTALL_DIR"
            echo "   ✅ Restored: $(basename "$SELECTED_BACKUP")"

            # Clean up other backups
            if [ ${#BACKUPS[@]} -gt 1 ]; then
                read -p "Delete other backups? (y/N): " delete_others
                if [ "$delete_others" = "y" ] || [ "$delete_others" = "Y" ]; then
                    for backup in "${BACKUPS[@]}"; do
                        if [ "$backup" != "$SELECTED_BACKUP" ]; then
                            rm -rf "$backup"
                            echo "   🗑️  Deleted: $(basename "$backup")"
                        fi
                    done
                fi
            fi
        else
            echo ""
            echo "🧹 Clean uninstall..."
            rm "$INSTALL_DIR"
            echo "   ✅ Symlink removed"

            # Ask about backups
            read -p "Delete all backups? (y/N): " delete_backups
            if [ "$delete_backups" = "y" ] || [ "$delete_backups" = "Y" ]; then
                for backup in "${BACKUPS[@]}"; do
                    rm -rf "$backup"
                    echo "   🗑️  Deleted: $(basename "$backup")"
                done
            else
                echo "   📦 Backups preserved (manual cleanup required)"
            fi
        fi
    else
        echo "⚠️  No backups found"
        echo ""
        read -p "Remove symlink anyway? (y/N): " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            rm "$INSTALL_DIR"
            echo "   ✅ Symlink removed"
        else
            echo "   ❌ Uninstall cancelled"
            exit 0
        fi
    fi
else
    echo "⚠️  Installation is not a symlink (regular installation)"
    echo "   This script only removes symlink installations"
    echo "   To uninstall regular installation, run:"
    echo "   rm -rf $INSTALL_DIR"
    exit 1
fi

echo ""
echo "✅ Uninstall complete!"
echo ""
echo "📋 Next steps:"
echo "   • To install from release:"
echo "     curl -fsSL \"https://github.com/arbgjr/sdlc_agentico/releases/download/v2.1.9/sdlc-agentico-v2.1.9.tar.gz\" | tar -xz"
echo "     cd sdlc-agentico-v2.1.9"
echo "     ./\.agentic_sdlc/scripts/setup-sdlc.sh"
echo ""
echo "   • To reinstall from local source:"
echo "     ./.claude/skills/sdlc-import/scripts/install-local.sh"
echo ""
