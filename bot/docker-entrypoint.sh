#!/bin/bash
set -e

# Ensure logs directory exists and is owned by appuser
if [ "$(id -u)" = '0' ]; then
    mkdir -p /app/logs
    chown -R appuser:appgroup /app/logs /app/.venv /app
    
    # Exec the command as appuser
    exec gosu appuser "$@"
fi

# If already running as non-root, just exec
exec "$@"
