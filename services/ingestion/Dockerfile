FROM python:3.11-slim

WORKDIR /app
COPY shared /app/shared
COPY services/ingestion /app/service
WORKDIR /app/service

RUN pip install fastapi>=0.110.0 uvicorn>=0.29.0 pydantic>=2.7.0 slack-sdk>=3.27.0 firecrawl-py>=1.0.0 google-auth>=2.29.0 google-api-python-client>=2.124.0
RUN pip install -e /app/shared

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
