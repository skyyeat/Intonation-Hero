#Intonation Hero Utils

import rec_lib
import Constants

#Write High Score
def WriteScore(scene, score):
    hiscore = scene.hiscore

    #Get line number
    n = scene.sectionno
    for x in range(scene.chapterno-1):
        secs = rec_lib.sect_enum("IE_" + str(x+1))
        for z in secs:
            n += 1

    file = open("savefile.txt", "r")
    olds = []
    line = []
    olde = []

    #count up to right line
    i = 1
    for lin in file:
        if i < n:
            olds += lin
        if i == n:
            line += lin
        if i > n:
            olde += lin
        i+= 1

    #Write the new line
    ex = scene.exerciseno
    exs = 0
    if rec_lib.repdep("IE_" + str(scene.chapterno)+"."+str(scene.sectionno)) == 0:
        for r in rec_lib.ex_enum("IE_" + str(scene.chapterno)+"."+str(scene.sectionno)):
            exs+=1
    if rec_lib.repdep("IE_" + str(scene.chapterno)+"."+str(scene.sectionno)) == 1:
        for r in range(round(len(rec_lib.ex_enum("IE_" + str(scene.chapterno)+"."+str(scene.sectionno)))/2)):
            exs+=1

    last = 0
    str1 = ''.join(line)
    newline = ""
    
    for t in range(ex):
        last = str1.find(",", last+1)

    start = str1[:len(str1)-len(str(hiscore))-2]
    end = "]\n"
    if last > 0:
        start = str1[:last-len(str(hiscore))]
        end = str1[last:]
    
    newline = start + str(score) + end
    
    #If the new score is higher than the saved high score, save the new score
    if score > hiscore:
        n=0
        save = open("savefile.txt", "w")
        for l in olds:
            save.write(l)
            n+=1
        save.write(newline)
        n+=1
        for l in olde:
            save.write(l)
            n+=1
        save.close() 

#Get High Score
def get_hiscore(scene):
    file = open("savefile.txt", "r")
        
    n = scene.sectionno
    for x in range(scene.chapterno-1):
        secs = rec_lib.sect_enum("IE_" + str(x+1))
        for z in secs:
            n += 1

    lst = []
    for l in range(n):
        lst = file.readline()

    ex = scene.exerciseno
    last = 0
    score = 0
    first = lst.find(",")

    for x in range(ex):
        score = lst[last+1:first]
        if first == -1:
            score = lst[last+1:len(lst)-2]
            return int(score)
        last = first
        first = lst.find(",", first+1)

    return int(score) 

def get_hi(chap, sec, ex):
    file = open("savefile.txt", "r")
        
    n = sec
    for x in range(chap-1):
        secs = rec_lib.sect_enum("IE_" + str(x+1))
        for z in secs:
            n += 1

    lst = []
    for l in range(n):
        lst = file.readline()

    last = 0
    score = 0
    first = lst.find(",")

    for x in range(ex):
        score = lst[last+1:first]
        if first == -1:
            score = lst[last+1:len(lst)-2]
            return int(score)
        last = first
        first = lst.find(",", first+1)

    return int(score) 


def chapset(scene, n):
    scene.chapterselected = n
    scene.sectionselected = 0
    scene.exerciseselected = 0

def secset(scene, n):
    scene.exerciseselected = 0
    scene.sectionselected = n

def exset(scene, n):
    scene.exerciseselected = n

def setselect(scene, n):
    scene.setselect = True

def hiselect(scene, n):
    scene.hiselect = True

def menuselect(scene, n):
    scene.menuselect = True

def speedselect(scene, n):
    scene.gamespeed = n
    Constants.SPEED = n
    rec_lib.write_settings(n, Constants.SPEAKER)

def newselect(scene, b):
    scene.newselect = True

def recordselect(scene, n):
    scene.record = True

def upselect (scene, n):
	if 400 > Constants.SPEAKER >= 50:
	    rec_lib.write_settings(Constants.SPEED, Constants.SPEAKER + 5)
	    Constants.SPEAKER += 5
	    scene.f0 = Constants.SPEAKER
	else:
		pass

def downselect (scene, n):
	if 400 >= Constants.SPEAKER > 50:
	    rec_lib.write_settings(Constants.SPEED, Constants.SPEAKER - 5)
	    Constants.SPEAKER -= 5
	    scene.f0 = Constants.SPEAKER
	else:
		pass

def nullselect (scene, n):
    pass

def newgame(scene, b):
    scene.newgame = True
    Constants.SPEAKER = 0
    Constants.SPEED = 3
    rec_lib.write_settings(3, 0)
    rec_lib.write_saves(scene)