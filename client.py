from __future__ import print_function
import requests
import json
import cv2

def bp(msg):
    print(msg)
    x = input()

#endpoint = '71.205.239.223:5000'
endpoint = 'localhost:5000'
test_url = 'http://' + endpoint + '/api/test'

# prepare headers for http request
content_type = 'image/jpg'
headers = {'content-type': content_type}

print("Loading Image... ")
img = cv2.imread("testImage.png")

# encode image as jpeg
_, img_encoded = cv2.imencode('.jpg', img)

# send http request with image and receive response
print("Sending Image... ")
response = requests.post(test_url, data=img_encoded.tobytes(), headers=headers)
# decode response
print(json.loads(response.text))

# expected output: {u'message': u'image received. size=132x136'}
bp("press ENTER to close...")