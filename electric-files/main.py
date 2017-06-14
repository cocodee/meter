# coding=utf-8
from pyasiaocr import smart_reading
import cv2

if __name__ == '__main__':
    im = cv2.imread('10000004_22_20170115203356.jpg')

    # 这个是矫正参数， 不同摄像头不同，现在可以用默认这个
    calib_params = (0.960208, 0.245623, 37.7075, 80.1473, 9.04529, 1, 0.56, 0.5)

    # 识别
    res, im = smart_reading(im, 0.5, calib_params)
    res = res.split('\n')

    print 'result:',  res[0]
    print 'confidence:',  res[1]
    print im
    #cv2.imshow('disp', im)
    #cv2.waitKey(0)
