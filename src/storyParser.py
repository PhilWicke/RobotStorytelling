import pickle
import os
import random

def get_random_line(filepath):
    file_size = os.path.getsize(filepath)
    with open(filepath, 'r') as f:
        while True:
            pos = random.randint(0, file_size)
            if not pos:  # the first line is chosen
                return f.readline()  # return str
            f.seek(pos)  # seek to random position
            f.readline()  # skip possibly incomplete line
            line = f.readline()  # read next (full) line
            if line:
                return line
            # else: line is empty -> EOF -> try another position in next iteration

def parse_rnd_dialog(path):
    """
    This method will parse dialog stories line by line and returns a list of stories in the following format:
    stories[1-N] holds all stories -> for story in stories
        Each story consists of lines -> for line in story
            Each line contains acts, except for the first two and the last line, here: line[0] == 0.
            line[0] = action (or "0" for first two and last line).
                acts = lines[1] -> for act in acts:
                    Each act has two or three parts -> for part in act:
                        role = act[0]
                        if act[1] starts with "{":
                            gesture = act[1]
                            sentence = act[2]
                        else
                            sentence = act[1]

    :param path: path to the example story file with the dialog
    :return: stories object (see method description)
    """
    # Parsing the example stories
    line = get_random_line(path)
    story = []

    content = line.split("\t")
    for indx, elem in enumerate(content):
        if indx == 1:
            story.append((0,elem))
        if indx == 3 or indx == 4 or indx == len(content)-1:
            story.append((1,elem))
        elif indx > 1 and len(elem)>1:
            acts = []
            parts = elem.split("]")
            action = parts[0].replace("[", "").replace("*", "")   # append: ACTION
            act = parts[1].split("|") #  act = ['A:{closer}you are as lovable as a little puppy', 'B:You flatter me', 'N:So at first']

            for part in act:
                temp = []
                if "}" in part:
                    whole = part.split("}")
                    [temp.append(fro) for fro in whole[0].split(":")]
                    temp.append(whole[1])
                    if len(whole) > 2:
                        temp.append(whole[2])
                else:
                    [temp.append(par) for par in part.split(":")]
                acts.append(temp)

            story.append((action, acts))
    return  story

def parse_one_dialog(path):
    """
    This method will parse dialog stories line by line and returns a list of stories in the following format:
    stories[1-N] holds all stories -> for story in stories
        Each story consists of lines -> for line in story
            Each line contains acts, except for the first two and the last line, here: line[0] == 0.
            line[0] = action (or "0" for first two and last line).
                acts = lines[1] -> for act in acts:
                    Each act has two or three parts -> for part in act:
                        role = act[0]
                        if act[1] starts with "{":
                            gesture = act[1]
                            sentence = act[2]
                        else
                            sentence = act[1]

    :param path: path to the example story file with the dialog
    :return: stories object (see method description)
    """
    # Parsing the example stories
    with open(path, "r") as fIn:
        line = fIn.readline()
    #line = path
    story = []
    actions = []

    content = line.split("\t")
    for indx, elem in enumerate(content):
        if indx == 0:
            actions = elem.split(":[")[1].replace("]", "").split(":")
        if indx == 1:
            story.append((0,elem))
        if indx == 3 or indx == 4 or indx == len(content)-1:
            story.append((1,elem))
        elif indx > 1 and len(elem)>1:
            acts = []
            parts = elem.split("]")
            action = parts[0].replace("[", "").replace("*", "")   # append: ACTION
            act = parts[1].split("|") #  act = ['A:{closer}you are as lovable as a little puppy', 'B:You flatter me', 'N:So at first']

            for part in act:
                temp = []
                if "}" in part:
                    whole = part.split("}")
                    [temp.append(fro) for fro in whole[0].split(":")]
                    temp.append(whole[1])
                    if len(whole) > 2:
                        temp.append(whole[2])
                else:
                    [temp.append(par) for par in part.split(":")]
                acts.append(temp)

            story.append((action, acts))
    return  story, actions

def parse_dialog(path):
    """
    This method will parse dialog stories line by line and returns a list of stories in the following format:
    stories[1-N] holds all stories -> for story in stories
        Each story consists of lines -> for line in story
            Each line contains acts, except for the first two and the last line, here: line[0] == 0.
            line[0] = action (or "0" for first two and last line).
                acts = lines[1] -> for act in acts:
                    Each act has two or three parts -> for part in act:
                        role = act[0]
                        if act[1] starts with "{":
                            gesture = act[1]
                            sentence = act[2]
                        else
                            sentence = act[1]

    :param path: path to the example story file with the dialog
    :return: stories object (see method description)
    """

    # Parsing the example stories
    with open(path, "r") as fIn:
        lines = fIn.readlines()
    stories = []
    story = []
    for idx, line in enumerate(lines):
        content = line.split("\t")
        for indx, elem in enumerate(content):
            if indx == 1:
                story.append((0,elem))
            if indx == 2 or indx == 3 or indx == len(content)-1:
                story.append((1,elem))
            elif indx > 1:
                acts = []
                parts = elem.split("]")
                action = parts[0].replace("[", "").replace("*", "")   # append: ACTION
                act = parts[1].split("|") #  act = ['A:{closer}you are as lovable as a little puppy', 'B:You flatter me', 'N:So at first']

                for part in act:
                    temp = []
                    if "}" in part:
                        whole = part.split("}")
                        [temp.append(fro) for fro in whole[0].split(":")]
                        temp.append(whole[1])
                        if len(whole) > 2:
                            temp.append(whole[2])
                    else:
                        [temp.append(par) for par in part.split(":")]
                    acts.append(temp)

                story.append((action, acts))
        stories.append(story)

    return(stories)


def parse_story(path):

    # Load annotations for actions
    with open('../data/schemas.pkl', 'rb') as f:
        schemaDic = pickle.load(f)
    with open('../data/reactions.pkl', 'rb') as f:
        reactionDic = pickle.load(f)


    # Parsing the example stories
    with open(path, "r") as fIn:
        lines = fIn.readlines()
    stories = []
    story = []
    for idx, line in enumerate(lines):

        if "The End" in line:
            stories.append(story)
            story = []
        elif "|" in line:
            line = tuple(line.strip().split("|"))
            story.append(line)
        elif "#" not in line:
            line = (0,line.strip())
            story.append(line)

    for idx, sentence in enumerate(story[1:-1]):
        sent = sentence[0]
        if sent:
            sent = sentence[0]#.replace("A_","").replace("_A","").replace("B_","").replace("_B","")
        story[idx] = (sent,sentence[1])

    # select a story                                            
    story = stories[0]

    # evaluate story
    action_parts = []
    for idx, element in enumerate(story):
        if idx == 0:
            intro = element[1]
                                                               
        if 0 not in element:
            action = element[0]
            sentence = element[1]

            action_key = action.split(" ")[1]
            schema = schemaDic[action_key]
            reaction = reactionDic[action_key]

            # Chose speaker
            if action.startswith("A") or action.endswith("B"):
                speaker = "A"
            elif action.startswith("B") or action.endswith("A"):
                speaker = "B"
            else:
                speaker = "A"

            subject = action[0]
            object  = action[-1]

            action = action.split(" ")[1]

            highest_reaction = [int(reaction[0]),int(reaction[1])].index(max([int(reaction[0]),int(reaction[1])],key=abs))
            if highest_reaction:
                reactor = object
                enactor = subject
            else:
                reactor = subject
                enactor = object

            #print("Sentence: ", sentence)
            #print("Action: ", action, "Schema: ", schema, "Reaction: ", reaction)
            #print("Speaker: ", speaker, "Reactor: ", reactor, "Enactor: ", enactor)
            #print
            action_parts.append([speaker, sentence, action, enactor, schema, reactor, reaction[highest_reaction]])
    return action_parts

#parse_story("../data/example_story.txt")
#parse_dialog("../data/example_dialog.txt")