# coding=utf-8
from pyasiaocr import smart_reading_analog_electric
from pyasiaocr import smart_reading_elec_meter
from pyasiaocr import set_domain
import cv2

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
import ConfigParser
from StorageApi import QiniuStorage
from uuid import uuid1
import multiprocessing
from datetime import datetime
import tornado
from tornado.concurrent import run_on_executor
# 这个并发库在python3自带在python2需要安装sudo pip install futures
from concurrent.futures import ThreadPoolExecutor
import monitor

_log=None

INTERNAL_SERVER_ERROR = 500
class App(object):
    def __init__(self,config,q_in):
        self.count = 0
        self._init_config()
        self.config = config
        self.q_in = q_in
        set_domain('http://yon4rccs.nq.cloudappl.com')
        pass

    def _init_config(self):
        log.init(log.PROD)
        _log = log.get_log("meter server")
        _log.info("test")


    def run(self):
        settings = dict()
        app = web.Application([('/analog-electric',AnalogElectricServerHandler,dict(app=self)),
                               ('/electric',ElectricServerHandler,dict(app=self)),
                               ('/meter/submit',GasServerHandler,dict(app=self)),],**settings)
        monitor.init(app)
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
    
def parse_arguments(request):
    req = request.request
    images = req.files.get('image')
    if not (images!=None and len(images)>0):
        raise Exception('no image attached')
        return
    tempfilename = create_tempfilename()
    with open(tempfilename,'w') as fout:
        fout.write(images[0]['body'])
    digitstr= request.get_argument('digits','0')
    digits = int(digitstr)
    return {"image":tempfilename,"digits":digits}

def create_tempfilename():
    id = uuid.uuid1()
    temp_name = 'meter_'+str(id)
    return temp_name

class AnalogElectricServerHandler(web.RequestHandler):
    executor = ThreadPoolExecutor(4)

    def initialize(self,app):
        self.app = app
        self.handlerlog = log.get_log("analog_electric_handler")
        self.bucket = "meter-analog-electric"

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):    
        try:
            monitor.http_request_total(self.bucket,"post")
            self.handlerlog.info("begin request")
            req_args = parse_arguments(self)
            result = yield self._read_meter(req_args['image'],req_args['digits'])
            self.write(errors.create_success(result['display'],result['confidence']))
            return
        except Exception as e:
            monitor.http_request_failure_total(self.bucket)
            self.handlerlog.error(e)
            self.set_status(INTERNAL_SERVER_ERROR)
            self.write(errors.create_error(INTERNAL_SERVER_ERROR,'FAIL',e.message))
            return           

    @run_on_executor
    def _read_meter(self,image,digits):
        try:
            im = cv2.imread(image)
            
            fid = uuid.uuid1()
            tmpname = 'tmp'+str(fid)
            # 识别
            if digits==0:
                digits=6
            res, im = smart_reading_analog_electric("a", im, ((0, 0), (im.shape[1], im.shape[0])), digits, 0.6)
            if "error" in res:
                raise Exception("service error.")
            res = res.split('\n')
            self.handlerlog.info("res from aisainfo")
            self.handlerlog.info(res)
            if len(res)<2:
                raise Exception("service return length less than 2")
        except Exception as e:
            monitor.http_request_failure_total(self.bucket)
            self.handlerlog.error(e)
            res = ["0","0 "]
        finally:
            try:
                self.app.q_in.put_nowait((self.bucket,image))
            except:
                os.remove(image)
         
        display_str = res[0]
        if display_str<>None and display_str<>'':
            d1 = display_str.split(' ')
            d2 = map(lambda x:x.strip(),d1)
            d3 = filter(lambda x:x<>'',d2)
            d4 = map(lambda x:x if x.find('/')==-1 else x[0],d3)
            display = ''.join(d4)
        if len(display)>digits:
            display = display[0:digits]

        confidence_str = res[1]
        confidence = get_confidence(confidence_str)

        self.handlerlog.info("complete request")
        return {"display":display,"confidence":str(confidence)}

class ElectricServerHandler(web.RequestHandler):
    executor = ThreadPoolExecutor(4)

    def initialize(self,app):
        self.app = app
        self.bucket = "meter-electric"
        self.handlerlog = log.get_log("electric_handler")

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):    
        try:
            monitor.http_request_total(self.bucket,"post")
            req_args = parse_arguments(self)
            result = yield self._read_meter(req_args['image'])
            self.write(errors.create_success_type(result['display'],result['confidence'],result["type"]))
            return
        except Exception as e:
            monitor.http_request_failure_total(self.bucket)
            self.set_status(INTERNAL_SERVER_ERROR)
            self.write(errors.create_error(INTERNAL_SERVER_ERROR,'FAIL',e.message))
            return           

    @run_on_executor
    def _read_meter(self,image):
        try:
            im = cv2.imread(image)
            
            fid = uuid.uuid1()
            tmpname = 'tmp'+str(fid)
            # 识别
            res, im = smart_reading_elec_meter(tmpname,im, 0.5)
            if "error" in res:
                raise Exception("service error.")
            if "error" in res:
                raise Exception("service error.")
            res = res.split('\n')
            self.handlerlog.info("res from aisainfo")
            self.handlerlog.info(res)
            if len(res)<2:
                raise Exception("service return length less than 2")
        except Exception as e:
            print(e)
            monitor.http_request_failure_total(self.bucket)
            res = ["0","0"]
        finally:
            print('put '+image)
            try:
                self.app.q_in.put_nowait((self.bucket,image))
            except:
                os.remove(image)

        print(res)
        display_str = res[0]
        if display_str<>None and display_str<>'':
            d1 = display_str.split(' ')
            print(d1)
            d2 = map(lambda x:x.strip(),d1)
            d3 = filter(lambda x:x<>''and x<>'D' and x<>'T' and x<>'E',d2)
            #d4 = map(lambda x:x if x.find('/')==-1 else x[0],d3)
            print(d3)
            display = ''.join(d3)
        else:
            display = '0'
        confidence_str = res[1]
        confidence = get_confidence(confidence_str)

        typ = 0
        if display_str.find("E")>=0 :
            typ = 1
        if display_str.find("T")>=0 :
            typ = 2
        if display_str.find("D")>=0 :
            typ = 2 
        return {"display":display,"confidence":str(confidence),"type":typ}


class GasServerHandler(web.RequestHandler):
    executor = ThreadPoolExecutor(4)

    def initialize(self,app):
        self.app = app
        self.bucket = "gas-meter"
        self.handlerlog = log.get_log("gas_handler")
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):    
        try:
            monitor.http_request_total(self.bucket,"post")
            req_args = parse_arguments(self)
            result = yield self._read_meter(req_args['image'],req_args['digits'])
            self.write(errors.create_success(result['display'],result['confidence']))
            return
        except Exception as e:
            monitor.http_request_failure_total(self.bucket)
            self.set_status(INTERNAL_SERVER_ERROR)
            self.write(errors.create_error(INTERNAL_SERVER_ERROR,'FAIL',e.message))
            return           

    @run_on_executor
    def _read_meter(self,image,digits):
        try:
            im = cv2.imread(image)
            
            fid = uuid.uuid1()
            tmpname = 'tmp'+str(fid)
            # 识别
            if digits==0:
                digits = 8
            res, im = smart_reading_analog_electric("a", im, ((0, 0), (im.shape[1], im.shape[0])), digits, 0.6)
            if "error" in res:
                raise Exception("service error.")
            res = res.split('\n')
        except Exception as e:
            monitor.http_request_failure_total(self.bucket)
            res = ["0","0 "]
        finally:
            print('put '+image)
            try:
                self.app.q_in.put_nowait((self.bucket,image))
            except:
                os.remove(image)

        display_str = res[0]
        if display_str<>None and display_str<>'':
            d1 = display_str.split(' ')
            d2 = map(lambda x:x.strip(),d1)
            d3 = filter(lambda x:x<>'',d2)
            d4 = map(lambda x:x if x.find('/')==-1 else x[0],d3)
            display = ''.join(d4)
        if len(display)>digits:
            display = display[0:digits]

        confidence_str = res[1]
        confidence = get_confidence(confidence_str)

        return {"display":display,"confidence":str(confidence)}

def get_confidence(confidence_str):
    confidence=0
    if confidence_str<>None and confidence_str<>'':
        a1 = confidence_str.split(' ')
        a2 = map(lambda x:x.strip(),a1)
        a3 = filter(lambda x:x<>'' and x<>'0',a2)
        a4 = map(lambda x:float(x),a3)
        a5 = filter(lambda x:x>0.001,a4)
        if len(a4)>0:
            confidence = min(a5)
    if confidence<0.0001:
        confidence=int(confidence)
    return confidence

def main(config):
    log.init(log.PROD)
    mainlog = log.get_log("gas-main")
    args = parse_command_line()
    qapi = QiniuStorage(config["ak"],config["sk"])
    queue = multiprocessing.Queue(1000)
    uploadProcess = multiprocessing.Process(target=upload,args=(qapi,queue,mainlog))
    uploadProcess.start()

    app = App(config,queue)
    app.run()
    queue.close()
    uploadProcess.join()

def upload(qapi,q_in,mainlog):
    while True:
        bucket_image = q_in.get()
        bucket = bucket_image[0]
        file_name = bucket_image[1]
        mainlog.info("get %s",file_name)
        if file_name is None:
            break
        id = uuid1()
        now = datetime.now()
        key = now.strftime("%Y-%m-%d")+"/"+bucket+"/"+file_name+"/"+str(id)+".jpg"
        ret = qapi.upload(bucket,key,file_name)
        if ret =="fail":
            mainlog.error('upload file failed')
        os.remove(file_name)

if __name__ == '__main__':
    cf = ConfigParser.ConfigParser()
    cf.read("./cf.ini")
    ak = cf.get("secret","ak")
    sk = cf.get("secret","sk")
    port = cf.get("web","port")
    config = {
        "port":int(port),
        "ak":ak,
        "sk":sk
    }
    print(config)
    main(config)
