# -*- coding: utf-8 -*-
import base64
import paramiko
import random
import time
import almath
import pickle
import numpy as np
import speech_recognition as sr
from naoqi import ALProxy
from collections import defaultdict
from google.cloud import texttospeech
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\Users\Text-To-Speech.json"


class Mind:

    NAO_USERNAME = "nao"

    ip = None
    behavior = None     #
    memory = None       # 
    motion = None       # 
    posture = None
    animSpeech = None   #
    audio = None        # 
    tts = None          # 
    recogSpeech = None  # 
    faceDetect = None   #
    photo = None        #
    leds = None         #
    sensors = None      
    autonom = None      

    vocabulary = None
    websocket = None
    pitch = None
    position = None
    disable_front_moves = None

    actions_a = dict()
    actions_b = dict()

    """
    Load the proxy abilities to access the various abilities
    """
    def __init__(self, nao_name, nao_ip):

        self.name        = nao_name
        self.ip          = nao_ip
        self.behavior    = ALProxy("ALBehaviorManager", nao_ip, 9559)
        self.memory      = ALProxy("ALMemory", nao_ip, 9559)
        self.motion      = ALProxy("ALMotion", nao_ip, 9559)
        self.posture     = ALProxy("ALRobotPosture", nao_ip, 9559)
        self.animSpeech  = ALProxy("ALAnimatedSpeech", nao_ip, 9559)
        self.audio       = ALProxy("ALAudioPlayer", nao_ip, 9559)
        self.tts         = ALProxy("ALTextToSpeech", nao_ip, 9559)
        self.recogSpeech = ALProxy("ALSpeechRecognition", nao_ip, 9559)
        self.faceDetect  = ALProxy("ALFaceDetection", nao_ip, 9559)
        self.photo       = ALProxy("ALPhotoCapture", nao_ip, 9559)
        self.leds        = ALProxy("ALLeds", nao_ip, 9559)
        self.sensors     = ALProxy("ALSensors", nao_ip, 9559)
        self.autonom     = ALProxy("ALAutonomousLife", nao_ip, 9559)
        self.aware       = ALProxy("ALBasicAwareness", nao_ip, 9559)
        self.temp        = ALProxy("ALBodyTemperature", nao_ip, 9559)
        self.autoMov     = ALProxy("ALAutonomousMoves", nao_ip, 9559)
        self.photo       = ALProxy("ALPhotoCapture" ,nao_ip, 9559)
        self.aware        = ALProxy("ALBasicAwareness" ,nao_ip, 9559)

        #self.vocabulary  = ["love", "hate", "war", "crime", "china", "trump", "yes", "no"]
        #self.recogSpeech.pause(True)
        #self.recogSpeech.setVocabulary(self.vocabulary, False)  #todo: if speech recognition is not used, delete!
        #self.recogSpeech.pause(False)

        self.position = 0
        self.disable_front_moves = False
        self.load_duo_DB()

        with open('../data/schemas.pkl', 'rb') as f:
            self.actionToSchemaDic = pickle.load(f)
        with open('../data/reactions.pkl', 'rb') as f:
            self.reactionDic = pickle.load(f)

        self.schemaDic = {
            "UP": "schema_creation-30656e/schema_up",
            "DOWN": "schema_creation-30656e/schema_down",
            "FRONT": "schema_creation-30656e/schema_front",
            "BACK": "schema_creation-30656e/schema_back",
            "CENTER": "schema_creation-30656e/schema_center",
            "PERIPHERY": "schema_creation-30656e/schema_periphery",
            "CONTACT": "schema_creation-30656e/schema_contact",
            "IN": "schema_creation-30656e/schema_in",
            "OUT": "schema_creation-30656e/schema_out",
            "SURFACE": "schema_creation-30656e/schema_surface",
            "CYCLE": "schema_creation-30656e/schema_cycle",
            "S-P-G": "schema_creation-30656e/schema_spg",
            "NEAR": "schema_creation-30656e/schema_near",
            "FAR": "schema_creation-30656e/schema_far"
            }

        self.schemaDic_subtle = {
            "UP": "subtle_schemas-ce5d8f/schema_up",
            "DOWN": "subtle_schemas-ce5d8f/schema_down",
            "FRONT": "subtle_schemas-ce5d8f/schema_front",
            "BACK": "subtle_schemas-ce5d8f/schema_back",
            "CENTER": "subtle_schemas-ce5d8f/schema_center",
            "PERIPHERY": "subtle_schemas-ce5d8f/schema_periphery",
            "CONTACT": "subtle_schemas-ce5d8f/schema_contact",
            "IN": "subtle_schemas-ce5d8f/schema_in",
            "OUT": "subtle_schemas-ce5d8f/schema_out",
            "SURFACE": "subtle_schemas-ce5d8f/schema_surface",
            "CYCLE": "subtle_schemas-ce5d8f/schema_cycle",
            "S-P-G": "subtle_schemas-ce5d8f/schema_spg",
            "NEAR": "subtle_schemas-ce5d8f/schema_near",
            "FAR": "subtle_schemas-ce5d8f/schema_far"
        }

        self.schemaInversion = {
            "UP": "DOWN",
            "DOWN": "UP",
            "FRONT": "BACK",
            "BACK": "FRONT",
            "CENTER": "PERIPHERY",
            "PERIPHERY": "CENTER",
            "CONTACT": "PERIPHERY",
            "IN": "OUT",
            "OUT": "IN",
            "SURFACE": "CYCLE",
            "CYCLE": "SURFACE",
            "S-P-G": "CYCLE",
            "NEAR": "FAR",
            "FAR": "NEAR"
        }

        self.iconicDic = {"condescend" : "iconic_actions-4373e0/condescend",
                            "condescend_to" : "iconic_actions-4373e0/condescend",
                            "deceive" : "iconic_actions-4373e0/deceive",
                            "are_deceived_by" : "iconic_actions-4373e0/deceive",
                            "steal" : "iconic_actions-4373e0/steal",
                            "steal_from" : "iconic_actions-4373e0/steal",
                            "rob" : "iconic_actions-4373e0/steal",
                            "are_robbed_by" : "iconic_actions-4373e0/steal",
                            "kill" : "iconic_actions-4373e0/kill",
                            "are_killed_by" : "iconic_actions-4373e0/kill",
                            "execute" : "iconic_actions-4373e0/kill",
                            "kill_for" : "iconic_actions-4373e0/kill",
                            "murder" : "iconic_actions-4373e0/kill",
                            "decapitate" : "iconic_actions-4373e0/kill",
                            "lecture" : "iconic_actions-4373e0/lecture",
                            "are_lectured_by" : "iconic_actions-4373e0/lecture",
                            "lecture_to" : "iconic_actions-4373e0/lecture",
                            "learn_from" : "iconic_actions-4373e0/lecture",
                            "coach" : "iconic_actions-4373e0/lecture",
                            "are_coached_by" : "iconic_actions-4373e0/lecture",
                            "teach" : "iconic_actions-4373e0/lecture",
                            "are_taught_by" : "iconic_actions-4373e0/lecture",
                            "are_mentored_by" : "iconic_actions-4373e0/lecture",
                            "mentor" : "iconic_actions-4373e0/lecture",
                            "are_tutored_by" : "iconic_actions-4373e0/lecture",
                            "educate" : "iconic_actions-4373e0/lecture",
                            "are_educated_by" : "iconic_actions-4373e0/lecture",
                            "instruct" : "iconic_actions-4373e0/lecture",
                            "are_instructed_by" : "iconic_actions-4373e0/lecture",
                            "learn_with" : "iconic_actions-4373e0/lecture",
                            "study_under" : "iconic_actions-4373e0/lecture",
                            "are_seduced_by" : "iconic_actions-4373e0/seduce",
                            "seduce" : "iconic_actions-4373e0/seduce",
                            "are_lured_by" : "iconic_actions-4373e0/seduce",
                            "attack" : "iconic_actions-4373e0/attack",
                            "are_attacked_by" : "iconic_actions-4373e0/attack",
                            "are_assaulted_by" : "iconic_actions-4373e0/attack",
                            "assault" : "iconic_actions-4373e0/attack",
                            "fight" : "iconic_actions-4373e0/attack",
                            "are_fought_by" : "iconic_actions-4373e0/attack",
                            "fight_with" : "iconic_actions-4373e0/attack",
                            "fight_against" : "iconic_actions-4373e0/attack",
                            "kiss" : "iconic_actions-4373e0/kiss",
                            "kiss_up_to" : "iconic_actions-4373e0/kiss",
                            "are_kissed_by" : "iconic_actions-4373e0/kiss",
                            "spurn" : "iconic_actions-4373e0/spurn",
                            "are_spurned_by" : "iconic_actions-4373e0/spurn",
                            "starve" : "iconic_actions-4373e0/starve",
                            "sing" : "iconic_actions-4373e0/sing",
                            "sing_with" : "iconic_actions-4373e0/sing",
                            "paint" : "iconic_actions-4373e0/paint",
                            "are_painted_by" : "iconic_actions-4373e0/paint",
                            "propose" : "iconic_actions-4373e0/propose",
                            "propose_to" : "iconic_actions-4373e0/propose",
                            "baptize" : "iconic_actions-4373e0/baptize",
                            "are_baptized_by" : "iconic_actions-4373e0/baptize",
                            "baptise" : "iconic_actions-4373e0/baptize",
                            "whip" : "iconic_actions-4373e0/whip",
                            "are_whipped_by" : "iconic_actions-4373e0/whip",
                            "hit" : "iconic_actions-4373e0/whip",
                            "point" : "iconic_actions-4373e0/point",
                            "forceful" : "iconic_actions-4373e0/forceful",
                            "surrender" : "iconic_actions-4373e0/surrender",
                            "quizzical" : "animations/Stand/Waiting/ScratchHead_1"}

        self.iconicDic_close = {"condescend": "iconic_actions-4373e0/condescend",
                          "condescend_to": "iconic_actions-4373e0/condescend",
                          "starve": "iconic_actions-4373e0/starve"}

        self.gestuary_dicts = self.load_gestuary("../data/storytellingData/gestuary.txt")

        self.websocket = None
        self.pitch = "\\vct=85\\"
        self.lastBehavior = None

    def alive(self):
        self.posture.goToPosture("Stand", 0.80)
        # Triggers passive movements / turns off awareness
        self.aware.stopAwareness()
        self.autonom.setState("solitary")
        self.autoMov.setExpressiveListeningEnabled(True)
        self.animSpeech.setBodyLanguageMode(1)
        self.autonom.setState("solitary")
        self.autoMov.setExpressiveListeningEnabled(True)
        self.animSpeech.setBodyLanguageMode(1)

    def demise(self):
        """
        Manages shutdown procedures and puts the robot in resting position
        :return: None
        """
        self.behavior.stopAllBehaviors()
        self.motion.rest()
        self.leds.off('AllLeds')

    def say(self, sentence):
        """
        Basic text to speech for the robot speaker
        :param sentence: to be uttered by the robot
        :return: None
        """
        self.tts.post.say(sentence)

    def say_load(self):
        #if self.finished_action():
        self.audio.playFile("/tmp/temp.wav")

    def load_speech(self, sentence, gender, count):
        """
        Basic text to speech for the robot speaker
        :param sentence: to be uttered by the robot
        :return: None
        """

        female_voices = ['en-GB-Wavenet-A', 'en-US-Wavenet-C', 'en-US-Wavenet-E', 'en-US-Wavenet-F', 'en-GB-Wavenet-C', 'en-AU-Wavenet-A', 'en-AU-Wavenet-C']
        male_voices = ['en-US-Wavenet-A', 'en-US-Wavenet-B', 'en-US-Wavenet-D', 'en-GB-Wavenet-B', 'en-GB-Wavenet-D', 'en-AU-Wavenet-B', 'en-AU-Wavenet-D']

        if gender == "Female":
            voice = female_voices[count]
        elif gender == "Male":
            voice = male_voices[count]
        try:
            client = texttospeech.TextToSpeechClient()
            synthesis_input = texttospeech.types.SynthesisInput(text=sentence)
            voice = texttospeech.types.VoiceSelectionParams(
                language_code='en-US',
                name=voice)
            audio_config = texttospeech.types.AudioConfig(
                audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16)
            response = client.synthesize_speech(synthesis_input, voice, audio_config)
        except:
            raise Exception("Google TTS failed.")
            #return False

        with open('temp.wav', 'wb') as out:
            # Write the response to the output file.
            out.write(response.audio_content)

        if self.name == "Kim":
            NAO_PASSWORD = base64.b64decode("password") # 01
        elif self.name == "Bap":
            NAO_PASSWORD = base64.b64decode("password") # 02

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.ip, username=self.NAO_USERNAME, password=NAO_PASSWORD)
        sftp = ssh.open_sftp()
        localpath = "temp.wav"
        remotepath = "/tmp/temp.wav"
        sftp.put(localpath, remotepath)
        sftp.close()
        ssh.close()

        return True

    def ask_for_topic_google(self):
        """
        Using python library SpeechRecognition and Google API to process verbal input (no dictionary required)
        :return: None
        """
        self.say("Hi, we are going to tell you a story, what topic do you have in mind?")
        text = None
        while text == None:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                audio = r.listen(source)
                try:
                    text = r.recognize_google(audio)  # use recognizer to convert our audio into text part.
                    print("User input : {}".format(text))

                except:
                    print("Sorry could not recognize your voice")

        self.say("Ok, we will tell you a story about " + str(text))

    def moveHead(self, direction="right"):
        """
        Move head of robot to (default) right side or left side.
        :param direction: to move the head
        :return: None
        """
        if direction == "right":
            direction = -80.0
        if direction == "left":
            direction = 80.0

        self.motion.setStiffnesses("Head", 1.0)

        # Simple command for the HeadYaw joint at 20% max speed
        names = "HeadYaw"
        angles = direction * almath.TO_RAD
        fractionMaxSpeed = 0.3
        self.motion.setAngles(names, angles, fractionMaxSpeed)

        time.sleep(2.0)
        self.motion.setStiffnesses("Head", 0.0)

    def runBehavior(self, path, post=False):
        """
        Executes a behavior specified by the given path, can run it as daemon if post set to True
        :param path: of the behavior on the robot system
        :param post: if True, behavior is run as daemon thread
        :return: None
        """
        if post:
            self.behavior.post.runBehavior(path)
        else:
            self.behavior.runBehavior(path)

    def showBehaviorList(self):
        """
        Prints the list of installed behaviors
        :return: None
        """
        for elem in self.behavior.getInstalledBehaviors():
            print(elem)

    def load_gestuary(self, filepath):
        behaviorModule = self.behavior

        # Initialize the dictionaries
        phrase_dictSTRONG = defaultdict(list)
        phrase_dictMEDIUM = defaultdict(list)
        phrase_dictWEAK = defaultdict(list)
        phrase_dicts = [phrase_dictSTRONG, phrase_dictMEDIUM, phrase_dictWEAK]

        # open the annotations file and read the data
        with open(filepath, 'r') as f:
            lines = f.readlines()

            for line in lines[1:]:
                token = line.strip().split('\t')
                behPath = token[0].strip()

                # save the annotations in phrase_dict
                for categ, assocCateg in enumerate(range(2, len(token))):
                    # but only of annotation is not empty
                    if (token[assocCateg] != ''):
                        assocs = token[assocCateg].split(",")
                        assocs = [elem.strip() for elem in assocs]
                        assocs = list(filter(None, assocs))
                        assocs = [elem.replace("*", "") for elem in assocs]

                        for assoc in assocs:
                            # check all three association levels
                            phrase_dict = phrase_dicts[categ]

                            if (assoc not in phrase_dict.keys()):
                                phrase_dict[assoc] = list()
                            phrase_dict.get(assoc).append(behPath)

        return phrase_dicts

    def drawFromRandomPool(self, close=False):
        '''
        This method holds a pool of non-contexual hard coded gesture paths for random speech behavior
        :return: randomly chosen non-contextual behavior path (as string)
        '''
        randomGestureList = ['animations/Stand/BodyTalk/Speaking/BodyTalk_9',
                             'animations/Stand/BodyTalk/Speaking/BodyTalk_10',
                             'animations/Stand/BodyTalk/Speaking/BodyTalk_22',
                             'animations/Stand/BodyTalk/Speaking/BodyTalk_11',
                             'animations/Stand/BodyTalk/Speaking/BodyTalk_14',
                             'animations/Stand/BodyTalk/Speaking/BodyTalk_2',
                             'animations/Stand/Gestures/IDontKnow_5',
                             'animations/Stand/Gestures/YouKnowWhat_5',
                             'animations/Stand/Gestures/Explain_1',
                             'animations/Stand/Gestures/Explain_2',
                             'animations/Stand/Gestures/Explain_5',
                             'animations/Stand/Gestures/Explain_7',
                             'animations/Stand/Gestures/HeSays_1',
                             'animations/Stand/Gestures/HeSays_2',
                             'animations/Stand/Gestures/HeSays_3',
                             'animations/Stand/Gestures/This_14']

        if close:
            randomGestureList = ['animations/Stand/BodyTalk/Speaking/BodyTalk_17',
                             'animations/Stand/BodyTalk/Speaking/BodyTalk_20',
                             'animations/Stand/BodyTalk/Speaking/BodyTalk_9',
                             'animations/Stand/Gestures/IDontKnow_4',
                             'animations/Stand/Gestures/IDontKnow_1',
                             'animations/Stand/Gestures/IDontKnow_3',
                             'animations/Stand/Gestures/IDontKnow_2',
                             'animations/Stand/Gestures/YouKnowWhat_4',
                             'animations/Stand/Gestures/YouKnowWhat_1',
                             'animations/Stand/Gestures/HeSays_2',
                             'animations/Stand/Gestures/This_11',
                             'animations/Stand/Gestures/This_10']

        return random.choice(randomGestureList)

    def finished_action(self):
        while self.behavior.isBehaviorRunning(str(self.lastBehavior)):
            time.sleep(0.5)
        return True

    def load_duo_DB(self, path="gestuary_duo.tsv"):
        # reset dicts
        self.actions_a = dict()
        self.actions_b = dict()

        # open the gestuary for dialog data
        with open("../data/storytellingData/"+path, "r") as f_in:
            f_in.readline()
            lines = f_in.readlines()

        # retrieve the gestures for the actions
        for line in lines:
            content = line.split("\t")
            word = content[0]
            acts_a = content[1].split(",")
            acts_b = content[2].split(",")

            self.actions_a[word] = [act_a.strip() for act_a in acts_a]
            self.actions_b[word] = [act_b.strip() for act_b in acts_b]

    def evaluateBehavior_DB(self, behavior):

        # clear behavior string
        behavior = behavior.split(" ")
        if len(behavior) > 1:
            behavior = behavior[1].strip("*")
        else:
            behavior = behavior[0].strip("*")

        if behavior not in self.actions_a.keys():
            act_a = self.drawFromRandomPool(self.disable_front_moves)
        else:
            act_a = self.actions_a[behavior]
            print("Gesture to action: ", act_a)

        if behavior not in self.actions_b.keys():
            act_b = self.drawFromRandomPool(self.disable_front_moves)
        else:
            act_b = self.actions_b[behavior]
            print("Gesture to action: ", act_b)

        # if no gesture as action could be found, retrieve reaction
        if act_a[0] == "":
            react_value = self.reactionDic[behavior][0]
            act_a = "reaction_moves-4cc1d0/react_"+str(react_value)
            if self.disable_front_moves:
                if int(react_value) > 2:
                    react_value = 2
                    act_a = random.choice(["reaction_moves-4cc1d0/react_" + str(react_value), self.drawFromRandomPool(True)])
                if int(react_value) < -1:
                    react_value = -1
                    act_a = random.choice(["reaction_moves-4cc1d0/react_" + str(react_value), self.drawFromRandomPool(True)])
            print("(Kim reaction: " + str(react_value) + ")")

        if act_b[0] == "":
            react_value = self.reactionDic[behavior][0]
            act_b = "reaction_moves-4cc1d0/react_" + str(react_value)
            if not self.disable_front_moves:
                if int(react_value) > 2:
                    react_value = 2
                    act_b = random.choice(["reaction_moves-4cc1d0/react_" + str(react_value), self.drawFromRandomPool(True)])
                if int(react_value) < -1:
                    react_value = -1
                    act_b = random.choice(["reaction_moves-4cc1d0/react_" + str(react_value), self.drawFromRandomPool(True)])
            print("(Bap reaction: " + str(react_value) + ")")

        # choose best action with weighted probabilities, better gestures are preferred
        if isinstance(act_a, list) and len(act_a) == 1:
            act_a = act_a[0]
        elif isinstance(act_a, list):
            # check if iconic movement is available
            iconic_a = [s for s in act_a if "iconic" in s]
            if iconic_a:
                act_a = iconic_a
                if isinstance(act_a, list):
                    act_a = act_a[0]
            else:
                act_a = sorted(act_a)
                weights = np.linspace(5, 50, len(act_a)) / 100
                weights = list(weights / np.sum(weights))
                weights.reverse()
                act_a = np.random.choice(act_a, 1, p=weights)[0]

        if isinstance(act_b, list) and len(act_b) == 1:
            act_b = act_b[0]
        elif isinstance(act_b, list):
            iconic_b = [s for s in act_b if "iconic" in s]
            if iconic_b:
                act_b = iconic_b
                if isinstance(act_b, list):
                    act_b = act_b[0]
            else:
                act_b = sorted(act_b)
                weights = np.linspace(5, 50, len(act_b)) / 100
                weights = list(weights / np.sum(weights))
                weights.reverse()
                act_b = np.random.choice(act_b, 1, p=weights)[0]

        return act_a.replace("*", ""), act_b.replace("*", "")

    def evaluateBehavior_DB_random(self, behavior):
        # get random actions
        return random.choice(self.gestuary_dicts[0][random.choice(self.gestuary_dicts[0].keys())]), random.choice(self.gestuary_dicts[0][random.choice(self.gestuary_dicts[0].keys())])

    def evaluateBehavior(self, behavior, actor):

        # if there is only A-* or B-*, then no acting
        able = True
        if actor == "A":
            passive = False
            # if B is the active actor of the behavior, set A to be passive
            if behavior.startswith("A-") or behavior.startswith("*") or behavior.startswith("B"):
                passive = True
        elif actor == "B":
            passive = False
            # if A is the active actor of the behavior, set B to be passive
            if behavior.startswith("B-") or not behavior.startswith("*") or behavior.startswith("A"):
                passive = True
        else:
            print("This should not happen.")
            exit()

        if " " in behavior:
            temp = behavior.split(" ")[1]
            if "-" in temp[0] and "-" in temp[2]:
                able = False
        else:
            temp = behavior

        # we access the gestuary
        if ("are_" in temp and passive and able) or (not "are_" in temp and not passive and able):
            print("action chosen")
            behavs = []
            for idx, dic in enumerate(self.gestuary_dicts):
                behav = dic.get(temp)

                # remove all sound behaviors if flag not set
                # if not soundAllowed and behav:
                #    behav = [elem for elem in behav if "*" not in elem]
                # check if this dictionary (strong, medium, weak) has any entries of ACTIVE verbs
                if behav:
                    behavs.extend(behav)
                print("Found strength ", idx, " gestures: ", behavs)
                if len(behavs) > 2:
                    print("Length of found gestures: ", len(behavs))
                    break

            if not behavs:
                gesture = self.drawFromRandomPool()
                print("Taking random gesture.")
            else:
                gesture = random.choice(behavs)

        # we need a reaction
        elif ("are_" in temp and not passive and able) or (not "are_" in temp and passive and able):
            print("reaction chosen")
            if actor == "A":
                reaction_level = self.reactionDic[temp.replace("*", "")][0]
            elif actor == "B":
                reaction_level = self.reactionDic[temp.replace("*", "")][1]

            gesture = "reaction_moves-4cc1d0/react_"+str(reaction_level)

        else:
            print("This should not happen.")
            exit()

        print(gesture)
        return gesture

    def movement_IS(self, move, act, inverse, congruency=False):

        if congruency:
            if move == "closer":
                move = "back-away"
            elif move == "back-away":
                move = "closer"

        if isinstance(move, tuple) and len(move) > 1:
            print("Move: " + str(move) + " Length: ", str(len(move)))
            self.movement(move[0])
            self.movement(move[1])
            return

        if move == "closer" and self.position < 3:
            print("Moving closer from "+str(self.position)+" to "+str(self.position+1))
            self.position += 1

            self.posture.goToPosture("Stand", 0.5)
            self.motion.setFootStepsWithSpeed(["LLeg"], [[0.1, 0, 0]], [0.1], False)
            self.motion.setFootStepsWithSpeed(["RLeg"], [[0, 0, 0]], [0.1], False)

            self.posture.goToPosture("StandInit", 0.5)
            self.posture.goToPosture("Stand", 0.5)

        if move == "back-away" and self.position > -3:
            print("Moving away from " + str(self.position) + " to " + str(self.position - 1))
            self.position -= 1

            self.posture.goToPosture("Stand", 0.5)
            self.motion.setFootStepsWithSpeed(["LLeg"], [[-0.1, 0, 0]], [0.1], False)
            self.motion.setFootStepsWithSpeed(["RLeg"], [[0, 0, 0]], [0.1], False)

            self.posture.goToPosture("StandInit", 0.5)
            self.posture.goToPosture("Stand", 0.5)

        schema = act
        if " " in act:
            schema = act.split(" ")[1]
        schema = self.actionToSchemaDic[schema]

        if inverse:
            schema = self.schemaInversion[schema]
        print("Do: ", self.schemaDic_subtle[schema])
        self.runBehavior(self.schemaDic_subtle[schema], True)
        self.lastBehavior = self.schemaDic_subtle[schema]

    def spatial_move(self, move, congruency=False):

        if congruency:
            if move == "closer":
                move = "back-away"
            elif move == "back-away":
                move = "closer"

        if isinstance(move, tuple) and len(move) > 1:
            print("Move: " + str(move) + " Length: ", str(len(move)))
            self.spatial_move(move[0])
            self.spatial_move(move[1])
            return

        if move == "closer" and self.position < 3:
            print("Moving closer from "+str(self.position)+" to "+str(self.position+1))
            self.position += 1

            self.posture.goToPosture("Stand", 0.5)
            self.motion.setFootStepsWithSpeed(["LLeg"], [[0.1, 0, 0]], [0.1], False)
            self.motion.setFootStepsWithSpeed(["RLeg"], [[0, 0, 0]], [0.1], False)

            self.posture.goToPosture("StandInit", 0.5)
            self.posture.goToPosture("Stand", 0.5)

        if move == "back-away" and self.position > -3:
            print("Moving away from " + str(self.position) + " to " + str(self.position - 1))
            self.position -= 1

            self.posture.goToPosture("Stand", 0.5)
            self.motion.setFootStepsWithSpeed(["LLeg"], [[-0.1, 0, 0]], [0.1], False)
            self.motion.setFootStepsWithSpeed(["RLeg"], [[0, 0, 0]], [0.1], False)
            self.motion.setFootStepsWithSpeed(["LLeg"], [[-0.1, 0, 0]], [0.1], False)
            self.motion.setFootStepsWithSpeed(["RLeg"], [[0, 0, 0]], [0.1], False)

            self.posture.goToPosture("StandInit", 0.5)
            self.posture.goToPosture("Stand", 0.5)

        if move in self.iconicDic and not self.disable_front_moves:
            print("Do: ", self.iconicDic[move])
            self.runBehavior(self.iconicDic[move], True)
            self.lastBehavior = self.iconicDic[move]
            return True
        elif move in self.iconicDic_close and self.disable_front_moves:
            print("Do: ", self.iconicDic_close[move])
            self.runBehavior(self.iconicDic_close[move], True)
            self.lastBehavior = self.iconicDic_close[move]
            return True
        else:
            return False


    def movement_pant(self, move, behavior, actor):

        if isinstance(move, tuple) and len(move) > 1:
            #print("Move: " + str(move) + " Length: ", str(len(move)))
            self.movement(move[0])
            self.movement(move[1])
            return

        if move in self.iconicDic:
            print("Do: ", self.iconicDic[move])
            self.runBehavior(self.iconicDic[move], True)
            self.lastBehavior = self.iconicDic[move]

        else:
            behavior = self.evaluateBehavior(behavior, actor)
            if behavior is None:
                print("Random move.")
                random_move = self.drawFromRandomPool()
                self.runBehavior(random_move, True)
                self.lastBehavior = random_move
            else:
                print("Do: ", behavior)
                self.runBehavior(behavior, True)
                self.lastBehavior = behavior

    def movement(self, move):

        if isinstance(move, tuple) and len(move) > 1:
            print("Move: " + str(move) + " Length: ", str(len(move)))
            self.movement(move[0])
            self.movement(move[1])
            return

        if move == "closer" and self.position < 3:
            print("Moving closer from "+str(self.position)+" to "+str(self.position+1))
            self.position += 1

            #self.posture.goToPosture("Stand", 0.5)
            #self.motion.setFootStepsWithSpeed(["LLeg"], [[0.1, 0, 0]], [0.1], False)
            #self.motion.setFootStepsWithSpeed(["RLeg"], [[0, 0, 0]], [0.1], False)

            #self.posture.goToPosture("StandInit", 0.5)
            #self.posture.goToPosture("Stand", 0.5)

        if move == "back-away" and self.position > -3:
            print("Moving away from " + str(self.position) + " to " + str(self.position - 1))
            self.position -= 1

            #self.posture.goToPosture("Stand", 0.5)
            #self.motion.setFootStepsWithSpeed(["LLeg"], [[-0.1, 0, 0]], [0.1], False)
            #self.motion.setFootStepsWithSpeed(["RLeg"], [[0, 0, 0]], [0.1], False)

            #self.posture.goToPosture("StandInit", 0.5)
            #self.posture.goToPosture("Stand", 0.5)

        if move in self.iconicDic:
            print("Do: ", self.iconicDic[move])
            self.runBehavior(self.iconicDic[move], True)
            self.lastBehavior = self.iconicDic[move]

        if "default" in move:
            print("Random move.")
            random_move = self.drawFromRandomPool()
            self.runBehavior(random_move, True)
            self.lastBehavior = random_move

        else:
            pass
            #ValueError("This should not happen. Parsing of movement failed.")
            #exit()

    def pantomime_move(self, action):
        print("Action: ", action)

        if action in self.iconicDic:
            self.runBehavior(self.iconicDic[action], True)
            self.lastBehavior = self.iconicDic[action]
            return None

        behavs = []
        for idx, dic in enumerate(self.gestuary_dicts):
            behav = dic.get(action)

            # remove all sound behaviors if flag not set
            #if not soundAllowed and behav:
            #    behav = [elem for elem in behav if "*" not in elem]
            # check if this dictionary (strong, medium, weak) has any entries of ACTIVE verbs
            if behav:
                behavs.extend(behav)
            print("Found strength ", idx, " gestures: ", behavs)
            if len(behavs)>2:
                print("Length of found gestures: ", len(behavs))
                break

        if not behavs:
            gesture = self.drawFromRandomPool()
            print("Taking random gesture.")
        else:
            gesture = random.choice(behavs)
        print(gesture)

        self.runBehavior(gesture, True)
        self.lastBehavior = gesture

    def schema_move(self, schema):
        self.behavior.runBehavior(self.schemaDic_subtle[schema])

    def reaction_move(self, reaction_number):


        # Todo: relate reaction number to internal representation
        self.say("I would react with a: "+str(reaction_number))
        #pass