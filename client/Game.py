from tkinter import *
import tkinter as tk
from turtle import window_height
import requests
import json
import time
import jsonpickle
import numpy as np
import cv2

frame_interval = 800

# Server Info
#endpoint = '71.205.239.223:5000'
#endpoint = '10.0.0.163:5000'
#endpoint = '71.205.239.223:25565'
#endpoint = "localhost:25565"
#crop_top = 0
#crop_bottom = 0
#crop_left = 0
#crop_right = 0

# Connect to webcam
print("Connecting to webcam...")
cam_port = 0
cam = cv2.VideoCapture(cam_port)
print("...webcam connected")

# Create the Window object of the control panel
window = tk.Tk()
#window.attributes('-fullscreen',True)
window.title('Remote Table')


# ^^^ Setup
###########################################################
# vvv Functions


def updateImage(imgFileName):
    img2 = tk.PhotoImage(file = imgFileName)
    imgLabel.configure(image = img2)
    imgLabel.image = img2


def takeWebcamPhoto():
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
    #updateImage("snapshot.png")

def handle_takeWebcamPhoto(event):
    takeWebcamPhoto()
    

def cropImage(drawBox):
    print("Cropping...")
    if(crop_top + crop_bottom > 100):
        print("Top/Bottom crops overlap")
        return
    if(crop_left + crop_right > 100):
        print("Left/Right crops overlap")
        return

    savedImg = cv2.imread("snapshot.png")

    # If all the crop params are 0, just copy the snapshot to cropped image
    if(crop_top == 0 & crop_bottom == 0 & crop_right == 0 & crop_left == 0):
        cv2.imwrite("croppedImg.png", savedImg)
        return

    height = int(savedImg.shape[0])
    width = int(savedImg.shape[1])
    top = int(height * crop_top / 100)
    bottom = int(height - (height * crop_bottom / 100))
    left = int(width * crop_left / 100)
    right = int(width - (height * crop_right / 100))

    if(drawBox):
        print("Draw box")
        start_point = (left,top)
        end_point = (right,bottom)
        color = (0,0,200)
        thickness = 1
        croppedImg = cv2.rectangle(savedImg, start_point, end_point, color, thickness)
    else:
        croppedImg = savedImg[top:bottom , left:right]
    
    cv2.imwrite("croppedImg.png", croppedImg)
    print("...Success")


def handle_serverResponse(response):
    print("handle server response...")
    response_decoded = jsonpickle.decode(response.text)
    img_decoded = cv2.imdecode(response_decoded, cv2.IMREAD_COLOR)
    cv2.imwrite("responseImg.png", img_decoded)

    # update the preview image
    #updateImage("responseImg.png")


def sendPhotoToServer():
    if(endpoint == ""):
        print("No IP entered")
        return

    # prepare headers for http request
    endpoint_url = 'http://' + endpoint + '/api/test'
    content_type = 'image/png'
    headers = {'content-type': content_type}

    img = cv2.imread("croppedImg.png")

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

def handle_sendPhotoToServer(event):
    sendPhotoToServer()


def resizeImg():
    savedImg = cv2.imread("responseImg.png")
    dsize = (newWidth, newHeight)
    resizeImg = cv2.resize(savedImg,dsize)
    cv2.imwrite("resizeImg.png", resizeImg)
    updateImage("resizeImg.png")


def handle_resize(event):
    eventWidth = int(event.width)
    eventHeight = int(event.height)

    savedImg = cv2.imread("croppedImg.png")
    oldHeight = int(savedImg.shape[0])
    oldWidth = int(savedImg.shape[1])

    eventAr = eventWidth/eventHeight
    imgAr = oldWidth/oldHeight
    global newHeight
    global newWidth
    if((eventAr/imgAr) > 1): #Window is wider than image (height limited)
        newHeight = eventHeight
        newWidth = eventWidth
        #newWidth = int(round(newHeight * imgAr))
    else: #Window is taller than image (width limited)
        newWidth = eventWidth
        newHeight = eventHeight
        #newHeight = int(round(newWidth / imgAr))


def loadSettings():
    print("Load settings...")
    inFile = open("settings.txt", "r")
    for line in inFile:
        try:
            currLine = line.split(';')
            if(currLine[0] == "ip"):
                global endpoint
                endpoint = currLine[1].strip('\n')
            elif(currLine[0] == "crop_top"):
                global crop_top
                crop_top = int(currLine[1].strip('\n'))
            elif(currLine[0] == "crop_bottom"):
                global crop_bottom
                crop_bottom = int(currLine[1].strip('\n'))
            elif(currLine[0] == "crop_left"):
                global crop_left
                crop_left = int(currLine[1].strip('\n'))
            elif(currLine[0] == "crop_right"):
                global crop_right
                crop_right = int(currLine[1].strip('\n'))
            elif(currLine[0] == "board_width"):
                global board_width
                board_width = int(currLine[1].strip('\n'))
            elif(currLine[0] == "board_height"):
                global board_height
                board_height = int(currLine[1].strip('\n'))
        except:
            print("skip line")
    print("...Settings Loaded:")
    print(endpoint)
    print(crop_top)
    print(crop_bottom)
    print(crop_left)
    print(crop_right)
    print(board_width)
    print(board_height)


def frame():
    print('frame')
    takeWebcamPhoto()
    cropImage(False)
    try:
        sendPhotoToServer()
    except:
        print("using latest image...")
    resizeImg()

    updateImage("resizeImg.png")
    window.after(frame_interval, frame)



# ^^^ Functions
###########################################################
# vvv UI


# Game Image
img = tk.PhotoImage(file = "snapshot.png")
imgLabel = tk.Label(window, image = img)
imgLabel.pack(fill=BOTH, expand=YES)


loadSettings()

# to respond to keyboard presses
# window.bind("<Key>", handle_keypress)
window.bind("<Configure>", handle_resize)
window.after(frame_interval, frame)
window.mainloop()
