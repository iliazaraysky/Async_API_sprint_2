FROM python:3.9-slim-buster
RUN mkdir /fastapi
COPY ./requirements.txt /fastapi
RUN pip install --upgrade pip && pip install -r ../fastapi/requirements.txt
COPY . /fastapi
WORKDIR /fastapi/
CMD ["python", "src/main.py"]
