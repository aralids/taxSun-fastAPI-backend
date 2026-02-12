FROM python:3.12-slim

WORKDIR /app

# Tools needed to download + extract NCBI taxdump at build time
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates tar \
  && rm -rf /var/lib/apt/lists/*

# Install dependencies first (better caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of your backend code
COPY . /app

# Bake NCBI taxonomy files into the image (NO runtime download)
RUN mkdir -p /app/data/taxonomy \
 && cd /app/data/taxonomy \
 && curl -L -o taxdump.tar.gz https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz \
 && tar -xzf taxdump.tar.gz names.dmp nodes.dmp merged.dmp \
 && rm taxdump.tar.gz

# Railway provides $PORT at runtime
# IMPORTANT: adjust "app.main:app" to your real import path if needed
CMD ["sh", "-c", "hypercorn app.main:app --bind 0.0.0.0:${PORT} --workers 2 --access-logfile - --error-logfile - --log-level info"]

