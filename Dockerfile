# Build stage
FROM python:3.12-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bot alembic.ini /app/

# Final stage
FROM gcr.io/distroless/python3-debian12
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /app /app
WORKDIR /app
ENV PYTHONPATH=/usr/local/lib/python3.12/site-packages
CMD ["python", "-m", "bot"]