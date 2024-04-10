FROM ubuntu:22.04

LABEL maintainer="Devin <zhengdevin11@gmail.com>"

USER root

ENV DEBIAN_FRONTEND noninteractive

# 定义编码
ENV LC_ALL="C.UTF-8"
ENV LANG="C.UTF-8"

WORKDIR /opt

RUN apt-get update && apt-get install -y python3

COPY wsgi.zip /opt

CMD ["python3", "/opt/wsgi.zip"]
