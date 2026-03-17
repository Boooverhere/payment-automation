FROM python:3.11-slim

# Install cron only — no extra packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends cron \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user to run the app
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Install dependencies as a separate cached layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (secrets are excluded via .dockerignore)
COPY . .

# Copy and register the crontab (cron must run as root)
COPY docker-cron /etc/cron.d/payment-cron
RUN chmod 0644 /etc/cron.d/payment-cron

# Give appuser ownership of the app directory
RUN chown -R appuser:appuser /app

# Entrypoint: exports env vars so cron can read them, then starts cron + gunicorn
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

CMD ["/docker-entrypoint.sh"]
