#!/usr/bin/env bash
set -euo pipefail

echo "Setting up Coding Agent..."
pushd cli >/dev/null
npm install || true
popd >/dev/null
pushd server >/dev/null
pip install -r requirements.txt || true
popd >/dev/null
echo "Done."
