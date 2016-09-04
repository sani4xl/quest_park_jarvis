#/usr/bin/env python

import os
import sys
import thread
import threading
import urlparse
import re
import json
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

elementsPool = json.loads(elementsPoolJson)
led = port.PA7
button = port.PA8
buttonState = False

gpio.init()


#gpio.setcfg(port.PA7, gpio.OUTPUT)
#gpio.setcfg(button, gpio.INPUT)
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


#sys.exit()

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

			elif url_path == '/get_controls':
				self.send_header('content-type','application/json')
				response = {}
				response['controls'] = elementsPool	
				output =  json.dumps(response)
				#self.wfile.write(jsonString)
			elif url_path == '/switch_state':			
				#currentElement = (element for element in elementsPool if element['id'] == queryParams['id']).next()
				currentElement = filter(lambda element: element['id'] == queryParams['id'], elementsPool)[0]
				#print queryParams['id']
				print currentElement
				currentElement['state'] = int(queryParams['state'])
				setPortValue(currentElement['port'], gpio.HIGH if currentElement['state'] else gpio.LOW)
				ouput = "done"
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
