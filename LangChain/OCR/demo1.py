import os
import sys

from RapidOCR_api import OcrAPI

ocrPath = '/RapidOCR-json.exe'
ocr = OcrAPI(ocrPath)
res = ocr.run('样例.png')

print('OCR识别结果：\n', res)
ocr.stop()
