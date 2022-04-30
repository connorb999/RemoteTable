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
#endpoint = '71.205.239.223:25565'
endpoint = 'localhost:25565'

# Connect to webcam
print("Connecting to webcam...")
cam_port = 0
cam = cv2.VideoCapture(cam_port + cv2.CAP_MSMF)
print("...webcam connected")

# Create the Window object of the control panel
window = tk.Tk()
#window.attributes('-fullscreen',True)
window.title('Remote Table Control Panel')


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
    

def cropImage(drawBox):
    try:
        top_crop = int(topCropEntryCam.get())
        bottom_crop = int(bottomCropEntryCam.get())
        right_crop = int(rightCropEntryCam.get())
        left_crop = int(leftCropEntryCam.get())
    except:
        print("Error parsing one of the crop params")
        return

    if(top_crop + bottom_crop > 100):
        print("Top/Bottom crops overlap")
        return
    if(left_crop + right_crop > 100):
        print("Left/Right crops overlap")
        return

    savedImg = cv2.imread("snapshot.png")

    # If all the crop params are 0, just copy the snapshot to cropped image
    if(top_crop == 0 & bottom_crop == 0 & right_crop == 0 & left_crop == 0):
        cv2.imwrite("croppedImg.png", savedImg)
        return

    height = int(savedImg.shape[0])
    width = int(savedImg.shape[1])
    top = int(height * top_crop / 100)
    bottom = int(height - (height * bottom_crop / 100))
    left = int(width * left_crop / 100)
    right = int(width - (height * right_crop / 100))

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


def handle_crop(event):
    print("Crop saved image...")
    cropImage(True)
    # set preview image
    img2 = tk.PhotoImage(file = "croppedImg.png")
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


def handle_launchGameWindow(event):
    print("*** Launching fullscreen... ***")


def handle_save(event):
    try:
        outFile = open("settings.txt", "w")
        
        # IP
        outFile.write("ip;")
        outFile.write(ipEntry.get())
        outFile.write("\n")
        # Crop - Top
        outFile.write("crop_top_cam;")
        outFile.write(topCropEntryCam.get())
        outFile.write("\n")
        # Crop - Bottom
        outFile.write("crop_bottom_cam;")
        outFile.write(bottomCropEntryCam.get())
        outFile.write("\n")
        # Crop - Left
        outFile.write("crop_left_cam;")
        outFile.write(leftCropEntryCam.get())
        outFile.write("\n")
        # Crop - Right
        outFile.write("crop_right_cam;")
        outFile.write(rightCropEntryCam.get())
        outFile.write("\n")
        # Crop - Top
        outFile.write("crop_top_proj;")
        outFile.write(topCropEntryProj.get())
        outFile.write("\n")
        # Crop - Bottom
        outFile.write("crop_bottom_proj;")
        outFile.write(bottomCropEntryProj.get())
        outFile.write("\n")
        # Crop - Left
        outFile.write("crop_left_proj;")
        outFile.write(leftCropEntryProj.get())
        outFile.write("\n")
        # Crop - Right
        outFile.write("crop_right_proj;")
        outFile.write(rightCropEntryProj.get())
        outFile.write("\n")
        # Board Width
        outFile.write("board_width;")
        outFile.write(boardWidthEntry.get())
        outFile.write("\n")
        # Board Height
        outFile.write("board_height;")
        outFile.write(boardHeightEntry.get())
        outFile.write("\n")

        outFile.close()
    except:
        #print("Error writing to file: " + filePath)
        errorStr = "Error writing to file: settings.txt"
        print(errorStr)
    

def loadSettings():
    print("Load settings...")
    inFile = open("settings.txt", "r")
    for line in inFile:
        try:
            currLine = line.split(';')
            if(currLine[0] == "ip"):
                ipEntry.delete(0, END)
                ipEntry.insert(0, currLine[1].strip('\n'))
            elif(currLine[0] == "crop_top_cam"):
                topCropEntryCam.delete(0, END)
                topCropEntryCam.insert(0, currLine[1].strip('\n'))
            elif(currLine[0] == "crop_bottom_cam"):
                bottomCropEntryCam.delete(0, END)
                bottomCropEntryCam.insert(0, currLine[1].strip('\n'))
            elif(currLine[0] == "crop_left_cam"):
                leftCropEntryCam.delete(0, END)
                leftCropEntryCam.insert(0, currLine[1].strip('\n'))
            elif(currLine[0] == "crop_right_cam"):
                rightCropEntryCam.delete(0, END)
                rightCropEntryCam.insert(0, currLine[1].strip('\n'))
            elif(currLine[0] == "crop_top_proj"):
                topCropEntryProj.delete(0, END)
                topCropEntryProj.insert(0, currLine[1].strip('\n'))
            elif(currLine[0] == "crop_bottom_proj"):
                bottomCropEntryProj.delete(0, END)
                bottomCropEntryProj.insert(0, currLine[1].strip('\n'))
            elif(currLine[0] == "crop_left_proj"):
                leftCropEntryProj.delete(0, END)
                leftCropEntryProj.insert(0, currLine[1].strip('\n'))
            elif(currLine[0] == "crop_right_proj"):
                rightCropEntryProj.delete(0, END)
                rightCropEntryProj.insert(0, currLine[1].strip('\n')) 
            elif(currLine[0] == "board_width_cam"):
                boardWidthEntry.delete(0, END)
                boardWidthEntry.insert(0, currLine[1].strip('\n'))
            elif(currLine[0] == "board_height_cam"):
                boardHeightEntry.delete(0, END)
                boardHeightEntry.insert(0, currLine[1].strip('\n'))
        except:
            print("skip line")

# ^^^ Functions
###########################################################
# vvv UI


# Image Preview
img = tk.PhotoImage(file = "snapshot.png")
imgLabel = tk.Label(window, image = img)
imgLabel.pack()

# IP adress input
ipLabel = tk.Label(text="Server IP (try 71.205.239.223:25565)")
ipLabel.pack()
ipEntry = tk.Entry()
ipEntry.insert(END, endpoint)
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

# Button to save settings
saveButton = tk.Button(
    text="Save Settings",
    width=25,
    height=2,
    bg="yellow",
    fg="green",
)
saveButton.pack()
saveButton.bind("<Button-1>", handle_save)

# Button launch game window
fullScreenButton = tk.Button(
    text="Launch Game Window",
    width=25,
    height=2,
    bg="purple",
    fg="yellow",
)
fullScreenButton.pack()
fullScreenButton.bind("<Button-1>", handle_launchGameWindow)

# Button to crop
cropButton = tk.Button(
    text="Crop",
    width=25,
    height=2,
    bg="violet",
    fg="yellow",
)
cropButton.pack()
cropButton.bind("<Button-1>", handle_crop)

# Crop controls
cropLabelCam = tk.Label(text="Camera crop percentages: Top, Bottom, Left, Right")
cropLabelCam.pack(padx=5, pady=10, side=tk.LEFT)
topCropEntryCam = tk.Entry(fg="red")
topCropEntryCam.insert(END, 15)
topCropEntryCam.pack(padx=5, pady=10, side=tk.LEFT)
bottomCropEntryCam = tk.Entry(fg="red")
bottomCropEntryCam.insert(END, 15)
bottomCropEntryCam.pack(padx=5, pady=10, side=tk.LEFT)
leftCropEntryCam = tk.Entry(fg="red")
leftCropEntryCam.insert(END, 15)
leftCropEntryCam.pack(padx=5, pady=10, side=tk.LEFT)
rightCropEntryCam = tk.Entry(fg="red")
rightCropEntryCam.insert(END, 15)
rightCropEntryCam.pack(padx=5, pady=10, side=tk.LEFT)
topCropEntryProj = tk.Entry(fg="blue")
topCropEntryProj.insert(END, 15)
topCropEntryProj.pack(padx=5, pady=10, side=tk.LEFT)
bottomCropEntryProj = tk.Entry(fg="blue")
bottomCropEntryProj.insert(END, 15)
bottomCropEntryProj.pack(padx=5, pady=10, side=tk.LEFT)
leftCropEntryProj = tk.Entry(fg="blue")
leftCropEntryProj.insert(END, 15)
leftCropEntryProj.pack(padx=5, pady=10, side=tk.LEFT)
rightCropEntryProj = tk.Entry(fg="blue")
rightCropEntryProj.insert(END, 15)
rightCropEntryProj.pack(padx=5, pady=10, side=tk.LEFT)



loadSettings()

# to respond to keyboard presses
# window.bind("<Key>", handle_keypress)

window.mainloop()
