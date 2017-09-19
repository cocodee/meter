# coding=utf-8
from pyasiaocr import smart_reading_analog_electric
import cv2
import sys

if __name__ == '__main__':
    if len(sys.argv)<2:
        print 'invalid param'
    
    im = cv2.imread(sys.argv[1])

    # 这个是矫正参数， 不同摄像头不同，现在可以用默认这个
     
    calib_params = (0.960208, 0.245623, 37.7075, 80.1473, 9.04529, -1, 0.56, 0.5)

    # 识别
    print 'reading'
    res, im = smart_reading_analog_electric("a", im, ((0, 0), (im.shape[1], im.shape[0])), 8, 0.6)
    res = res.split('\n')
    print 'reading complete'
    print 'result:',  res[0]
    print 'confidence:',  res[1]
    print im
    #cv2.imshow('disp', im)
    #cv2.waitKey(0)
