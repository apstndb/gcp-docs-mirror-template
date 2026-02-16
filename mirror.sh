#!/bin/bash
# mirror.sh: Rebuild the entire Spanner documentation mirror using tools from GitHub.

set -e

# 1. Configuration
# Allow overriding the version (stable tag, commit hash, or 'latest') via first argument
VERSION=${1:-v0.2.2}
MIRROR_TOOL="github.com/apstndb/gcp-docs-mirror-tools@$VERSION"

# 2. Cleanup
# Ensure a clean state to avoid "ghost files" from deleted documentation.
echo "--- Cleaning up old mirror state ---"
rm -rf docs/ logs/ metadata.yaml

# 3. Execution
echo "--- Starting full Spanner documentation mirror rebuild via go run ($MIRROR_TOOL) ---"
# Use GOPROXY=direct to ensure we get the absolute latest if requested
# Pass -config settings.toml to the tool
GOPROXY=direct go run "$MIRROR_TOOL" -config settings.toml

echo "--- Rebuild complete ---"
echo "Check metadata.yaml, logs/* for changes."
