FROM python:3.11-slim

WORKDIR /app
COPY shared /app/shared
COPY services/publishing /app/service
WORKDIR /app/service

RUN pip install fastapi>=0.110.0 uvicorn>=0.29.0 pydantic>=2.7.0 tweepy>=4.14.0 httpx>=0.27.0
RUN pip install -e /app/shared

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
