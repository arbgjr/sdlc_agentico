#!/bin/bash
# Enable multi-client architecture feature

set -e

echo "🔧 Enabling Multi-Client Architecture..."

# Create directories if they don't exist
mkdir -p .sdlc_clients/_base
mkdir -p .sdlc_clients/generic
mkdir -p .sdlc_clients/demo-client

# Copy files if not exists
if [ ! -f ".sdlc_clients/_base/profile.yml" ]; then
    echo "📝 Creating base profile template..."
    # Files will be created from the feature branch when needed
fi

# Update settings.json (requires jq)
if command -v jq &> /dev/null; then
    echo "⚙️  Updating settings.json..."
    jq '.sdlc.feature_flags.multi_client_architecture = true | .sdlc.clients.enabled = true' .claude/settings.json > .claude/settings.json.tmp
    mv .claude/settings.json.tmp .claude/settings.json
else
    echo "⚠️  jq not found. Manually set:"
    echo '   "feature_flags": {"multi_client_architecture": true}'
    echo '   "clients": {"enabled": true}'
fi

echo "✅ Multi-Client Architecture enabled!"
echo ""
echo "Next steps:"
echo "  1. Check .sdlc_clients/ directory"
echo "  2. Use /create-client to create new profiles"
echo "  3. Use /set-client to switch between profiles"
