#!/usr/bin/python
import socket, select, string, sys, time, base64

def encode(key, data):
	enc = []
	for i in range(len(data)):
		key_c = key[i%len(key)]
		enc_c = chr((ord(data[i])+ord(key_c))%256)
		enc.append(enc_c)
	return base64.urlsafe_b64encode("".join(enc))

def decode(key, enc):
	dec = []
	enc = base64.urlsafe_b64decode(enc)
	for i in range(len(enc)):
		key_c = key[i%len(key)]
		dec_c = chr((256+ord(enc[i])-ord(key_c))%256)
		dec.append(dec_c)
	return "".join(dec)

def search(newname):
	info_2 = open("info.txt", "r")
	for line in info_2:
		tokens = line.split()
		if newname==tokens[0]:
			newname = raw_input("Username already used, please try again\n")
			search(newname)
	info_2.close()
	return newname

def newusr():
	info = open("info.txt", "a+")
	newname = raw_input("type in username\n")
	newname = search(newname)
	info.write(newname+" ")
	usrname = newname
	newpass = raw_input("type in password\n")
	info.write(newpass+"\n")
	info.close()
	
def login(usrname):
	flag = 0
	info = open("info.txt", "r")
	for line in info:
		tokens = line.split()
		if usrname==tokens[0] : 
			flag = 1
			password = tokens[1]

	if flag==0:
		usrname = raw_input("Username does not exist, please try again or type 'new' to register\n")
		register = "new"
		if usrname == register:
			newusr()
		else:
			login(usrname)
	else:
		passwordfunc(password)
		info.close()
		
def passwordfunc(password):	
	pw = raw_input("Password: ")
	if pw == password:
		print "Welcome"
	else:
		print "Incorrect password, please try again"
		passwordfunc(password)
		
usrname = raw_input("Username or type in 'new' to register\n")
register = "new"	
if usrname==register: 
	newusr()
	
else:
	login(usrname)

host = "localhost"
port = 2014
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)
 
# connect to remote host
try :
	s.connect((host, port))
except :
	print 'Unable to connect'
	sys.exit()
 
print 'Connected to remote host'

passtoenc = "computernetwork" 
firstmsg = "username "+usrname+"\n"
s.send(encode(passtoenc, firstmsg))
histfile = usrname+".txt"

while 1:
	socket_list = [sys.stdin, s]
	 
	# Get the list sockets which are readable
	read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
	for sock in read_sockets:
		#incoming message from remote server
		if sock == s:
			data = sock.recv(4096)
			if not data :
				print 'Connection closed'
				sys.exit()
			else :
				demsg = decode(passtoenc, data)
				hist = open(histfile, "a+")
				now = time.asctime(time.localtime(time.time()))
				towrite = now+"    "+demsg+"\n"
				hist.write(towrite)
				hist.close()
				sys.stdout.write(demsg)
		 
		#user entered a message
		else :
			msg = sys.stdin.readline()
			hist = open(histfile, "a+")
			now = time.asctime(time.localtime(time.time()))
			cutoff = msg.split()
			if msg=="Query\n":
				convo = msg
			else:
				convo = msg[len(cutoff[0])+1:]
			towrite = now+"    "+convo
			hist.write(towrite)
			hist.close()
			if msg=="Query\n":
				qhist = open(histfile, "r")
				print "-----Historical records for "+usrname+"----"
				with open(histfile, "r") as fin:
					print fin.read()
			else:
				enmsg = encode(passtoenc, msg)
				s.send(enmsg)

