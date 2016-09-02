from Tkinter import *
from ttk import *
import socket
import thread

class ChatClient(Frame):
  
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
    self.root.title("Client ")
    ScreenSizeX = self.root.winfo_screenwidth()
    ScreenSizeY = self.root.winfo_screenheight()
    #self.FrameSizeX  = 265
    #self.FrameSizeY  = 550
    self.FrameSizeX  = 600
    self.FrameSizeY  = 500
    FramePosX   = (ScreenSizeX - self.FrameSizeX)/2
    FramePosY   = (ScreenSizeY - self.FrameSizeY)/2
    self.root.geometry("%sx%s+%s+%s" % (self.FrameSizeX,self.FrameSizeY,FramePosX,FramePosY))
    self.root.resizable(width=False, height=False)
    
    padX = 10
    padY = 10
    parentFrame = Frame(self.root)
    parentFrame.grid(padx=padX, pady=padY, stick=E+W+N+S)
    
    ipGroup = Frame(parentFrame)
    serverLabel = Label(ipGroup, text="Name:")
    ipLabel = Label(ipGroup, text="IP:")
    portLabel = Label(ipGroup, text="Port:")
    self.nameVar = StringVar()
    self.nameVar.set("Molano")
    nameField = Entry(ipGroup, width=10, textvariable=self.nameVar)

    self.clientIPVar = StringVar()
    self.clientIPVar.set("127.0.0.1")
    clientIPField = Entry(ipGroup, width=15, textvariable=self.clientIPVar)
    self.clientPortVar = StringVar()
    self.clientPortVar.set("9009")
    clientPortField = Entry(ipGroup, width=5, textvariable=self.clientPortVar)
    clientSetButton = Button(ipGroup, text="Connect", width=10, command=self.handleAddClient)
    exitChatButton = Button(ipGroup, text="Exit", width=10, command=self.quit)     
    serverLabel.grid(row=0, column=0)
    ipLabel.grid(row=2, column=0,padx=5)
    portLabel.grid(row=3, column=0,padx=5)
    nameField.grid(row=0, column=1,padx=5)

    clientIPField.grid(row=2, column=1, padx=5)
    clientPortField.grid(row=3, column=1)
    clientSetButton.grid(row=0, column=4, padx=5)
    exitChatButton.grid(row=2, column=4, padx=5)
    
    readChatGroup = Frame(parentFrame)
    self.receivedChats = Text(readChatGroup, bg="white", width=70, height=20, state=DISABLED)
    #self.friends = Listbox(readChatGroup, bg="white", width=30, height=30)
    self.receivedChats.grid(row=0, columnspan=3, sticky=W+N+S, padx = (0,10))
    #self.friends.grid(row=0, column=1, sticky=E+N+S)

    writeChatGroup = Frame(parentFrame)
    self.chatVar = StringVar()
    self.chatField = Entry(writeChatGroup, width=50, textvariable=self.chatVar)
    sendChatButton = Button(writeChatGroup, text="Send", width=10, command=self.handleSendChat)
    self.chatField.grid(row=0, column=0, sticky=W)
    sendChatButton.grid(row=0, column=1, padx=5)

    self.statusLabel = Label(parentFrame)

    bottomLabel = Label(parentFrame, text="")
    
    ipGroup.grid(row=0, column=0)
    readChatGroup.grid(row=1, column=0)
    writeChatGroup.grid(row=2, column=0, pady=10)
    self.statusLabel.grid(row=3, column=0)
    bottomLabel.grid(row=4, column=0, pady=10)
    
  def handleSetServer(self):
    if self.serverSoc != None:
        self.serverSoc.close()
        self.serverSoc = None
        self.serverStatus = 0
    serveraddr = (self.clientIPVar.get().replace(' ',''), int(self.clientPortVar.get().replace(' ','')))
    try:
        self.serverSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSoc.bind(serveraddr)
        self.serverSoc.listen(5)
        self.setStatus("Server listening on %s:%s" % serveraddr)
        thread.start_new_thread(self.listenClients,())
        self.serverStatus = 1
        self.name = self.nameVar.get().replace(' ','')
        if self.name == '':
            self.name = "%s:%s" % serveraddr
    except:
        self.setStatus("Error setting up server")
    
  def listenClients(self):
    while 1:
      clientsoc, clientaddr = self.serverSoc.accept()
      self.setStatus("Client connected from %s:%s" % clientaddr)
      self.addClient(clientsoc, clientaddr)
      thread.start_new_thread(self.handleClientMessages, (clientsoc, clientaddr))
    self.serverSoc.close()
  
  def handleAddClient(self):
    if self.serverSoc != None:
        self.serverSoc.close()
        self.serverSoc = None
        self.serverStatus = 0
    

    self.name = self.nameVar.get() 
    clientaddr = (self.clientIPVar.get().replace(' ',''), int(self.clientPortVar.get().replace(' ','')))
    try:
        clientsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsoc.connect(clientaddr)
        self.setStatus("Connected to client on %s:%s" % clientaddr)
        self.addClient(clientsoc, clientaddr)
        thread.start_new_thread(self.handleClientMessages, (clientsoc, clientaddr))
    except:
        self.setStatus("Error connecting to client")

  def handleClientMessages(self, clientsoc, clientaddr):
    while 1:
      try:
        data = clientsoc.recv(self.buffsize)
        if not data:
            break
        self.addChat("%s:%s" % clientaddr, data)
      except:
          break
    self.removeClient(clientsoc, clientaddr)
    clientsoc.close()
    self.setStatus("Client disconnected from %s:%s" % clientaddr)
  
  def handleSendChat(self):
   
    msg = self.chatVar.get()
    modified_message = "(received from %s)->%s" % (self.name,msg)
    if msg == '':
        return
    #self.addChat("me", msg)
    self.addChat("me", msg)
    for client in self.allClients.keys():
      client.send(modified_message)
    self.chatField.delete(0, 'end')
  def addChat(self, client, msg):
    self.receivedChats.config(state=NORMAL)
    self.receivedChats.insert("end",client+": "+msg+"\n")
    self.receivedChats.config(state=DISABLED)
  
  def addClient(self, clientsoc, clientaddr):
    self.allClients[clientsoc]=self.counter
    self.counter += 1
    #self.friends.insert(self.counter,"%s:%s" % clientaddr)
  
  def removeClient(self, clientsoc, clientaddr):
      print self.allClients
      #self.friends.delete(self.allClients[clientsoc])
      del self.allClients[clientsoc]
      print self.allClients
  
  def setStatus(self, msg):
    self.statusLabel.config(text=msg)
    print msg
      
def main():  
  root = Tk()
  app = ChatClient(root)
  root.mainloop()  

if __name__ == '__main__':
  main() 
