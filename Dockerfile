# base image conains the normal softwares
FROM index.qiniu.com/ataraxia/pyspark-base:v0.0.4
MAINTAINER cocodee <coco.dee@gmail.com>

RUN apt-get install -y libboost-dev libboost-thread-dev libboost-system-dev libboost-python-dev libjsoncpp-dev libcurl4-openssl-dev

RUN apt-get install -y wget
RUN pip install tornado --index-url https://pypi.tuna.tsinghua.edu.cn/simple
COPY files/* /workspace/

WORKDIR /workspace
CMD python ./server.py 
