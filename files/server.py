# coding=utf-8
from pyasiaocr import smart_reading
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
_log = None

INTERNAL_SERVER_ERROR = 500
class App(object):
    def __init__(self,config):
        self.business_name = 'meter/submit'
        self.count = 0
        self._init_config()
        self.config = config
        pass

    def _init_config(self):
        log.init(log.PROD)
        _log = log.get_log(self.business_name)


    def run(self):
        settings = dict()
        app = web.Application([('/'+self.business_name,TrainServerHandler,dict(app=self))],**settings)
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
    
class TrainServerHandler(web.RequestHandler):
    def initialize(self,app):
        self.app = app

    def post(self):    
        try:
            req_args = self._parse_arguments()
            result = self._read_meter(req_args['image'])
            self.write(errors.create_success(result['display'],result['confidence']))
            return
        except Exception as e:
            self.set_status(INTERNAL_SERVER_ERROR)
            self.write(errors.create_error(INTERNAL_SERVER_ERROR,'FAIL',e.message))
            return           

    def _read_meter(self,image):
        try:
            im = cv2.imread(image)
            
            # 这个是矫正参数， 不同摄像头不同，现在可以用默认这个
            calib_params = (0.960208, 0.245623, 37.7075, 80.1473, 9.04529, 1, 0.56, 0.5)
            fid = uuid.uuid1()
            tmpname = 'tmp'+str(fid)
            # 识别
            res, im = smart_reading(tmpname,im, 0.5, calib_params)
            res = res.split('\n')
        finally:
            os.remove(image)
        return {"display":res[0],"confidence":res[1]}

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
