#!/bin/bash
# mirror.sh: Rebuild the documentation mirror using tools from GitHub.

set -e

# 1. Configuration
VERSION=${1:-latest}
MIRROR_TOOL_PKG="github.com/apstndb/gcp-docs-mirror-tools@$VERSION"
BINARY_NAME="./gcp-docs-mirror-tools"

# 2. Cleanup
echo "--- Cleaning up old mirror state ---"
rm -rf docs/ logs/ metadata.yaml

# 3. Execution
# Prefer local binary if it exists
if [ -f "$BINARY_NAME" ]; then
    echo "--- Using local binary: $BINARY_NAME ---"
    chmod +x "$BINARY_NAME"
    "$BINARY_NAME" -config settings.toml
else
    # Fallback to go run
    echo "--- Binary not found. Falling back to go run ($MIRROR_TOOL_PKG) ---"
    echo "Note: This may take a while to download and compile."
    GOPROXY=direct go run "$MIRROR_TOOL_PKG" -config settings.toml
fi

echo "--- Rebuild complete ---"
echo "Check metadata.yaml, logs/* for changes."
