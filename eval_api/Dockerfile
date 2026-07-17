FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY eval_api.py .

CMD ["uvicorn", "eval_api:app", "--host", "0.0.0.0", "--port", "8080"]
