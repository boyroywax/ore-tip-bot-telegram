FROM python:3.10.1-alpine3.15

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY requirements.txt .

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

RUN addgroup -S appgroup && adduser -S app -G appgroup

COPY .env .

COPY ./src/ .

USER app

CMD ["python3", "main.py"]