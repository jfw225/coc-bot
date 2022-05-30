import cv2
import mss
import pyautogui
import numpy as np

from time import sleep

from state import SharedVariables, State, FiniteStateMachine


class Shared(SharedVariables):
    def __init__(self):
        self.salvage_img = cv2.imread("data/salvage.png")
        self.inventory_img = cv2.imread("data/inventory.png")

        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]
        monitor_width, monitor_height = self.monitor["width"], self.monitor["height"]

        green = np.array([17, 248, 178])[::-1]
        self.green1 = green - 17
        self.green2 = green + 20

        white = np.array([255, 255, 255])[::-1]
        self.w1 = white - 30
        self.w2 = white

    def screenshot(self, window):
        return np.array(self.sct.grab(window))[:, :, :3]

    def find_object(self, image, obj):
        result = cv2.matchTemplate(obj, image, cv2.TM_SQDIFF)
        min_val, max_val, min_loc, _ = cv2.minMaxLoc(result)

        print(min_val, max_val, min_val/max_val)
        return min_val, max_val, min_loc


class OpenInventory(State):
    def __init__(self, shared: SharedVariables = ...):
        super().__init__(shared=shared)

        self.inventory_thresh = 0.05

    def transition(self, sh: SharedVariables):
        # check if inventory is open

        screen = sh.screenshot(sh.monitor)
        min_val, max_val, min_loc = sh.find_object(screen, sh.inventory_img)

        if min_val / max_val < self.inventory_thresh:
            return FindItemInfo

        pyautogui.press("tab")
        sleep(1)

        return OpenInventory


class FindItemInfo(State):
    def transition(self, sh: SharedVariables):
        # capture screen
        screen = sh.screenshot(sh.monitor)
        # make copy
        screen_copy = screen.copy()

        # convert to grayscale
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

        # apply a blur using the median filter
        screen = cv2.medianBlur(screen, 5)

        # finds the circles in the grayscale image using the Hough transform
        circles = cv2.HoughCircles(image=screen, method=cv2.HOUGH_GRADIENT, dp=0.9,
                                   minDist=80, param1=110, param2=39, maxRadius=70)

        for co, i in enumerate(circles[0, :].astype(np.int32), start=1):
            print(i[0])
            # draw the outer circle in green
            cv2.circle(screen_copy, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle in red
            cv2.circle(screen_copy, (i[0], i[1]), 2, (0, 0, 255), 3)

        # print the number of circles detected
        print("Number of circles detected:", co)

        cv2.imshow("out", screen_copy)
        cv2.waitKeyEx(1)

        return FindItemInfo


if __name__ == '__main__':
    shared = Shared()
    fsm = FiniteStateMachine(shared,
                             OpenInventory, FindItemInfo)
    fsm.run()
