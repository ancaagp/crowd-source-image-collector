FROM python:3.7-alpine

ARG aws_access_key
ARG aws_secret_key
ARG aws_region

# python output is transmitted directly to the terminal 
# without being buffered and that allows displaying the 
# application’s output in real-time
ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt /requirements.txt

RUN mkdir -p /root/.aws/
RUN echo "[default]\naws_access_key_id=${aws_access_key}\naws_secret_access_key = ${aws_secret_key}" >> /root/.aws/credentials
RUN echo "[default]\region=${aws_region}}\noutput = json" >> /root/.aws/config

RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \ 
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

RUN mkdir /image_collector
COPY ./image_collector /image_collector
WORKDIR /image_collector