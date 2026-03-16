FROM python:3.11-slim

# Install cron only — no extra packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends cron \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies as a separate cached layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (secrets are excluded via .dockerignore)
COPY . .

# Copy and register the crontab
COPY docker-cron /etc/cron.d/payment-cron
RUN chmod 0644 /etc/cron.d/payment-cron

# Entrypoint: exports env vars so cron can read them, then starts cron
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

CMD ["/docker-entrypoint.sh"]
