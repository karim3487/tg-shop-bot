#!/bin/bash
set -e

# Ensure logs and staticfiles directories exist and are owned by appuser
# We do this as root before dropping privileges
if [ "$(id -u)" = '0' ]; then
    mkdir -p /app/logs /app/staticfiles
    chown -R appuser:appgroup /app/logs /app/staticfiles /app/.venv
    
    # Exec the command as appuser
    exec gosu appuser "$@"
fi

# If already running as non-root, just exec
exec "$@"
