#!/bin/bash
while [ "$#" -lt "1" ]; do
    echo "provide at least 1 param"
    exit 1
done
imageName="$1"
echo "request with image:$imageName"
curl -X POST -F "image=@$imageName" http://61.153.154.178:8888/electric
