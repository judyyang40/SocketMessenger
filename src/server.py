#!/usr/bin/python
import socket, select, sys, string, time, base64, os

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

def broadcast_data (sock, message):
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except :
                # broken socket connection may be, chat client pressed ctrl+c for example
                socket.close()
                CONNECTION_LIST.remove(socket)

passtodec = "computernetwork"
  
if __name__ == "__main__":
      
    CONNECTION_LIST = []    # list of socket clients
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    PORT = 2014
         
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    #server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)
 
    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)
 
    print "Chat server started on port " + str(PORT)
    i=0
    j=99
    addr_array=[]
    fd=[]
    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
 
        for sock in read_sockets:
             
            #New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection received through server_socket
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                fd.append(sockfd.fileno())
                print "Client (%s, %s) connected" % addr
                i = i + 1
                 
            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    data = sock.recv(RECV_BUFFER)
                    # echo back the client message
                    if data:
                        data = decode(passtodec, data)
                        crap = data.split()
                        j=0;
                        #new user logged on
                        if crap[0] == "username":
                            print "username: "+ crap[1]
                            currentfd = sock.fileno()
                            for index in range(len(fd)):
                                if currentfd==fd[index]:
                                    j=index
                            log = open("log.txt", "a+")
                            log.write(crap[1]+" %d\n" %j)
                            log.close()
                            #search for any offline msgs
                            readmsg = open("offline.txt", "r")
                            lines = readmsg.readlines()
                            readmsg.close()
                            #print "done reading"
                            writeback = open("offline.txt", "w")
                            #print "open file for writing"
                            for line in lines:
                                ids = line.split()
                                if ids[1]==crap[1]:
                                    print ids[1]
                                    tosend = ids[0]+": "+line[len(ids[0])+len(ids[1])+1:]
                                    CONNECTION_LIST[j+1].send(encode(passtodec, tosend))
                                    print "sent: "+tosend
                                else:
                                    writeback.write(line)
                            writeback.close()

                        elif crap[0]=="close":
                            sock.close()
                        elif crap[0]=="LOGOUT":
                            readmsg = open("log.txt", "r")
                            lines = readmsg.readlines()
                            readmsg.close()
                            #print "lines: "
                            #print lines
                            updatelog = open("log.txt","w")
                            random = -1
                            #print "opened log to write"
                            for line in lines:
                                fdlogout = line.split()
                                #print fdlogout[1]
                                #print fd[int(fdlogout[1])]
                                if sock.fileno()==fd[int(fdlogout[1])]:
                                    random = fdlogout[1]
                                    #print random
                                else:
                                    if random<0:
                                        #print "random < 0"
                                        updatelog.write(line)
                                    else:
                                        #print "ranom <fdlogout[1]"
                                        n = int(fdlogout[1])-1
                                        newlog = fdlogout[0]+" "+str(n)+"\n"
                                        #print newlog
                                        updatelog.write(newlog)
                            update.close()
                            fd.remove(sock.fileno())
                            sock.close()
                            #CONNECTION_LIST.remove(sock)
                        else:
                            otherperson = crap[0]
                            sender = " "
                            foundflag=0
                            contact = open("log.txt", "r")
                            for line in contact:
                                stat = line.split()
                                if otherperson==stat[0]:
                                    dest = int(stat[1])+1
                                    foundflag=1
                                elif sock.fileno()==fd[int(stat[1])]:
                                    sender=stat[0]
                            if foundflag==1:
                                msg=": "+data[len(otherperson)+1:]
                                senddata = encode(passtodec, sender+msg)
                                CONNECTION_LIST[dest].send(senddata)
                            #if cannot find user in log.txt, means that user is not online
                            elif foundflag==0:
                                #print data
                                offline = open("offline.txt", "a+")
                                now = time.asctime(time.localtime(time.time()))
                                data = data.replace("\n", "   ")
                                offmsg = sender+" "+data+now+"\n"
                                offline.write(offmsg)
                                offline.close()
                            #sock.send('OK ... ' + data)
                # client disconnected, so remove from socket list
                except:
                    broadcast_data(sock, "Client (%s, %s) is offline" % addr)
                    print "Client (%s, %s) is offline" % addr
                    #sock.close()
                    CONNECTION_LIST.remove(sock)
                    continue
         
    server_socket.close()