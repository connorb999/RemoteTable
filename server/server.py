from flask import Flask, request, Response
import jsonpickle
import numpy as np
import cv2

# Initialize the Flask application
app = Flask(__name__)

# route http posts to this method
@app.route('/api/test', methods=['POST'])
def test():
    print("incoming request...")
    r = request
    #print(r.data)
    # convert string of image data to uint8
    #print(r.data)
    nparr = np.frombuffer(r.data, np.uint8)
    #print(nparr)
    # decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # do some fancy processing here....
    cv2.imwrite("test/test.png", img)

    flipImg = cv2.flip(img, 1)
    mergeImg = cv2.addWeighted(img, 0.5, flipImg, 0.5, 0)

    # encode image as png
    try:
        good, img_encoded = cv2.imencode('.png', mergeImg)
        if good != True:
            print("Image could not be encoded")
        #print(img_encoded.tobytes())
    except:
        print("Error encoding image")

    # build a response dict to send back to client
    #response = {'message': 'image received. size={}x{}'.format(img_encoded.shape[1], img_encoded.shape[0]) }
    response = img_encoded.tobytes()

    # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)

    print(img_encoded)

    print("...Success")
    return Response(response=response_pickled, status=200, mimetype="application/json")

# start flask app
app.run(host="0.0.0.0", port=5000)