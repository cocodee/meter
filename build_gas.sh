#!/bin/bash
while [ "$#" -lt "1" ]; do
    echo "provide at least 1 param"
    exit 1
done
image_version="$1"
docker build -t  index.qiniu.com/ataraxia/meter:$image_version -f Dockerfile .

docker run -i -t -p 8888:8888 index.qiniu.com/ataraxia/meter:$image_version /bin/bash
