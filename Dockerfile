# Separate "build" image
FROM python:3.12-slim-bookworm as compile-image
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# "Run" image
FROM python:3.12-slim-bookworm
COPY --from=compile-image /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY alembic.ini /app/alembic.ini
COPY bot /app/bot
CMD ["python", "-m", "bot"]
