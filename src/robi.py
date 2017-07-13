'''
This is the main-file for our RoboCup project
The Robo should search for 2 objects and bring it to
a special destination for each object
'''
from math import pi as PI
from naoqi import ALProxy
from optparse import OptionParser
import numpy as np
import cv2
import math

### CONSTANTS ###

#** Connection **#
#DEFAULT_NAO_IP = "nao3.local"
DEFAULT_NAO_IP = "10.0.7.16"
DEFAULT_NAO_PORT = 9559

#** sizes **#
CAM_ID_TOP = 0
CAM_ID_BOTTOM = 1
SIZE_AT_A_METER = 1190

#** for program **#
FELL_DOWN = -1

#** HSV **#
ORANGE_DOWN = np.array([10, 150, 150])
ORANGE_UP = np.array([15, 255, 255])

PINK_DOWN = np.array([300, 150, 150])
PINK_UP = np.array([320, 255, 255])

### GLOBAL VARIABLES ###

#** Proxys **#
ttsProxy = None
motionProxy = None
visionProxy = None


def getPictureFromOneCamera(colorDown, colorUp, cameraId):
        #get imagedata from top cam
        data = visionProxy.getBGR24Image(cameraId)
        image = np.fromstring(data, dtype=np.uint8).reshape((480, 640, 3))
        #cv2.imshow('image', image)
        hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        #search color
        mask = cv2.inRange(hsv_img, colorDown, colorUp)
        moments = cv2.moments(mask)
        area = moments['m00']
        return area, image, moments


def getBetterPicture(colorDown, colorUp):
        area0, image0, moments0 = getPictureFromOneCamera(visionProxy,
        colorDown, colorUp, CAM_ID_TOP)

        area1, image1, moments1 = getPictureFromOneCamera(visionProxy,
        colorDown, colorUp, CAM_ID_BOTTOM)

        if area0 > area1:
            return area0, image0, moments0
        else:
            return area1, image1, moments1


def searchForColor(colorDown, colorUp):
    detected = False
    dist = 0
    #Getting the picture with the bigger area of the color
    area, image, moments = getBetterPicture(visionProxy, colorDown, colorUp)

    while not(detected):

        cv2.imshow('image', image)

        if (area > 500000):
            # Searching for center (x,y) from object
            x = int(moments['m10'] / moments['m00'])
            y = int(moments['m01'] / moments['m00'])
            computedSize = math.sqrt(area)

            # calculate distance
            dist = SIZE_AT_A_METER / computedSize
            print "distance = ", dist

            # mark the object with an red circle
            rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            rect_image = cv2.rectangle(rgb_img,
            (x, y), (x + 50, y + 50), (0, 0, 255), 2)
            cv2.imshow('rec_image', rect_image)

            detected = True

        while 1:
            key = cv2.waitKey(5) & 0xFF
            if key == 27:
                break
        #turn to search in another direction
        if not detected:
            if(not moveTo(motionProxy, ttsProxy, 0, 0, PI / 16)):
                return FELL_DOWN

    return dist


def makeFotoOfQuadrat(imgTitle):
    # find quadrat
    data = visionProxy.getBGR24Image(CAM_ID_BOTTOM)
    image = np.fromstring(data,
    dtype=np.uint8).reshape((480, 640, 3))

    #show and write
    cv2.imshow('image', image)
    while 1:
        key = cv2.waitKey(5) & 0xFF
        if key == 27:
            break
    cv2.imwrite(imgTitle, image)


def searchColorAndTakeFoto(imgTitle, colorDown, colorUp):
    distance = FELL_DOWN

    while(distance > 0.2 or distance == FELL_DOWN):
        if(distance == FELL_DOWN):
            initMotion()
        distance = searchForColor(colorDown, colorUp)
        if(distance == FELL_DOWN):
            continue

        while(1):
            key = cv2.waitKey(5) & 0xFF
            if key == 27:
                break
        cv2.destroyAllWindows()

        ttsProxy.say("Found the orange square. moving to it.")
        distToWalk = distance / 2
        print "distance to walk =", distToWalk
        if(not moveTo(distToWalk, 0, 0)):
            distance = FELL_DOWN

    ttsProxy.say("I'm near enough to make the foto")
    makeFotoOfQuadrat(imgTitle)


def setHeadCentral():
    yawAngle = motionProxy.getAngles("HeadYaw", True)
    pitchAngle = motionProxy.getAngles("HeadPitch", True)
    motionProxy.changeHeadAngles(-1 * yawAngle, -1 * pitchAngle, 0.1)


def moveTo(x, y, theta):
    motionProxy.post.moveTo(x, y, theta)
    while(motionProxy.moveIsActive()):
        if(motionProxy.getPosture() == "Back" or
        motionProxy.getPosture("Belly")):
            ttsProxy.say("Damnit. Can anybody help me standing up?")
            return False
    return True


def initMotion():
    # Wake up robot
    motionProxy.setStiffnesses("Body", 1.0)
    motionProxy.wakeUp()

    #turn the head, so its looking straight forward
    setHeadCentral()

    # Send robot to Stand Init
    motionProxy.moveInit()


def main(pip, pport):
    '''
    ENTRY-POINT
    '''

    # Init Proxy's
    global ttsProxy
    ttsProxy = ALProxy("ALTextToSpeech", pip, pport)
    global motionProxy
    motionProxy = ALProxy("ALMotion", pip, pport)
    global visionProxy
    visionProxy = ALProxy("RobocupVision", pip, pport)

    initMotion()
    ttsProxy.say("Hello Masters.")

    ttsProxy.say("Going to search for the orange square.")
    searchColorAndTakeFoto("orange_object", ORANGE_DOWN, ORANGE_UP)

    ttsProxy.say("Going to search for the pink square.")
    searchColorAndTakeFoto("pink_object", PINK_DOWN, PINK_UP)

    ttsProxy.say("Finished my job. Goodbye")
    motionProxy.rest()


if __name__ == "__main__":
    # Parsing Commandlineparams
    parser = OptionParser()
    parser.add_option("--pip",
        help="Parent broker port. The IP address or your robot",
        dest="pip")
    parser.add_option("--pport",
        help="Parent broker port. The port NAOqi is listening to",
        dest="pport",
        type="int")
    parser.set_defaults(
        pip=DEFAULT_NAO_IP,
        pport=DEFAULT_NAO_PORT)

    (opts, args_) = parser.parse_args()
    pip = opts.pip
    pport = opts.pport
    main(pip, pport)