FROM python:3.9.7

USER root
WORKDIR /usr/src

ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y libgl1-mesa-dev

RUN pip3 install --upgrade pip \
    && pip3 install typed-argument-parser \
    && pip3 install poetry \
    && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock /usr/src/
RUN poetry install

COPY . /usr/src/
