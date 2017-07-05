# base image conains the normal softwares
FROM index.qiniu.com/ataraxia/meterbase:v0.0.1
MAINTAINER cocodee <coco.dee@gmail.com>

COPY files/* /workspace/
RUN sed -i s/archive.ubuntu.com/mirrors.163.com/g /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y libcv-dev
RUN apt-get install -y python-opencv  python-numpy vim
RUN pip install requests --index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install qiniu
WORKDIR /workspace
CMD python ./server.py 
