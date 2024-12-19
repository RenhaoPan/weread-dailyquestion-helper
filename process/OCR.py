# -*- coding: utf-8 -*-
from aip import AipOcr
from paddleocr import PaddleOCR
import io

class OCR:

    def __init__(self, mode, appId=None, apiKey=None, secretKey=None):
        self.mode = mode
        if mode == 'paddle':
            self.client = PaddleOCR(lang='ch', show_log=False)# need to run only once to load model into memory
        elif mode == 'baidu':
            self.client = AipOcr(appId, apiKey, secretKey)

    def _pil2bin(self, pilObj):
        bin = io.BytesIO()
        pilObj.save(bin, format='JPEG')
        return bin.getvalue()

    def _ocr(self, img):

        imgBin = self._pil2bin(img)
        if self.mode == 'baidu':
            # 百度OCR
            # #return self.client.webImage(imgBin)  # 网络图片文字识别 1000次/月
            return self.client.basicGeneral(imgBin)           #通用文字识别（标准版）1000次/月
            # #return self.client.general(imgBin)                  #通用文字识别（标准含位置）1000次/月
            # #return self.client.basicAccurate(imgBin)        #通用文字识别（高精度版）1000次/月
            # #return self.client.accurate(imgBin)             #通用文字识别（高精度含位置版）500次/月
        elif self.mode == 'paddle':
            # paddle OCR
            result = self.client.ocr(img, cls=False)
            res = []
            for idx in range(len(result)):
                for line in result[idx]:
                    res.append(line[-1])
            return res


    def run(self, quesImg, answImg):
        ques = self._ocr(quesImg)
        answ = self._ocr(answImg)
        if self.mode == 'baidu':
            ques = ''.join([item['words'] for item in ques['words_result']])
            answ = [item['words'] for item in answ['words_result']]
        elif self.mode == 'paddle':
            ques = ''.join([str(item[0]) for item in ques])
            answ = [item[0] for item in answ]
        return ques, answ

if __name__ == '__main__':
    ocr = PaddleOCR(lang='ch', show_log=False)
    for i in range(1, 10):
        img_path = f'../img/test{i}.png'
        result = ocr.ocr(img_path, cls=False)
        # print(result)
        res = []
        for idx in range(len(result)):
            for line in result[idx]:
                res.append(line[-1])
        ques = ''.join([str(item[0]) for item in res])
        answ = [item[0] for item in res]
        print(ques)
        # print(answ)


