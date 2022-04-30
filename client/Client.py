import tkinter as tk
from tkinter import ttk
from tkinter import *
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

# ^^^ Setup / Global Variables
###########################################################
# vvv Game Window

class GameWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry('300x100')
        self.title('Game Window')

        ttk.Button(self,
                text='Close',
                command=self.destroy).pack(expand=True)

        gameImg = tk.PhotoImage(file = "croppedImg.png")
        gameLabel = tk.Label(self, image = gameImg)
        gameLabel.pack()

# ^^^ Game Window
###########################################################
# vvv Control Window

class ControlWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry('300x200')
        self.title('Control Window')

        # Preview Image
        previewImg = tk.PhotoImage(file = "snapshot.png")
        previewImg = tk.Label(self, image = previewImg)
        previewImg.pack()

        # place a button on the root window
        ttk.Button(self,
                text='Launch Game Window',
                command=self.open_game_window).pack(expand=True)

    def open_game_window(self):
        gameWindow = GameWindow(self)
        gameWindow.grab_set()


if __name__ == "__main__":
    app = ControlWindow()
    app.mainloop()