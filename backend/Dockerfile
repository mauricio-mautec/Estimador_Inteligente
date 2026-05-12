FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ /app/src/
# Expomos a porta 8000. O Uvicorn lidará com a alta concorrência (RNF002)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]