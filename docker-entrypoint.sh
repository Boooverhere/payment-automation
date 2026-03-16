#!/bin/sh
set -e

# Export all environment variables so cron jobs can access them.
# (Cron does not inherit the container's env by default.)
printenv | grep -v "no_proxy" > /etc/environment

# Start cron as a background daemon (handles 24h/48h/72h reminders)
cron

echo "Payment automation container started."
echo "  - Cron running for reminder emails (24h / 48h / 72h)"
echo "  - Webhook server starting for instant invoice delivery"

# Start Flask webhook server in the foreground (PID 1)
exec python3 webhook_server.py
