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
DEFAULT_NAO_IP = "10.0.7.14"
DEFAULT_NAO_PORT = 9559

#** sizes **#
CAM_ID_TOP = 0
CAM_ID_BOTTOM = 1
SIZE_AT_A_METER = 1190

#** for program **#
FELL_DOWN = -1

#** HSV **#
ORANGE_DOWN = np.array([10, 150, 150])
ORANGE_UP = np.array([20, 255, 255])

PINK_DOWN = np.array([150, 100, 100])
PINK_UP = np.array([200, 255, 255])

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
        return area, image, moments, mask


def getBetterPicture(colorDown, colorUp):
        area0, image0, moments0, mask0 = getPictureFromOneCamera(colorDown, colorUp, CAM_ID_TOP)

        area1, image1, moments1, mask1 = getPictureFromOneCamera(colorDown, colorUp, CAM_ID_BOTTOM)

        if area0 > area1:
            return area0, image0, moments0, mask0
        else:
            return area1, image1, moments1, mask1


def searchForColor(colorDown, colorUp):
    detected = False
    dist = 0

    while not(detected):

        # Getting the picture with the bigger area of the color
        area, image, moments, mask = getBetterPicture(colorDown, colorUp)

        #cv2.imshow('image', image)
        #cv2.imshow('mask', mask)
        #while 1:
        #    key = cv2.waitKey(5) & 0xFF
        #    if key == 27:
        #        break
        #cv2.destroyAllWindows()

        if (area > 500000):
            # Searching for center (x,y) from object
            x = int(moments['m10'] / moments['m00'])
            y = int(moments['m01'] / moments['m00'])

            if x < 150 or x > 450:
                if (not moveTo(0, 0, PI / 16)):
                    return FELL_DOWN
                continue

            computedSize = math.sqrt(area)

            # calculate distance
            dist = SIZE_AT_A_METER / computedSize
            print "distance = ", dist

            # mark the object with an red circle
            rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            #rect_image = cv2.rectangle(rgb_img,
            #(x, y), (x + 50, y + 50), (0, 0, 255), 2)
            #cv2.imshow('rec_image', rect_image)
            cir_image = cv2.circle(rgb_img, (x, y), 50, (255, 0, 0), 3)
            cv2.imshow('circ_image', cir_image)

            detected = True

        #turn to search in another direction
        if not detected:
            if(not moveTo(0, 0, PI / 16)):
                return FELL_DOWN

    return dist


def makeFotoOfQuadrat(imgTitle, colorDown, colorUp):
    # find quadrat
    area, image, moments, mask = getBetterPicture(colorDown, colorUp)

    #show and write
    #cv2.imshow('image', image)
    #while 1:
    #    key = cv2.waitKey(5) & 0xFF
    #    if key == 27:
    #        break
    #cv2.destroyAllWindows()
    x = int(moments['m10'] / moments['m00'])
    y = int(moments['m01'] / moments['m00'])

    cir_image = cv2.circle(image, (x, y), 50, (255, 0, 0), 3)
    cv2.imwrite(imgTitle, cir_image)


def searchColorAndTakeFoto(imgTitle, colorDown, colorUp):
    distance = FELL_DOWN

    while(distance > 0.3 or distance == FELL_DOWN):
        if(distance == FELL_DOWN):
            initMotion(True)
        distance = searchForColor(colorDown, colorUp)
        if(distance == FELL_DOWN or distance <= 0.3):
            continue

        #while(1):
        #    key = cv2.waitKey(5) & 0xFF
        #    if key == 27:
        #        break
        #cv2.destroyAllWindows()

        ttsProxy.say("Found the square object. moving to it.")
        distToWalk = distance / 2
        print "distance to walk =", distToWalk
        if(not moveTo(distToWalk, 0, 0)):
            distance = FELL_DOWN
        distance = distToWalk

    ttsProxy.say("I'm near enough to make the foto")
    makeFotoOfQuadrat(imgTitle, colorDown, colorUp)


def setHeadCentral():
    yawAngle = motionProxy.getAngles("HeadYaw", True)
    pitchAngle = motionProxy.getAngles("HeadPitch", True)
    motionProxy.changeHeadAngles(-1 * yawAngle[0], -1 * pitchAngle[0], 0.1)


def moveTo(x, y, theta):
    motionProxy.moveTo(x, y, theta)
    #while(motionProxy.post.moveIsActive()):
    if(motionProxy.getPosture() == "Back" or
    motionProxy.getPosture() == "Belly"):
        ttsProxy.say("Damnit. Can anybody help me standing up?")
        return False
    motionProxy.waitUntilWalkIsFinished()
    if(motionProxy.getPosture() == "Back" or
    motionProxy.getPosture() == "Belly"):
        ttsProxy.say("Damnit. Can anybody help me standing up?")
        return False
    return True


def initMotion(shouldRest):
    # Wake up robot
   # motionProxy.setStiffnesses("Body", 0.0)
    motionProxy.setStiffnesses("Body", 1.0)
    if(shouldRest):
        motionProxy.rest()
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

    initMotion(False)
    #ttsProxy.say("Hello Masters.")



    ttsProxy.say("Going to search for the pink square.")
    searchColorAndTakeFoto("pink_object.png", PINK_DOWN, PINK_UP)

    ttsProxy.say("Going to search for the orange square.")
    searchColorAndTakeFoto("orange_object.png", ORANGE_DOWN, ORANGE_UP)




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