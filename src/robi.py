'''
This is the main-file for our RoboCup project
The Robo should search for 2 objects and bring it to
a special destination for each object
'''
from math import pi as PI
from naoqi import ALProxy
from optparse import OptionParser
import numpy as np
from os import listdir, path
import pickle
import cv2
import math

# CONSTANTS
#DEFAULT_NAO_IP = "nao3.local"
DEFAULT_NAO_IP = "10.0.7.16"
DEFAULT_NAO_PORT = 9559

ROBOT_POSE_CLF = 'recources/robot_pose.pkl'
ROBOT_POSE_DATA_DIR = 'recources/robot_pose_data'
classes = listdir(ROBOT_POSE_DATA_DIR)

#global variables - ports
pip = None
pport = None
#global variables - constants
sizeOfObject = 210
focus = 300
cameraId = 1
cte_size = 1190

###HSV###
orange_down = np.array([10, 150, 150])
orange_up = np.array([15, 255, 255])

#global variables
orangedetected = False


def searchForTheBall(motionProxy, visionProxy):
    global orangedetected
    orangedetected = False
    dist = 0

    while not(orangedetected):

        #get imagedata from top cam
        data = visionProxy.getBGR24Image(cameraId)
        image = np.fromstring(data, dtype=np.uint8).reshape((480, 640, 3))
        #cv2.imshow('image', image)
        hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        #search orange
        mask = cv2.inRange(hsv_img, orange_down, orange_up)
        moments = cv2.moments(mask)
        area = moments['m00']

        #mask2 = cv2.inRange(image, orange_down, orange_up)
        #moments = cv2.moments(mask2)
        #area = moments['m00']

        #cv2.imshow('hsv_img', hsv_img)
        cv2.imshow('mask', mask)
        cv2.imshow('image', image)

        if (area > 500000):
            # Searching for center (x,y) from object
            x = int(moments['m10'] / moments['m00'])
            y = int(moments['m01'] / moments['m00'])
            computedSize = math.sqrt(area)

            # print coordinates on console
            print "x = ", x
            print "y = ", y
            print "computedSize = ", computedSize

            # calculate distance
            #dist = (sizeOfObject / computedSize) * focus
            dist = cte_size / computedSize
            print "distance = ", dist

            # mark the object with an red circle
            rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            rect_image = cv2.rectangle(rgb_img,
            (x , y ), (x + 50, y + 50), (0, 0, 255), 2)
            cv2.imshow('rec_image', rect_image)

           # draw_image = cv2.drawContours(rgb_img, [mask], 1, (0, 255, 0), 2)
            #cv2.imshow('draw_image', draw_image)

            orangedetected = True

        while 1:
            key = cv2.waitKey(5) & 0xFF
            if key == 27:
                break
        #turn to search in another direction
        if not orangedetected:
            motionProxy.moveTo(0, 0, PI / 16)

    return dist


def makeFotoOfOrangeQuadrat(visionProxy):
    # find quadrat
    orange_quadrat = visionProxy.getBGR24Image(cameraId)
    orange_image = np.fromstring(orange_quadrat,
    dtype=np.uint8).reshape((480, 640, 3))

    #show and write
    cv2.imshow('image', orange_image)
    orange_object = "orange_object"
    while 1:
        key = cv2.waitKey(5) & 0xFF
        if key == 27:
            break
    cv2.imwrite(orange_object, orange_image)

def recognize_posture(motionProxy):
    posture_classifier = pickle.load(open(ROBOT_POSE_CLF))
    posture = 'unknown'
    perception = motionProxy.getPerception()
    data = {}
    data.append(perception.joint['LHipYawPitch'])
    data.append(perception.joint['LHipRoll'])
    data.append(perception.joint['LHipPitch'])
    data.append(perception.joint['LKneePitch'])
    data.append(perception.joint['RHipYawPitch'])
    data.append(perception.joint['RHipRoll'])
    data.append(perception.joint['RHipPitch'])
    data.append(perception.joint['RKneePitch'])
    data += perception.imu

    data = numpy.array(data).reshape(1, -1)

    index = self.posture_classifier.predict(data)
    posture = classes[index[0]]
    return posture

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
        print "distance to walk =", distance/2
        motionProxy.moveTo(distance / 2 , 0, 0)
    ttsProxy.say("In front of the ball")
    makeFotoOfOrangeQuadrat(visionProxy)


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