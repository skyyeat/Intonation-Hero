#Constants.py

def get_speed():
	file = open("settings.txt", "r")
	speed = file.readline()
	i = speed.find(":")
	s = speed[i+2:].find(" ")
	speed = speed[i+2:s]
	return speed

def get_speaker():
	file = open("settings.txt", "r")
	speaker = file.readline()
	speaker = file.readline()
	i = speaker.find(":")
	speaker = speaker[i+2:]
	return speaker

RATE = 44100

CHUNK_SIZE = 1024

WIN_WIDTH = 800

WIN_HEIGHT = 600

HALF_WIDTH = int(WIN_WIDTH / 2)

HALF_HEIGHT = int(WIN_HEIGHT / 2)

SPEED = int(get_speed())

SPEAKER = int(get_speaker())

#COLORS
white = (255,255,255)
black = (0,0,0)
red = (175,0,0)
green = (34,177,76)
yellow = (175,175,0)
blue = (30,144,255)
green_light = (0,255,0)
red_light = (255,0,0)
yellow_light = (255,255,0)
blue_light = (0,191,255)
grey = (211, 211, 211)
