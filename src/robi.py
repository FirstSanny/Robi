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

# CONSTANTS
DEFAULT_NAO_IP = "nao3.local"
DEFAULT_NAO_PORT = 9559

#global variables
balldetected = False
pip = None
pport = None
#RGB
#orange_down = np.array([16, 48, 91])
#orange_up = np.array([46, 100, 100])
#BGR
orange_down = np.array([153, 204, 255])
orange_up = np.array([0, 102, 102])

orangedetected = False



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


    # Send robot to Stand Init
    motionProxy.moveInit()
    ttsProxy.say("Hello Friends.")

    #getVisionResults(0)

    ttsProxy.say("Going to search for the ball.")
    while not(orangedetected):
        cameraId = 0
        data = visionProxy.getBGR24Image(cameraId)
        image = np.fromstring(data, dtype=np.uint8).reshape((480, 640, 3))
        cv2.imshow('image', image)
        #hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        #mask = cv2.inRange(hsv_img, orange_down, orange_up)
        #moments = cv2.moments(mask)
        #area = moments['m00']

        mask2 = cv2.inRange(image, orange_down, orange_up)
        moments = cv2.moments(mask2)
        area = moments['m00']

       # cv2.imshow('hsv_img', hsv_img)
       # cv2.imshow('mask', mask)
        cv2.imshow('mask_image', mask2)


        # print area
        #if (area > 2000):
            # Buscamos el centro x, y del objeto
         #   x = int(moments['m10'] / moments['m00'])
          #  y = int(moments['m01'] / moments['m00'])

            # Mostramos sus coordenadas por pantalla
#            print "x = ", x
#           print "y = ", y

            # Dibujamos una marca en el centro del objeto
#            rect = cv2.rectangle(hsv_img, (x, y), (x + 100, y + 100), (0, 0, 255), 2)
#            cv2.imshow('rec', rect)
            # Mostramos la imagen original con la marca del centro y
            # la mascara


#            orangedetected = True

        if (area > 200000):
            # Buscamos el centro x, y del objeto
            x = int(moments['m10'] / moments['m00'])
            y = int(moments['m01'] / moments['m00'])

            # Mostramos sus coordenadas por pantalla
            print "x = ", x
            print "y = ", y

            # Dibujamos una marca en el centro del objeto
            rect_image = cv2.rectangle(image, (x, y), (x + 100, y + 100), (0, 0, 255), 2)
            cv2.imshow('rec_image', rect_image)
            # Mostramos la imagen original con la marca del centro y
            # la mascara


            orangedetected = True

        while(1):
            tecla = cv2.waitKey(5) & 0xFF
            if tecla == 27:
                break


        if not orangedetected:
            motionProxy.moveTo(0, 0, PI / 16)
    #cv2.destroyAllWindows()


    ttsProxy.say("Found the Ball.")


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