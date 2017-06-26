# coding=utf-8
from pyasiaocr import smart_reading_analog_electric
import cv2

if __name__ == '__main__':
    im = cv2.imread('T1AaETB7Ev1RCvBVdK.jpg')


    # 识别
    res, im = smart_reading_analog_electric("test",im, ((48, 65), (200, 55)),6,0.4)
    res = res.split('\n')

    print 'result:',  res[0]
    print 'confidence:',  res[1]
    print im
    #cv2.imshow('disp', im)
    #cv2.waitKey(0)
