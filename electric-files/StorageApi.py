# -*- coding: utf-8 -*-
# linyining@mail.qiniu.com


import requests
from qiniu import Auth, put_file, etag, urlsafe_base64_encode, BucketManager

AK = 'xxxxxyyyyyyyyx'
SK = 'xxxxxyyyyyyyyx'

class QiniuStorage:
    def __init__(self, ak = AK, sk = SK):
        self.q_access = Auth(ak, sk)
    
    def create_bucket(self):
        print "not implemented"


    def download(self, bucket_domain, key, donwloaded_filename, expires=3600):
        base_url = 'http://%s/%s' % (bucket_domain, key)
        private_url = self.q_access.private_download_url(base_url, expires)
        r = requests.get(private_url)
        assert r.status_code == 200
        if r.status_code == 200:
            with open(donwloaded_filename, "wb") as f:
                f.write(r.content)
            return "success"
        else:
            return "fail"

    def upload(self, bucket_name, key, localfile, expires=3600):
        token = self.q_access.upload_token(bucket_name, key, expires)
        ret, info = put_file(token, key, localfile)
        if ret['key'] == key and ret['hash'] == etag(localfile):
            return "success"
        else:
            return "fail"

    def fetch_url_to_bucket(self, url, bucket_name, key):
        bucket = BucketManager(self.q_access)
        ret, info = bucket.fetch( url, bucket_name, key)
        #print(info)
        if ret['key'] == key:
            return "success"
        else:
            return "fail"


if __name__ == '__main__':
    qapi = QiniuStorage()
    url = "http://a.hiphotos.baidu.com/image/pic/item/e7cd7b899e510fb3a78c787fdd33c895d0430c44.jpg"
    bucket_name = "data"
    bucket_domain = "o9d987omi.qnssl.com"
    key = "beau.jpg"
    new_key = "beauty.jpg"
    ret = qapi.fetch_url_to_bucket(url, bucket_name, key)
    print "fetch ", ret
    ret = qapi.dowonload(bucket_domain, key, new_key)
    print "dowonload ", ret
    ret = qapi.upload(bucket_name, new_key, newkey)
    print "upload ", ret
    