# slim Python + no Oracle client needed (thin mode)
FROM python:3.12-slim

WORKDIR /app

# speed: avoid cache bloat; add build deps only if needed
RUN pip install --no-cache-dir oracledb Faker

COPY generate.py /app/generate.py

CMD ["python", "/app/generate.py"]
