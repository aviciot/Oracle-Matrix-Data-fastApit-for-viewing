FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn oracledb jinja2 watchfiles

COPY app.py /app/app.py
COPY templates /app/templates
COPY static /app/static

ENV HOST=0.0.0.0 PORT=8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
