from tkinter import *
import tkinter as tk
import requests
import json
import jsonpickle
import numpy as np
import cv2

# Server Info
#endpoint = '71.205.239.223:5000'
#endpoint = '10.0.0.163:5000'
endpoint = 'localhost:5000'

# Connect to webcam
print("Connecting to webcam...")
cam_port = 0
cam = cv2.VideoCapture(cam_port)
print("...webcam connected")


# ^^^ Setup
###########################################################
# vvv Functions


def handle_takeWebcamPhoto(event):
    print("Taking snapshot...")
    # read the input using the camera
    result, image = cam.read()  

    # If the image was successfully read, update the saved file
    if result:
        cv2.imwrite("snapshot.png", image)
        print("...Success   (saved in 'snapshot.png')")
    else:
        print("Failed to grab frame from webcam")
        return

    # update the preview image
    img2 = tk.PhotoImage(file = "snapshot.png")
    imgLabel.configure(image = img2)
    imgLabel.image = img2
    

def handle_serverResponse(response):
    print("handle server response...")
    response_decoded = jsonpickle.decode(response.text)
    img_decoded = cv2.imdecode(response_decoded, cv2.IMREAD_COLOR)
    cv2.imwrite("responseImg.png", img_decoded)

    # update the preview image
    img2 = tk.PhotoImage(file = "responseImg.png")
    imgLabel.configure(image = img2)
    imgLabel.image = img2


def handle_sendPhotoToServer(event):
    if(ipEntry.get() == ""):
        print("No IP entered")
        return

    # prepare headers for http request
    endpoint_url = 'http://' + ipEntry.get() + '/api/test'
    content_type = 'image/png'
    headers = {'content-type': content_type}

    img = cv2.imread("snapshot.png")

    # encode image as png
    try:
        good, img_encoded = cv2.imencode('.png', img)
        if good != True:
            print("Image could not be encoded")
    except:
        print("Error encoding image")

    # send http request with image and receive response
    try:
        print("Send image...")
        response = requests.post(endpoint_url, data=img_encoded.tobytes(), headers=headers)
    except:
        print("Unexpected server error...")
        return
    handle_serverResponse(response)


# ^^^ Functions
###########################################################
# vvv UI


window = tk.Tk()
window.title('Remote Table Control Panel')

# Image Preview
img = tk.PhotoImage(file = "snapshot.png")
imgLabel = tk.Label(window, image = img)
imgLabel.pack()

# IP adress input
ipLabel = tk.Label(text="Server IP (try 71.205.239.223:5000) >localhost:5000<")
ipLabel.pack()
ipEntry = tk.Entry()
ipEntry.pack()

# Button to take a webcam photo
takePhotoButton = tk.Button(
    text="Take Webcam Photo",
    width=25,
    height=2,
    bg="blue",
    fg="yellow",
)
takePhotoButton.pack()
takePhotoButton.bind("<Button-1>", handle_takeWebcamPhoto)

# Button to send photo to the server
sendImageButton = tk.Button(
    text="Send photo to server",
    width=25,
    height=2,
    bg="green",
    fg="yellow",
)
sendImageButton.pack()
sendImageButton.bind("<Button-1>", handle_sendPhotoToServer)


# to respond to keyboard presses
# window.bind("<Key>", handle_keypress)
window.mainloop()