FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


COPY ./requirements.txt /app

RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

COPY . /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8000

CMD ["/app/scripts/entrypoint.sh"]
