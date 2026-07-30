FROM python:3.11-slim

WORKDIR /app
COPY shared /app/shared
COPY services/generation /app/service
WORKDIR /app/service

RUN pip install fastapi>=0.110.0 uvicorn>=0.29.0 pydantic>=2.7.0 langchain>=0.1.13 langgraph>=0.0.30 langchain-anthropic>=0.1.4 langchain-google-vertexai>=0.1.2
RUN pip install -e /app/shared

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
