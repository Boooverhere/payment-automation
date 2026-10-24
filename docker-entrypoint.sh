#!/bin/sh
set -e

# Export all environment variables so cron jobs can access them.
# (Cron does not inherit the container's env by default.)
printenv | grep -v "no_proxy" > /etc/environment

# Cron jobs run as root; create the log file first so it stays writable by
# appuser (gunicorn can't boot if root created it).
touch /app/payment.log
chown appuser:appuser /app/payment.log

# Start cron as a background daemon (handles 24h/48h/72h reminders)
cron

echo "Payment automation container started."
echo "  - Cron running for reminder emails (24h / 48h / 72h)"
echo "  - Webhook server starting via Gunicorn"

# Start Gunicorn as the webhook server in the foreground (PID 1)
# 2 workers, 30s timeout, binds to internal port 8000
exec su -s /bin/sh appuser -c \
    "gunicorn --workers 2 --timeout 30 --bind 0.0.0.0:8000 webhook_server:app"
