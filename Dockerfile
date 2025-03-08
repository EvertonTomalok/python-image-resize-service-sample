FROM python:3.8

ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV DB_ENVIRONMENT=PRODUCTION

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ADD . .

RUN make setup
