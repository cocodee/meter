# base image conains the normal softwares
FROM index.qiniu.com/ataraxia/meterbase:v0.0.1
MAINTAINER cocodee <coco.dee@gmail.com>

COPY files/* /workspace/
RUN apt-get install -y libcv-dev
RUN apt-get install -y python-opencv  python-numpy vim
WORKDIR /workspace
CMD python ./server.py 
