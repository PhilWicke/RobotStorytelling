import datetime
import wave
import contextlib

class srt_maker():

    start_time = 0
    counter = 0
    lines = ""

    def __init__(self):
        self.start_time = datetime.datetime.now()

    def get_duration(self, path):
        with contextlib.closing(wave.open(path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            return duration

    def add_srt(self, line):

        # add line breaks to lines
        lines = ""
        indent_count = 0
        for symbol in line:
            if indent_count > 40 and symbol == " ":
                lines = lines + "\n"
                indent_count = 0
            else:
                lines = lines + symbol
            indent_count += 1

        self.counter += 1
        self.lines = self.lines + str(self.counter) + "\n"

        # format timestamp
        now_time = datetime.datetime.now()

        timestamp_now = now_time - self.start_time
        timestamp = "0" + str(timestamp_now).replace(".", ",")[:11]

        # get duration of current sound file
        dur = str(self.get_duration("temp.wav"))

        # evaluate elapsed time and add it
        elapsed_time = datetime.timedelta(seconds=int(dur.split(".")[0]), milliseconds=int(dur.split(".")[1][:3]))
        elapsed_stamp =  "0" + str(str(elapsed_time+timestamp_now).replace(".", ",")[:11])

        self.lines = self.lines + str(timestamp) + " --> " + elapsed_stamp + "\n"

        # add lines to output
        self.lines = self.lines + lines + "\n\n"

    def print_lines(self):
        print(self.lines)

    def make_srt(self, path):
        with open(path, "w+") as f:
            f.writelines(self.lines)



"""    
1
00:00:01,492 --> 00:00:03,968
The film you will see is the result
of the free Creation of the authors.

2
00:00:03,969 --> 00:00:08,704
The reference to existing people is a Artistic
elaboration without documentary intent.
"""