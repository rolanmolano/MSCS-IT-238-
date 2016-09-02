from Tkinter import *
from ttk import *
import thread
import sys, socket, select


SOCKET_LIST = [] 
PORT =9

class Server(Frame):

  def __init__(self, root):
    Frame.__init__(self, root)
    self.root = root
    self.initUI()
    self.serverSoc = None
    self.serverStatus = 0
    self.buffsize = 1024
    self.allClients = {}
    self.counter = 0
  
  def initUI(self):
    self.root.title("Server")
    ScreenSizeX = self.root.winfo_screenwidth()
    ScreenSizeY = self.root.winfo_screenheight()
    self.FrameSizeX  = 550
    self.FrameSizeY  = 350
    FramePosX   = (ScreenSizeX - self.FrameSizeX)/2
    FramePosY   = (ScreenSizeY - self.FrameSizeY)/2
    self.root.geometry("%sx%s+%s+%s" % (self.FrameSizeX,self.FrameSizeY,FramePosX,FramePosY))
    self.root.resizable(width=False, height=False)
    
    padX = 10
    padY = 10
    parentFrame = Frame(self.root)
    parentFrame.grid(padx=padX, pady=padY, stick=E+W+N+S)
    
    ipGroup = Frame(parentFrame)
    serverLabel = Label(ipGroup, text="Port #")

    self.serverPortVar = StringVar()
    self.serverPortVar.set("8999")
    serverPortField = Entry(ipGroup, width=5, textvariable=self.serverPortVar)
    serverSetButton = Button(ipGroup, text="Connect", width=10, command=self.click)

    serverLabel.grid(row=0, column=0)

    serverPortField.grid(row=0, column=1)
    serverSetButton.grid(row=0, column=2, padx=5)

    
    readChatGroup = Frame(parentFrame)
    #self.receivedChats = Text(readChatGroup, bg="white", width=60, height=30, state=DISABLED)
    self.friends = Listbox(readChatGroup, bg="white", width=65, height=15)
    #self.receivedChats.grid(row=0, column=0, sticky=W+N+S, padx = (0,10))
    self.friends.grid(row=0, columnspan=3, sticky=E+N+S)


    self.statusLabel = Label(parentFrame)

    bottomLabel = Label(parentFrame, text="")
    
    ipGroup.grid(row=0, column=0)
    readChatGroup.grid(row=2, column=0)
    #writeChatGroup.grid(row=2, column=0, pady=10)
    self.statusLabel.grid(row=3, column=0)
    bottomLabel.grid(row=4, columnspan=3, pady=10)
    
  def click(self):
      global PORT
      PORT = int(self.serverPortVar.get())
      thread.start_new_thread(self.handleSetServer,())
 
  def handleSetServer(self):
        global SOCKET_LIST 
	HOST = '10.0.4.125'
	RECV_BUFFER = 4096 

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
   	server_socket.bind((HOST, PORT))
    	server_socket.listen(10)
        

    	SOCKET_LIST.append(server_socket)
 
    	print "Chat server started on port" + str(PORT)

       
	while 1:


		ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)
	      
		for sock in ready_to_read:

		    if sock == server_socket: 
		        sockfd, addr = server_socket.accept()
		        SOCKET_LIST.append(sockfd)
		        print "Client (%s, %s) connected" % addr
		        self.addClient(sockfd, addr)
		        thread.start_new_thread(self.broadcast,(server_socket, sockfd, "(%s,%s) Connect chat:" % addr))
		     

		    else:
		        # process data recieved from client, 
		        try:
		            # receiving data from the socket.
		            data = sock.recv(RECV_BUFFER)
		            if data:
		                # there is something in the socket
		                thread.start_new_thread(self.broadcast,(server_socket, sock, "\r" + '[' + str(sock.getpeername()) + '] ' + data))  
		            else:
		                # remove the socket that's broken    
		                if sock in SOCKET_LIST:
				    SOCKET_LIST.remove(sock)
			            self.removeClient(sock, addr)
		                    
		                    # at this stage, no data means probably the connection has been broken
		                    thread.start_new_thread(self.broadcast,(server_socket, sock,"Client (%s, %s) is offline\n" % addr)) 
				
		        # exception 
		        except:
			     SOCKET_LIST.remove(sock)
                             thread.start_new_thread(self.broadcast,(server_socket, sock, "Client (%s, %s) is offline\n" % addr))
		             self.removeClient(sock, addr)
			     continue

	server_socket.close()
        

    
  def listenClients(self):
    #while 1:
    #  clientsoc, clientaddr = self.serverSoc.accept()
      self.setStatus("Client connected from %s:%s" % clientaddr)
      self.addClient(clientsoc, clientaddr)
    #  thread.start_new_thread(self.handleClientMessages, (clientsoc, clientaddr))
    #self.serverSoc.close()
    

    #server_socket.close()

  
  def handleAddClient(self):
    if self.serverStatus == 0:
      self.setStatus("Set server address first")
      return
    clientaddr = (self.clientIPVar.get().replace(' ',''), int(self.clientPortVar.get().replace(' ','')))
    try:
        clientsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsoc.connect(clientaddr)
        self.setStatus("Connected to client on %s:%s" % clientaddr)
        thread.start_new_thread(self.broadcast(server_socket, sockfd, "[%s:%s] entered our chatting room" % clientaddr))
        self.addClient(clientsoc, clientaddr)
        thread.start_new_thread(self.handleClientMessages, (clientsoc, clientaddr))
    except:
        self.setStatus("Error connecting to client")

  def handleClientMessages(self, clientsoc, clientaddr):
        SOCKET_LIST =[]
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
   	server_socket.bind((clientaddr, PORT))
    	server_socket.listen(10)
 
    	# add server socket object to the list of readable connections
    	SOCKET_LIST.append(server_socket)
 
    	print "Chat server started on port" + str(PORT)

       
	while 1:

		# get the list sockets which are ready to be read through select
		# 4th arg, time_out  = 0 : poll and never block
		ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)
	      
		for sock in ready_to_read:
		    # a new connection request recieved
		    if sock == server_socket: 
		        sockfd, addr = server_socket.accept()
		        SOCKET_LIST.append(sockfd)
		        print "Client (%s, %s) connected" % addr
		         
		        broadcast(server_socket, sockfd, "[%s:%s] entered our chatting room" % addr)
		     
		    # a message from a client, not a new connection
		    else:
		        # process data recieved from client, 
		        try:
		            # receiving data from the socket.
		            data = sock.recv(RECV_BUFFER)
		            if data:
		                # there is something in the socket
		                broadcast(server_socket, sock, "\r" + '[' + str(sock.getpeername()) + '] ' + data)  
		            else:
		                # remove the socket that's broken    
		                if sock in SOCKET_LIST:
		                    SOCKET_LIST.remove(sock)

		                # at this stage, no data means probably the connection has been broken
		                broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr) 
				
		        # exception 
		        except:
		            broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr)
		            continue

   
  def broadcast (self,server_socket, sock, message):
      global SOCKET_LIST
      for socket in SOCKET_LIST:
          # send the message only to peer
          if socket != server_socket and socket != sock :
              try :
                  socket.send(message)
              except :
                  # broken socket connection
                  socket.close()
                  # broken socket, remove it
                  if socket in SOCKET_LIST:
                      SOCKET_LIST.remove(socket)
 

  def handleSendChat(self):
    if self.serverStatus == 0:
      self.setStatus("Set server address first")
      return
    msg = self.chatVar.get().replace(' ','')
    if msg == '':
        return
    self.addChat("me", msg)
    for client in self.allClients.keys():
      client.send(msg)
  
  #def addChat(self, client, msg):
  def addChat(self,msg):
    self.receivedChats.config(state=NORMAL)
    #self.receivedChats.insert("end",client+": "+msg+"\n")
    self.receivedChats.insert("end",": "+msg+"\n")
    self.receivedChats.config(state=DISABLED)
  
  def addClient(self, clientsoc, clientaddr):
    self.allClients[clientsoc]=self.counter
    self.counter += 1
    self.friends.insert(self.counter,"%s:%s" % clientaddr)
  
  def removeClient(self, clientsoc, clientaddr):
      print self.allClients
      self.friends.delete(self.allClients[clientsoc])
      del self.allClients[clientsoc]
      print self.allClients
  
  def setStatus(self, msg):
    self.statusLabel.config(text=msg)
    print msg
      
def main():  
  root = Tk()
  app = Server(root)
  root.mainloop()  

if __name__ == '__main__':
  main() 
