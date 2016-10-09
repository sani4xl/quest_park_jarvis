#/usr/bin/env python

import os
import sys
import thread
import threading
import urlparse
import re
import json
import random
#import vlc
import pygame
import time
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

#if not os.getegid() == 0:
#	sys.exit('no root')


from pyA20.gpio import gpio
from pyA20.gpio import connector
from pyA20.gpio import port
from time import sleep

elementsPoolJson = """[
{
 "id" : "led1",
 "title" : "LED 1",
 "port": "PA7",
 "io": "OUTPUT",
 "state" : false
}
]""";

modulesPoolJson = """[
{
 "id" : "module1",
 "title" : "module 1",
 "activate" : 0
}
]""";



#mp3Instance = vlc.Instance()
#mp3Player = mp3Instance.media_player_new()
#media = mp3Instance.media_new('win.mp3')
#mp3Player.set_media(media)
#mp3Player.play()
pygame.mixer.init()
SONG_END = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(SONG_END)
pygame.mixer.music.set_volume(0.5) # 50% volume
#pygame.mixer.music.load("audio/soundtrack/win.mp3")
#pygame.mixer.music.play()

#time.sleep(2)
#pygame.mixer.music.load("audio/soundtrack/sound1.mp3")
#pygame.mixer.music.play()
#effect = pygame.mixer.Sound('audio/sound/hit_button.wav');
#effect.play()
#time.sleep(5)
#sys.exit()
_current_playing_track = None
_tracks_are_playing = False

_tracks_library = {}
def addTrackToLibrary(trackId, initPath):
	global _tracks_library	
	path = _tracks_library.get(trackId)
	if path == None:
		_tracks_library[trackId] = initPath
	return initPath

def playTrackById(trackId):	
	global _current_playing_track
	global _tracks_library	
	global _tracks_are_playing
	path = _tracks_library.get(trackId)
	pygame.mixer.music.stop()
	if path != None:		
		_current_playing_track = trackId
		pygame.mixer.music.load(path)
		pygame.mixer.music.play()
		#_tracks_are_playing = True

	
def playCurrentTrack():
	global _current_playing_track
	playTrackById(_current_playing_track)

addTrackToLibrary('win', "audio/soundtrack/win.mp3")
addTrackToLibrary('track1', "audio/soundtrack/sound1.mp3")
addTrackToLibrary('track2', "audio/soundtrack/sound2.mp3")
#_current_playing_track = 'win'
#playCurrentTrack()

playTrackById('win')
# SOUNDS
_sounds_library = {}
def addSoundToLibrary(trackId, initPath):
	global _sounds_library	
	sound = _sounds_library.get(trackId)
	if sound == None:
		sound = pygame.mixer.Sound(initPath);
		_sounds_library[trackId] = sound
	return sound

def playSoundById(trackId):	
	global _sounds_library	
	sound = _sounds_library.get(trackId)
	if sound != None:
		sound.play()
	
addSoundToLibrary('hit_button', "audio/sound/hit_button.wav")

	

#time.sleep(10)
#sys.exit()

modulesPool  = json.loads(modulesPoolJson)

elementsPool = json.loads(elementsPoolJson)
led = port.PA7
button = port.PA8
buttonState = False

gpio.init()


#gpio.setcfg(port.PA7, gpio.OUTPUT)
gpio.setcfg(button, gpio.INPUT)
#gpio.output(port.PA7, gpio.HIGH)
#sleep(1)
#gpio.output(port.PA7, gpio.LOW)

for element in elementsPool:
	element_port = element['port']
	gpioPort = getattr(port, element_port)
	gpio.setcfg( gpioPort, gpio.OUTPUT)
	#gpio.setcfg(button, gpio.INPUT)
	gpio.output(gpioPort,  gpio.HIGH if element['state'] else gpio.LOW)
	

def setPortValue(element_port, value):
	gpioPort = getattr(port, element_port)
	gpio.output(gpioPort,  value)

def getElementById(elementId):
	global elementsPool
	currentElement = filter(lambda element: element['id'] == elementId, elementsPool)[0]
	return currentElement


#sys.exit()

#gpio.pullup(button, gpio.PULLUP)

def doTracks():
	global _current_playing_track
	global _tracks_are_playing

	while True:
		k = 1
		if _tracks_are_playing and not pygame.mixer.music.get_busy():
				
			
			next_track = random.choice(  _tracks_library.keys() )
			while next_track == _current_playing_track:
				next_track = random.choice(  _tracks_library.keys() )			
			print(next_track)
			playTrackById(next_track)
		elif pygame.mixer.music.get_busy():
			_tracks_are_playing = True
		
			#playCurrentTrack()

		#	print(event.type)

def ioListen():
	global buttonState
	try:
		print("ctr+c to break")
		while True:
			state = gpio.input(button)
			#print(state)
			if state:
				currentElement = getElementById('led1')
				currentElement['state'] = 0 if currentElement['state'] else 1
				setPortValue(currentElement['port'], gpio.HIGH if currentElement['state'] else gpio.LOW)


				# buttonState:
				#gpio.output(port.PA7, gpio.LOW)
				#buttonState = False
				#else:
				#	gpio.output(port.PA7, gpio.HIGH)
				#	buttonState = True
			sleep(0.4)


	except KeyboardInterrupt:
	  print("bye")


def doServer():

	class HttpProcessor(BaseHTTPRequestHandler):
		def do_HEAD(self):
			self.send_response(200)
			self.send_header('content-type','text/html')
			self.end_headers()

		def do_GET(self):
			global buttonState
			parsed_path = urlparse.urlparse(self.path)
			url_path = parsed_path.path
			queryParams = dict(urlparse.parse_qsl(parsed_path.query))
		
			print parsed_path
			print queryParams

			self.send_response(200)
			self.send_header("Access-Control-Allow-Origin","*");
			self.send_header("Access-Control-Allow-Expose-Headers","Access-Control-Allow-Origin");
			self.send_header("Access-Control-Allow-Headers","Origin, X-Requested-With, Content-Type, Accept");

			#self.send_header('content-type','text/html')
			#self.end_headers()
			#self.wfile.write("hello")
			output = "";
			if re.match( r'.*\.(html|html|js|css|jpeg|jpg|png|gif)$', url_path, re.M|re.I):
				self.send_header('content-type','text/html')
				relative_url_path = re.sub( r'^\/', '', url_path)
				#self.wfile.write(relative_url_path)
				with open(relative_url_path, 'r') as adminFile:
					data = adminFile.read()
					#self.wfile.write(data)
					output = data

			
			elif url_path == '/get_tracks':
				global _tracks_library	
				self.send_header('content-type','applicaiton/json')
				response = {}
				response['tracks'] = _tracks_library
				output = json.dumps(response)
			elif url_path == '/get_sounds':
				global _sounds_library	
				self.send_header('content-type','applicaiton/json')
				response = {}
				response['sounds'] = _sounds_library.keys()
				output = json.dumps(response)
			elif url_path == '/current_track':
				global _tracks_library	
				global _current_playing_track
				#self.send_header('content-type','applicaiton/json')
				self.send_header('content-type','text/html')

				#response = {}
				#response['tracks'] = _tracks_library
				output = _current_playing_track
				#json.dumps(response)

			elif url_path == '/get_controls':
				self.send_header('content-type','application/json')
				response = {}
				response['controls'] = elementsPool	
				output =  json.dumps(response)

			elif url_path == '/get_modules':
				self.send_header('content-type','application/json')
				response = {}
				response['modules'] = modulesPool	
				output =  json.dumps(response)
			
			elif url_path == '/switch_state':			
				#currentElement = (element for element in elementsPool if element['id'] == queryParams['id']).next()
				currentElement = filter(lambda element: element['id'] == queryParams['id'], elementsPool)[0]
				#print queryParams['id']
				print currentElement
				currentElement['state'] = int(queryParams['state'])
				setPortValue(currentElement['port'], gpio.HIGH if currentElement['state'] else gpio.LOW)
				output = "done"

			elif url_path == '/activate_module':			
				#currentElement = (element for element in elementsPool if element['id'] == queryParams['id']).next()
				module = filter(lambda element: element['id'] == queryParams['id'], modulesPool)[0]
				#print queryParams['id']
				print module
				module['activate'] = int(queryParams['state'])
				#setPortValue(currentElement['port'], gpio.HIGH if currentElement['state'] else gpio.LOW)
				output = "done"

			elif url_path == '/module-info':
				module = filter(lambda element: element['id'] == queryParams['id'], modulesPool)[0]
				print module
				output =  json.dumps(module)

			elif url_path == '/set_volume':			
				newVolume = float(queryParams['volume'])
				pygame.mixer.music.set_volume(newVolume) # in percent 0 to 1.0

			elif url_path == '/play_track':			
				global _tracks_are_playing
				_tracks_are_playing = False
				pygame.mixer.music.stop()				
				playTrackById(queryParams['trackId'])				
				output = "playing_track"
			elif url_path == '/stop_track':			
				global _tracks_are_playing
				_tracks_are_playing = False
				pygame.mixer.music.stop()								
				output = "track_stopped"
			elif url_path == '/play_sound':							
				playSoundById(queryParams['trackId'])				
				output = "done"

			elif url_path == '/turn':
				if buttonState:
					gpio.output(port.PA7, gpio.LOW)
					buttonState = False
				else:
					gpio.output(port.PA7, gpio.HIGH)
					buttonState = True
			self.end_headers()
			self.wfile.write(output)
			
			

	serv = HTTPServer(('', 8080),HttpProcessor)
	serv.serve_forever()
	print "server started"


def doStart():
#try:
	#thread.start_new_thread(doServer())
	#thread.start_new_thread(ioListen())
	t2 = threading.Thread(target=doServer)
	t1 = threading.Thread(target=ioListen)
	t3 = threading.Thread(target=doTracks)
	
	t1.daemon = True
	t2.daemon = True
	t3.daemon = True
	t2.start()
	t1.start()
	t3.start()
		  
#except:
#	print "error with threading"

doStart()

while 1:
	pass

#sleep(2)
#gpio.output(port.PA7, gpio.LOW)
