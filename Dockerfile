###########
# BUILDER #
###########

FROM python:3.10.1-alpine3.15 as builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN python3 -m pip install --upgrade pip
# install python dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

RUN pip install flake8
# Copy the src and lint
COPY ./src/ .
RUN python3 -m flake8 --ignore=E501,F401,F541,F841 --exclude=env/lib .



#########
# FINAL #
#########

# pull official base image
FROM python:3.10.1-alpine3.15

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install git
RUN apk add git

# create directory for the app user
ENV HOME=/home/app
RUN mkdir -p ${HOME}

ENV USER=app
ENV UID=1001

# create the app user
RUN addgroup -S $USER
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "$HOME" \
    --ingroup "$USER" \
    --no-create-home \
    --uid "$UID" \
    "$USER"

# create the appropriate directories
ENV APP_HOME=/home/app/web
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

# install dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends netcat
COPY --from=builder /usr/src/app/wheels /wheels
# COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# copy project
COPY ./src $APP_HOME

# copy entrypoint
COPY ./entrypoint.sh $APP_HOME
RUN chmod +x ${APP_HOME}/entrypoint.sh

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app

# run entrypoint.prod.sh
ENTRYPOINT ["./entrypoint.sh"]

EXPOSE 80

