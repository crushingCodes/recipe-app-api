From python:3.7-alpine

#PYTHON SETUP
ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

#Move app to docker
RUN mkdir /app
WORKDIR /app
COPY ./app /app

#Limit the permissions
RUN adduser -D user
USER user