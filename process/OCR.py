# -*- coding: utf-8 -*-
from aip import AipOcr
import io

class OCR:

    def __init__(self, appId, apiKey, secretKey):
        self.client = AipOcr(appId, apiKey, secretKey)

    def _pil2bin(self, pilObj):
        bin = io.BytesIO()
        pilObj.save(bin, format='JPEG')
        return bin.getvalue()

    def _ocr(self, img):
        imgBin = self._pil2bin(img)
        #return self.client.webImage(imgBin)  # 网络图片文字识别 1000次/月
        return self.client.basicGeneral(imgBin)           #通用文字识别（标准版）1000次/月
        #return self.client.general(imgBin)                  #通用文字识别（标准含位置）1000次/月
        #return self.client.basicAccurate(imgBin)        #通用文字识别（高精度版）1000次/月
        #return self.client.accurate(imgBin)             #通用文字识别（高精度含位置版）500次/月



    def run(self, quesImg, answImg):
        ques = self._ocr(quesImg)
        answ = self._ocr(answImg)
        ques = ''.join([item['words'] for item in ques['words_result']])
        answ = [item['words'] for item in answ['words_result']]

        return ques, answ

