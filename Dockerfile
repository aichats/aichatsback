FROM python:3.11 AS builder

WORKDIR /app

RUN python -m venv venv
RUN . venv/bin/activate

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

FROM python:3.11-slim

ENV mode=production
ENV PINECONE_API_KEY=""
ENV PINECONE_API_ENV=""
ENV OPENAI_API_KEY=""
ENV OPENAI_EMBEDDINGS_LLM=text-embedding-ada-002
ENV OPENAI_CHAT_MODEL=gpt-3.5-turbo
ENV INDEX_NAME=aichat
ENV PORT=80

EXPOSE 80

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app/venv /app/venv

RUN . venv/bin/activate

RUN if [ "$mode" = "testing" ]; then pip install -r requirements-test.txt; fi

COPY . .

ENTRYPOINT ["python","-m","uvicorn", "app:app", "--host", "0.0.0.0", "--port", "$PORT","--workers","4"]
