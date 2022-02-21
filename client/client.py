from __future__ import print_function
import requests
import json
import cv2

def bp(msg):
    print(msg)
    x = input()

#endpoint = '71.205.239.223:5000'
#endpoint = '10.0.0.163:5000'
endpoint = 'localhost:5000'
test_url = 'http://' + endpoint + '/api/test'

# prepare headers for http request
content_type = 'image/jpg'
headers = {'content-type': content_type}

print("Loading Image... ")
img = cv2.imread("hoe.png")

# encode image as jpeg
try:
    _, img_encoded = cv2.imencode('.jpg', img)
except:
    bp("error encoding image")

# send http request with image and receive response
print("Sending Image... ")
try:
    response = requests.post(test_url, data=img_encoded.tobytes(), headers=headers)

    # decode response
    print(json.loads(response.text))
    bp("press ENTER to close...")
except:
    bp("Unexpected server error...")

# expected output: {u'message': u'image received. size=132x136'}