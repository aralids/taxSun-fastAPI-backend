FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates tar \
  && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy dependency files first (better caching)
COPY pyproject.toml poetry.lock* /app/

# Install deps into system site-packages (no venv in container)
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi

# Copy the rest of your backend code
COPY . /app

# Bake NCBI taxonomy files into the image
RUN mkdir -p /app/data/taxonomy \
 && cd /app/data/taxonomy \
 && curl -L -o taxdump.tar.gz https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz \
 && tar -xzf taxdump.tar.gz names.dmp nodes.dmp merged.dmp \
 && rm taxdump.tar.gz

CMD ["sh", "-c", "hypercorn app.main:app --bind 0.0.0.0:$PORT"]
