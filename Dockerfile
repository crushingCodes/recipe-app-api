FROM python:3.7-alpine

# PYTHON Environment SETUP
ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt /requirements.txt

# These requirements stay in the container
RUN apk add --update --no-cache postgresql-client jpeg-dev

# Temp requirements to build Postgres client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

# Install the requirements
RUN pip install -r /requirements.txt

#Move app to docker
RUN mkdir /app
WORKDIR /app
COPY ./app /app

# Put everything we might need access to in vol(in case other containers need access)
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

# Limit the permissions by creating a custom user
RUN adduser -D user

# Set permissions recursively to custom user for vol folder
RUN chown -R user:user /vol/

# Owner can modify, others can just read
RUN chmod -R 755 /vol/web

# Set the active user to user
USER user