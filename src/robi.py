'''
This is the main-file for our RoboCup project
The Robo should search for 2 objects and bring it to
a special destination for each object
'''
from math import pi as PI
from naoqi import ALProxy
from optparse import OptionParser
import cv2
import numpy as np

# CONSTANTS
DEFAULT_NAO_IP = "nao3.local"
DEFAULT_NAO_PORT = 9559

#global variables
balldetected = False
pip = None
pport = None

###RGB##
#orange_down = np.array([16, 48, 91])
#orange_up = np.array([46, 100, 100])

###BGR###
#orange_down = np.array([153, 204, 255])
#orange_up = np.array([0, 102, 102])

###HSV###
orange_down = np.array([5, 50, 50])
orange_up = np.array([15, 255, 255])

orangedetected = False


def searchForTheBall(motionProxy, visionProxy):
    global orangedetected
    orangedetected = False
    
    while not(orangedetected):   
        cameraId = 0
        
        data = visionProxy.getBGR24Image(cameraId)
        image = np.fromstring(data, dtype=np.uint8).reshape((480, 640, 3)) #cv2.imshow('image', image)
        hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        mask = cv2.inRange(hsv_img, orange_down, orange_up)
        moments = cv2.moments(mask)
        area = moments['m00']
       
        #mask2 = cv2.inRange(image, orange_down, orange_up)
        #moments = cv2.moments(mask2)
        #area = moments['m00']
       
        cv2.imshow('hsv_img', hsv_img)
        cv2.imshow('mask', mask)
        #cv2.imshow('mask_image', mask2)
        
        if (area > 20000):
            # Searching for center (x,y) from object
            x = int(moments['m10'] / moments['m00'])
            y = int(moments['m01'] / moments['m00'])
            
            # print coordinates on console
            print "x = ", x
            print "y = ", y
            
            # mark the object with an red circle
            rect_image = cv2.rectangle(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), (x - 50, y - 50), (x + 50, y + 50), (0, 0, 255), 2)
            cv2.imshow('rec_image', rect_image)
            
            orangedetected = True
        while 1:
            key = cv2.waitKey(5) & 0xFF
            if key == 27:
                break
        
        if not orangedetected:
            motionProxy.moveTo(0, 0, PI / 16)
        
        #TODO: Compute Distance and return it
        return 0.3

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

    # Send robot to Stand Init
    motionProxy.moveInit()
    ttsProxy.say("Hello Friends.")

    #getVisionResults(0)

    ttsProxy.say("Going to search for the ball.")
    distance = 100
    
    while(distance > 0.2):
        distance = searchForTheBall(motionProxy, visionProxy)
        
        while(1):
            key = cv2.waitKey(5) & 0xFF
            if key == 27:
                break
        cv2.destroyAllWindows()
    
        ttsProxy.say("Found the Ball. Moving toward it.")
        motionProxy.move(distance/8, 0, 0);
    


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