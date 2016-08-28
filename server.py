#/usr/bin/env python

import os
import sys
import thread
import threading
import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

#if not os.getegid() == 0:
#	sys.exit('no root')


from pyA20.gpio import gpio
from pyA20.gpio import connector
from pyA20.gpio import port
from time import sleep

led = port.PA7
button = port.PA8
buttonState = False

gpio.init()


gpio.setcfg(port.PA7, gpio.OUTPUT)
gpio.setcfg(button, gpio.INPUT)

#gpio.pullup(button, gpio.PULLUP)

def ioListen():
	global buttonState
	try:
		print("ctr+c to break")
		while True:
			state = gpio.input(button)
			#print(state)
			if state:
				if buttonState:
					gpio.output(port.PA7, gpio.LOW)
					buttonState = False
				else:
					gpio.output(port.PA7, gpio.HIGH)
					buttonState = True
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

			self.send_response(200)
			self.send_header('content-type','text/html')
			self.end_headers()
			self.wfile.write("hello")
			if url_path == '/turn':
				if buttonState:
					gpio.output(port.PA7, gpio.LOW)
					buttonState = False
				else:
					gpio.output(port.PA7, gpio.HIGH)
					buttonState = True


	serv = HTTPServer(('', 8080),HttpProcessor)
	serv.serve_forever()
	print "server started"


def doStart():
#try:
	#thread.start_new_thread(doServer())
	#thread.start_new_thread(ioListen())
	t2 = threading.Thread(target=doServer)
	t1 = threading.Thread(target=ioListen)
	t1.daemon = True
	t2.daemon = True
	t2.start()
	t1.start()
		  
#except:
#	print "error with threading"

doStart()

while 1:
	pass

#sleep(2)
#gpio.output(port.PA7, gpio.LOW)
