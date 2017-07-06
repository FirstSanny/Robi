'''
This is the main-file for our RoboCup project
The Robo should search for 2 objects and bring it to
a special destination for each object
'''
from math import pi as PI
from naoqi import ALProxy
from naoqi import ALModule
from optparse import OptionParser

# CONSTANTS
DEFAULT_NAO_IP = "nao.local"
DEFAULT_NAO_PORT = 9559

#global variables
balldetected = False
pip = None
pport = None


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

    # Wake up robot
    motionProxy.setStiffnesses("Body", 1.0)
    motionProxy.wakeUp()

    # Send robot to Stand Init
    motionProxy.moveInit()
    ttsProxy.say("Hello Friends.")

    ttsProxy.say("Going to search for the ball.")
    while not(balldetected):
        motionProxy.moveTo(0, 0, PI / 16)

    ttsProxy.say("Found the Ball.")


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
    global pip
    pip = opts.pip
    global pport
    pport = opts.pport

    main()