FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p logs
VOLUME ["/app/data"]
ENV PYTHONBUFFERED=1
ENV DATABASE_PATH=/app/data/product_data.db
RUN mkdir -p /app/data && \
    chmod 777 /app/data
RUN python3 -c "from scraper.db_manager import DatabaseManager; DatabaseManager('/app/data/product_data.db')"
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8080 || exit 1
CMD ["sh", "-c", "python3 migration_script.py && python3 main.py"]
EXPOSE 8080