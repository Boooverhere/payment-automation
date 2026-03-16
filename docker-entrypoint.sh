#!/bin/sh
set -e

# Export all environment variables so cron jobs can access them.
# (Cron does not inherit the container's env by default.)
printenv | grep -v "no_proxy" > /etc/environment

echo "Payment automation container started. Cron scheduler running."
exec cron -f
