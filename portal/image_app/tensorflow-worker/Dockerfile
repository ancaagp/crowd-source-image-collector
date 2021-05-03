FROM tensorflow/tensorflow:latest

ARG aws_access_key
ARG aws_secret_key
ARG aws_region

RUN mkdir -p /root/.aws/
RUN echo "[default]\naws_access_key_id=${aws_access_key}\naws_secret_access_key = ${aws_secret_key}" >> /root/.aws/credentials
RUN echo "[default]\region=${aws_region}}\noutput = json" >> /root/.aws/config

RUN pip3 install flask flask_shell2http
RUN pip3 --no-cache-dir install --upgrade awscli
RUN pip3 install argh
RUN pip3 install pillow

RUN mkdir /py
ADD train_model.py /py
ADD predict_model.py /py
ADD wsgi.py /py
WORKDIR /py
CMD flask run -p 4000 --host=0.0.0.0