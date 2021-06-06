import argparse
import openfoodfacts
from PIL import Image
import requests
from io import BytesIO
import pytesseract
import numpy as np
import skimage
from skimage import io

def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def removeNoise(image):
    return cv2.medianBlur(image,5)

def thresHold(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def dilate(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.dilate(image, kernel, iterations = 1)

def erode(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.erode(image, kernel, iterations = 1)

def canny(image):
    return cv2.Canny(image, 100, 200)

def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def preProcess(inImage):
    img = cv2.imread(inImage)
    grayImage = grayscale(img)
    noiseless = removeNoise(grayImage)
    thresh = thresHold(noiseless)
    dilated = dilate(thresh)
    eroded = erode(dilated)
    canny = canny(eroded)
    opened = opening(canny)
    deskewed =   (opened)
    return deskewed


def main():
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    ap = argparse.ArgumentParser()
    ap.add_argument("-i","--image",required=True,help="Path to input image")
    args=vars(ap.parse_args())

    image=cv2.imread(args["image"])

    barcodes=pyzbar.decode(image)

    for barcode in barcodes:
        barcodeData=barcode.data.decode("utf-8")
        barcodeType=barcode.type

    product = openfoodfacts.products.get_product(barcodeData)

    for items in product['product']:
        print(items)

    print(product['product']['product_name'])
    print(str(product['product']['nutriments']['energy-kcal_100g']) + " kcal per 100g")


    response = requests.get(str(product['product']['image_ingredients_url']))
    inImage = Image.open(BytesIO(response.content))
    inImage.show()
    inImage = io.imread(inImage)

    inImage = preProcess(inImage)
    inImage.show()
    print(pytesseract.image_to_string(inImage))


main()
