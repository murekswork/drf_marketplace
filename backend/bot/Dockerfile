FROM python:3.10-slim
WORKDIR /app

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

RUN pip install pip-tools
COPY ./bot /app/bot
COPY requirements/bot_reqs/requirements.txt /app/requirements.txt
COPY ./kafka_common /app/bot/kafka_common

RUN pip-sync requirements.txt
