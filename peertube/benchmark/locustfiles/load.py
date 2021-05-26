import os

path = os.path.abspath("../videos")
videos = os.listdir(path)

files = []

for i in range(len(videos)):
    videofile = path +"/" +videos[i]
    f = open(videofile,'rb')
    files.append(f.read())

num_videos=len(files)