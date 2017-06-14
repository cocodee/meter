# coding=utf-8
import logging
import signal
from tornado import ioloop,web
from tornado.options import define,options,parse_command_line
from tornado import gen, httpclient, concurrent, escape
import threading
import log
import errors
import time
import uuid
import os
import requests
import json
_log = None

INTERNAL_SERVER_ERROR = 500
class App(object):
    def __init__(self,config):
        self.business_name = 'blue'
        self.count = 0
        self._init_config()
        self.config = config
        pass

    def _init_config(self):
        log.init(log.PROD)
        _log = log.get_log(self.business_name)


    def run(self):
        settings = dict()
        app = web.Application([('/'+self.business_name,TrainServerHandler,dict(app=self)),('/bluepull',PullHandler,dict(app=self))],**settings)
        app.listen(self.config['port'])
        self.__init_signal(app)
        ioloop.IOLoop.current().start()

    def __init_signal(self,app):
        def _int_handler(signum, frame):
            _log.info('receive signal %d', signum)
            app.close()
    
        def _eval_close(sn, f):
            _log.error('eval process exit unexpect')
            app.close_loop()
    
        signal.signal(signal.SIGINT, _int_handler)
        signal.signal(signal.SIGHUP, _eval_close)

class PullHandler(web.RequestHandler):
    def initialize(self,app):
        self.app = app

    def post(self):    
        try:
            req_args = self._parse_arguments()
            result = self._read_meter(req_args['image'])
            self.set_header("Content-Type","Content-Type: text/html; charset=utf-8")
            self.write(json.dumps(result,ensure_ascii=False))
            return
        except Exception as e:
            self.set_status(INTERNAL_SERVER_ERROR)
            self.set_header("Content-Type","Content-Type: text/html; charset=utf-8")
            self.write(errors.create_error(INTERNAL_SERVER_ERROR,'FAIL',e.message))
            return           

    def _read_meter(self,image):
        res = {}
        try:
            res = self.blue(image)
        except Exception as e:
            print(e)
            res = {'code':500,'err':'failed'}
        finally:
            os.remove(image)
        return res

    def blue(self,f):
        url = "http://a2.lightbox.pub/api/test/json/blue"
        files = {'file':open(f,'rb')}
        data = {'user':'qiniu','token':'80b2f6f52d386d30b161dda40aab0421'}
        try:
            r = requests.post(url,files=files,data=data)
        except Exception as e:
            return {'code':500,'err':'failed'}
        if not r.status_code == requests.codes.ok:
            return {'code':500,'err':'failed'}
        else:
            j = json.loads(r.text)
            j['code']=200
            return j

    def _parse_arguments(self):
        req = self.request
        image = self.get_argument("image")
        tempfilename = self._create_tempfilename()
        response=requests.get(image,timeout=5)
        with open(tempfilename,'w') as fout:
            fout.write(response.content)
        return {"image":tempfilename}

    def _create_tempfilename(self):
        id = uuid.uuid1()
        temp_name = 'meter_'+str(id)
        return temp_name
   
class TrainServerHandler(web.RequestHandler):
    def initialize(self,app):
        self.app = app

    def post(self):    
        try:
            req_args = self._parse_arguments()
            result = self._read_meter(req_args['image'])
            self.set_header("Content-Type","Content-Type: text/html; charset=utf-8")
            self.write(json.dumps(result,ensure_ascii=False))
            return
        except Exception as e:
            self.set_status(INTERNAL_SERVER_ERROR)
            self.set_header("Content-Type","Content-Type: text/html; charset=utf-8")
            self.write(errors.create_error(INTERNAL_SERVER_ERROR,'FAIL',e.message))
            return           

    def _read_meter(self,image):
        res = {}
        try:
            res = self.blue(image)
        except Exception as e:
            print(e)
            res = {'code':500,'err':'failed'}
        finally:
            os.remove(image)
        return res

    def blue(self,f):
        url = "http://a2.lightbox.pub/api/test/json/blue"
        files = {'file':open(f,'rb')}
        data = {'user':'qiniu','token':'80b2f6f52d386d30b161dda40aab0421'}
        try:
            r = requests.post(url,files=files,data=data)
        except Exception as e:
            return {'code':500,'err':'failed'}
        if not r.status_code == requests.codes.ok:
            return {'code':500,'err':'failed'}
        else:
            j = json.loads(r.text)
            j['code']=200
            return j

    def _parse_arguments(self):
        req = self.request
        images = self.request.files.get('image')
        if not (images!=None and len(images)>0):
            raise Exception('no image attached')
            return
        tempfilename = self._create_tempfilename()
        with open(tempfilename,'w') as fout:
            fout.write(images[0]['body'])
        return {"image":tempfilename}

    def _create_tempfilename(self):
        id = uuid.uuid1()
        temp_name = 'meter_'+str(id)
        return temp_name
def main():
    args = parse_command_line()
    config={'port':8888}
    app = App(config)
    app.run()

if __name__ == '__main__':
    main()
