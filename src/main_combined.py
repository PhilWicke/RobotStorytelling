import pyttsx3, time
from consciousness import Mind
from storyParser import parse_one_dialog, get_random_line
from subtitle_tools import srt_maker

srt = srt_maker()

bap = Mind("Bap", "10.0.0.12")
bap.alive()

kim = Mind("Kim", "10.0.0.13")
kim.alive()

narrator = pyttsx3.init()
narrator.setProperty('voice', "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0")
narrator.setProperty('rate', 135)

story, actions = parse_one_dialog("test_story.txt")
action_count = 0

#story_line = get_random_line("../data/storyville.txt")
#story, actions = parse_one_dialog(story_line) # use: story_line

gender_A = None
count_A = 0
gender_B = None
count_B = 0

role_A = None
role_B = None


for idx, acts in enumerate(story):

    # Mapping the gender for the voice
    action = acts[0]
    if action == 0:
        characters = acts[1].split(";")
        for character in characters[:2]:
            mapping = character.split("=")
            if mapping[1][-2] == "F" and mapping[0] == "A":
                gender_A = "Female"
            elif mapping[1][-2] == "F" and mapping[0] == "B":
                gender_B = "Female"
            elif mapping[1][-2] == "M" and mapping[0] == "A":
                gender_A = "Male"
            elif mapping[1][-2] == "M" and mapping[0] == "B":
                gender_B = "Male"
        if gender_A == gender_B:
            count_B += 1

        # Introduction of actors
        role_A = characters[0].split("=")[1][:-3]
        role_B = characters[1].split("=")[1][:-3]

        print("Introduction.")
        narrator.say("Say hello to " + role_A)
        kim.runBehavior("intro_moves-582bc0/intro_right_1", True)
        srt.add_srt("Say hello to " + role_A)
        narrator.runAndWait()
        time.sleep(2)

        narrator.say("and let us welcome " + role_B)
        bap.runBehavior("intro_moves-582bc0/intro_left_1", True)
        srt.add_srt("and let us welcome " + role_B)
        narrator.runAndWait()
        time.sleep(2)


    # Let the narrator speak the first two sentences
    elif action == 1:
        sentence = acts[1]
        print("Narrator: " + sentence)
        narrator.say(sentence)
        srt.add_srt(sentence)
        narrator.runAndWait()

    else:
        print("Parsing sentence.")
        # Define the gestures for the actors
        lead = None
        behavior = actions[action_count]
        action_count += 1

        # If both robots are too close, disable moves that interfere
        if kim.position + bap.position >= 4 and (not kim.disable_front_moves or not bap.disable_front_moves):
                print("Too close, disable frontal moves.")
                kim.disable_front_moves = True
                bap.disable_front_moves = True
                kim.load_duo_DB("gestuary_duo_close.tsv")
                bap.load_duo_DB("gestuary_duo_close.tsv")

        elif kim.position + bap.position < 4 and (kim.disable_front_moves or bap.disable_front_moves):
                print("Not too close, enable frontal moves.")
                kim.disable_front_moves = True
                bap.disable_front_moves = True
                kim.load_duo_DB("gestuary_duo_close.tsv")
                bap.load_duo_DB("gestuary_duo_close.tsv")

        if behavior.startswith("*") or behavior.startswith("B"):
            bap_act, kim_act = kim.evaluateBehavior_DB(behavior)
            print("Selected A-action: ", kim_act)
            print("Selected B-action: ", bap_act)
        else:
            kim_act, bap_act = kim.evaluateBehavior_DB(behavior)
            print("Selected A-action: ", kim_act)
            print("Selected B-action: ", bap_act)

        for idx, element in enumerate(acts[1]):
            act = acts[0]
            actor = element[0]
            if "{" in element[1]: # the second element should have the gesture definition
                move = element[1][1:]
                if "{" in element[2]:   # if the third also has a gesture definition
                    move = (element[1][1:], element[2][1:])
                    sentence = element[3]
                else:
                    sentence = element[2]
            else:
                move = None
                sentence = element[1]

            print("Executing sentence.")
            # Decide if narrator or actors speak and move
            if actor == "N":
                print("Narrator: "+sentence)
                narrator.say(sentence)
                srt.add_srt(sentence)
                narrator.runAndWait()
            elif actor == "A":
                print("Kim: <"+str(move)+">")

                made_iconic_move = kim.spatial_move(move)
                if not made_iconic_move:
                    print("No iconic move, hence A-action: ", kim_act)
                    kim.runBehavior(kim_act, True)
                kim.load_speech(sentence, gender_A, count_A)

                print("Kim: "+sentence)
                srt.add_srt(sentence)
                kim.say_load()
            elif actor == "B":
                print("Bap: <"+str(move)+">")

                made_iconic_move = bap.spatial_move(move)
                if not made_iconic_move:
                    print("No iconic move, hence B-action: ", bap_act)
                    bap.runBehavior(bap_act, True)
                bap.load_speech(sentence, gender_B, count_B)


                print("Bap: "+sentence)
                srt.add_srt(sentence)
                bap.say_load()

    #srt.print_lines()

# Outro of actors
narrator.say("Let's say goodbye to " + role_A)
kim.runBehavior("intro_moves-582bc0/intro_right_2", True)
srt.add_srt("Let's say goodbye to " + role_A)
narrator.runAndWait()

time.sleep(2)
narrator.say("and let us thank " + role_B)
bap.runBehavior("intro_moves-582bc0/intro_left_2", True)
srt.add_srt("and let us thank " + role_B)
narrator.runAndWait()
time.sleep(4)

srt.make_srt("temp.srt")
bap.demise()
kim.demise()