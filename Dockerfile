FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt /app

RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

COPY . /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8000

CMD ["/app/scripts/entrypoint.sh"]
