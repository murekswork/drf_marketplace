FROM python:3.10-slim
WORKDIR /marketplace

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

COPY marketplace /marketplace/
COPY requirements/marketplace_reqs/requirements.txt /marketplace/requirements.txt
COPY ./kafka_common /marketplace/kafka_common

RUN pip --default-timeout=2000 install -r requirements.txt
