'''
This is the main-file for our RoboCup project
The Robo should search for 2 objects and bring it to a special destination for each object
'''

from naoqi import ALProxy

from optparse import OptionParser


NAO_IP = "nao.local"

def main():
    '''
    ENTRY-POINT
    '''
    
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
    
    tts = ALProxy("ALTextToSpeech", pip, pport)
    tts.say("I am getting on my way.")
    
    

if __name__ == "__main__":
    main()