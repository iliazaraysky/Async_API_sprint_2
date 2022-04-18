FROM python:3.9-slim-buster
RUN mkdir /work && mkdir /work/tests
COPY ./requirements.txt /work
RUN pip install --upgrade pip && pip install -r ../work/requirements.txt
COPY ./tests /work/tests
WORKDIR /work/tests