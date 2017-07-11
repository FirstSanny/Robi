'''
This is the main-file for our RoboCup project
The Robo should search for 2 objects and bring it to
a special destination for each object
'''
from math import pi as PI
from naoqi import ALProxy
from naoqi import ALModule
from optparse import OptionParser
import cv2
import matplotlib.pyplot as plot
import numpy as np
import math

# CONSTANTS
DEFAULT_NAO_IP = "10.0.7.13"
DEFAULT_NAO_PORT = 9559

# global variables
balldetected = False
pip = None
pport = None

###HSV###
orange_down = np.array([5, 50, 50])
orange_up = np.array([15, 255, 255])

orangedetected = False

# Size of the square and focus camera
Z = 210
f = 30


class BallDetectionModule(ALModule):
    def __init__(self):
        super(BallDetectionModule, self).__init__()
        self.memory = ALProxy("ALMemory")
        self.memory.subscribeToEvent("redBallDetected",
                                     "BallDetecter",
                                     "onRedBallDetected")

    def onRedBallDetected(self, *_args):
        self.memory.unsubscribeToEvent("redBallDetected",
                                       "BallDetecter")
        global balldetected
        balldetected = True


def main():
    '''
    ENTRY-POINT
    '''

    # Init Proxy's
    ttsProxy = ALProxy("ALTextToSpeech", pip, pport)
    motionProxy = ALProxy("ALMotion", pip, pport)
    visionProxy = ALProxy("RobocupVision", pip, pport)

    # Wake up robot
    motionProxy.setStiffnesses("Body", 1.0)
    motionProxy.wakeUp()

    global orangedetected
    global Z
    global f

    # Send robot to Stand Init
    motionProxy.moveInit()
    ttsProxy.say("Hello Friends.")

    # getVisionResults(0)

    # gets the list of sensor supported on your robot
    # getSensorNAmes()

    # getPosture()
    # setPostureConfig(cfg) cfq string of configuration same as content of config file

    # ttsProxy.say("Going to search for the ball.")
    while not (orangedetected):
        cameraId = 0
        data = visionProxy.getBGR24Image(cameraId)
        image = np.fromstring(data, dtype=np.uint8).reshape((480, 640, 3))
        cv2.imshow('image', image)
        hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv_img, orange_down, orange_up)
        moments = cv2.moments(mask)
        area = moments['m00']
        print "area", area

        cv2.imshow('hsv_img', hsv_img)
        cv2.imshow('mask', mask)

        # print area
        if (area > 2):
            # Buscamos el centro x, y del objeto
            x = int(moments['m10'] / moments['m00'])
            y = int(moments['m01'] / moments['m00'])
            z = math.sqrt(area)

            # Mostramos sus coordenadas por pantalla
            print "x = ", x
            print "y = ", y
            print "z = ", z
            # distance to the object
            d = (Z / z) * f

            print "distance = ", d

            object_x = d
            object_y = y
            # object_theta =

            # Rectangle
            rect = cv2.rectangle(hsv_img, (x, y), (x + 100, y + 100), (0, 0, 255), 2)
            cv2.imshow('rec', rect)

            # draw countour around object
           # cv2.drawContours(draw_image, [mask2], 1, (0, 255, 0), 2)
           # cv2.imshow('rec_image', draw_image)

            orangedetected = True

        while (1):
            tecla = cv2.waitKey(5) & 0xFF
            if tecla == 27:
                break

        if not orangedetected:
            motionProxy.moveTo(0, 0, PI / 16)
    # cv2.destroyAllWindows()


    ttsProxy.say("Found the Ball.")

    # After we find the ball, we should walk there. we should know with the camara sensor
    #  the distance to the object and then use that information to walk there
    # we have a error of 10 cm

    # AT FIRST WE NEED TO NOW X,Y,Z IN THE CAMERA AND THEN TRANSFORM IT TO THE BODY X,Y,THETA

    ttsProxy.say("walking to the ball")
    motionProxy.moveTo(object_x - 0.1, object_y - 0.1, 0)

    ttsProxy.say("In front of the ball")

    orange_quadrat = visionProxy.getBGR24Image(cameraId)
    orange_image = np.fromstring(orange_quadrat, dtype=np.uint8).reshape((480, 640, 3))
    cv2.imshow('image', orange_image)
    orange_object = "orange_object"
    cv2.imwrite(orange_object, orange_image)


if __name__ == "__main__":
    # Parsing Commandlineparams
    global pip
    global pport
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
    main()