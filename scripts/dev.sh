#!/usr/bin/env bash
set -euo pipefail

tmux new-session -d -s codingagent 'cd server && uvicorn api.main:app --reload'
tmux split-window -t codingagent 'cd web-ui && npm run dev'
tmux split-window -t codingagent 'cd cli && npm link && coding-agent --help || true'
tmux attach -t codingagent
