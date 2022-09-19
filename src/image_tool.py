import numpy
import cv2


class ImageTool:
    @staticmethod
    def cmpimg(pic1, pic2):
        pic1 = cv2.imread(pic1, cv2.IMREAD_GRAYSCALE)
        pic2 = cv2.imread(pic2, cv2.IMREAD_GRAYSCALE)
        return (pic1 == pic2).mean()

