FROM python:3.11-slim

WORKDIR /app

COPY modelo/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY db/       /app/src/db/
COPY modelo/src/ /app/src/

ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1

CMD ["python", "src/modelo.py"]
