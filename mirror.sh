#!/bin/bash
# mirror.sh: Rebuild the documentation mirror using tools from GitHub.

set -euo pipefail

# 1. Configuration
VERSION=${1:-latest}
MIRROR_TOOL_PKG="github.com/apstndb/gcp-docs-mirror-tools@$VERSION"
BINARY_NAME="./gcp-docs-mirror-tools"

# 2. Stage a fresh snapshot; failed fetches never remove the published mirror.
mkdir -p .tmp
STAGE=$(mktemp -d .tmp/mirror.XXXXXX)
echo "--- Staging mirror in $STAGE ---"
ARGS=(-config settings.toml -docs "$STAGE/docs" -logs "$STAGE/logs" -metadata "$STAGE/metadata.yaml")

# 3. Execution
# Prefer local binary if it exists
if [ -f "$BINARY_NAME" ]; then
    echo "--- Using local binary: $BINARY_NAME ---"
    chmod +x "$BINARY_NAME"
    "$BINARY_NAME" "${ARGS[@]}"
else
    # Fallback to go run
    echo "--- Binary not found. Falling back to go run ($MIRROR_TOOL_PKG) ---"
    echo "Note: This may take a while to download and compile."
    GOPROXY=direct go run "$MIRROR_TOOL_PKG" "${ARGS[@]}"
fi

python3 scripts/validate-mirror.py "$STAGE"

# Keep the previous snapshot for recovery. Staging and backup are on the same
# filesystem. A failed promotion stops before the workflow can commit anything.
mkdir "$STAGE/previous"
for entry in docs logs metadata.yaml; do
    if [[ -e "$entry" ]]; then
        mv "$entry" "$STAGE/previous/$entry"
    fi
    mv "$STAGE/$entry" "$entry"
done

echo "--- Rebuild complete ---"
echo "Previous snapshot retained in $STAGE/previous"
echo "Check metadata.yaml, logs/* for changes."
