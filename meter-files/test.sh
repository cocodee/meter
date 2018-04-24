#!/bin/bash
while [ "$#" -lt "2" ]; do
    echo "provide at least 1 param"
    exit 1
done
action="$1"
imageName="$2"
echo $action
if [ $action = "a" ]; then
echo a
curl -X POST -F "image=@$imageName" http://61.153.154.143:8888/analog-electric
elif [ $action = "e" ]; then
echo e
curl -X POST -F "image=@$imageName" http://61.153.154.143:8888/electric
elif [ $action = "g" ]; then
echo g
curl -X POST -F "image=@$imageName" http://61.153.154.143:8888/meter/submit?digits=7
fi

echo 'done'
sleep 1

