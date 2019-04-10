import random, csv

vidlist = []
with open('scriptlets/vidlinks.csv', 'r') as f:
    reader = csv.reader(f, delimiter=',')
    vidlink = list(reader)
choice = random.randint(0, len(vidlink))
songtitle = vidlink[choice][1]
songlink = vidlink[choice][0]
print(songtitle, songlink)
