# base image conains the normal softwares
FROM index.qiniu.com/ataraxia/meterbase:v0.0.2
MAINTAINER cocodee <coco.dee@gmail.com>

RUN apt-get install -y python-concurrent.futures
COPY files/* /workspace/
WORKDIR /workspace
CMD python ./server.py 
