#!/bin/bash
while [ "$#" -lt "1" ]; do
    echo "provide at least 1 param"
    exit 1
done
imageName="$1"   
curl -X POST -F "image=@$imageName" http://127.0.0.1:8888/analog-electric 

