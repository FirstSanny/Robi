'''
This is the main-file for our RoboCup project
The Robo should search for 2 objects and bring it to a special destination for each object
'''

from naoqi import ALProxy

from optparse import OptionParser


NAO_IP = "nao.local"

def main(pip, pport):
    '''
    ENTRY-POINT
    '''
    
    # Init Proxy's    
    ttsProxy = ALProxy("ALTextToSpeech", pip, pport)
    motionProxy  = ALProxy("ALMotion", pip, pport)
    postureProxy = ALProxy("ALRobotPosture", pip, pport)

    # Wake up robot
    motionProxy.wakeUp()

    # Send robot to Stand Init
    postureProxy.goToPosture("StandInit", 0.5)
    ttsProxy.say("Hello Friends.")
    
    ttsProxy.say("I am getting on my way.")
    

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
        pip=NAO_IP,
        pport=9559)
    
    (opts, args_) = parser.parse_args()
    pip   = opts.pip
    pport = opts.pport
    main(pip, pport)