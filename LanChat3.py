#IMPORTS
from threading import Thread, Lock
from socket import *
from re import search
from time import ctime, sleep
from os import system

#GLOBALS
lock = Lock()
_TERMCODE = 'TERMCODE'
_CHECKSTR = 'CHECKSTR'
_BUFFSIZE = 2048
_DEFPORT = 45565
_testing = False#True#

def testlog(*args, pause=False, **kwargs):
    if _testing:
        with lock:
            print(*args, **kwargs)
        if pause: input()

def getIP(): #to find the global IP of the system
    theIP = False
    try:
        sock = socket(2, 1)
        try: 
            sock.bind(('', _DEFPORT))
        except OSError:
            testlog('Unable to obtain Port')
            sock.close();
            return False;
        sock.connect(('stjosephprinting.dx.am', 80)) #Connecting to online server to find ip
        testlog('\nConnected to online server')
        sock.send(bytes('GET http://f21-preview.awardspace.net/stjosephprinting.dx.am/lanchat3.php HTTP/1.1\r\nHost: localhost\r\nConnection: keep-alive\r\nCache-Control: max-age=0\r\nUpgrade-Insecure-Requests: 1\r\nDNT: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36\r\nSec-Fetch-Dest: document\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nSec-Fetch-Site: cross-site\r\nSec-Fetch-Mode: navigate\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.9\r\n\r\n', 'utf-8')); testlog('Request sent')
        data = str(sock.recv(_BUFFSIZE))[2:-1]; testlog('Response received')
        theIP = data[search('lanchat3_ip>>>.*<<<', data).start()+len('lanchat3_ip>>>'):-3].split(':')[0]
        testlog('fetched IP : '+theIP)
    except Exception as e:
        print("Couldn't find your ip.\nIf you are not connected to the internet, only local networking is possible")
        testlog("Exception : "+str(e)+'\n', pause=True)
        theIP = gethostbyname(gethostname())
    finally:
        sock.close()
        return theIP

class Server(Thread):
    def __init__(self, port=_DEFPORT):
        Thread.__init__(self)
        self.clients = [] #messages are forwarded to ips in this list
        self.ip = getIP()
        self.port = port
        self.sock = socket(2, 2)
        try: self.sock.bind(('', self.port))
        except OSError:
            testlog('Port '+_DEFPORT+' is already in use. Terminating')
            self.sock.close()
            return False;
        with lock: print('\nConnect to Master IP : %s'%self.ip)
        self.client = Client('localhost') #starts a client for the master user.
        testlog('Server : client started')
    
    def run(self):
        self.client.start()
        message = ''
        while True:
            testlog('Server : LoopStart')
            data, sender = self.sock.recvfrom(_BUFFSIZE)
            
            testlog('Server : data received')
            if str(data)[2:2+len(_CHECKSTR)] == _CHECKSTR:
                testlog('Server : client initialization '+str(sender))
                self.sock.sendto(bytes(_CHECKSTR, 'utf-8'), sender)
                continue
            elif sender not in self.clients:
                testlog('Server : address registration')
                self.clients.append(sender)
                message = ctime()[11:-5]+' : CONNECTED < '+str(data)[2:-1]+' '+str(sender)
            elif str(data)[2:2+len(_TERMCODE)] == _TERMCODE:
                testlog('Server : Disconnection '+str(sender))
                self.clients.remove(sender)
                message = ctime()[11:-5]+' : DISCONNECTED < '+str(data)[3+len(_TERMCODE):-1]+' '+str(sender)
            else:
                message = ctime()[11:-5]+' : '+str(data)[2:-1]
            
            try:
                testlog('Server : message broadcast to '+str(self.clients))
                for client in self.clients:
                    if client != sender:
                        self.sock.sendto(bytes(message, 'utf-8'), (client[0], client[1]+1))
            except Exception as e:
                with lock: print('Server : Broadcast Error', str(e))
            
            self.sock.close()
            self.sock = socket(2, 2)
            self.sock.bind(('', self.port))
            if not self.clients: break
        try: self.client.join(1.0)
        except:pass
        try: self.sock.close()
        except: pass
        testlog('Server : Terminating', pause=True)

class Client(Thread):
    def __init__(self, serverIP):
        testlog('Press enter to initiate Client', pause=True)
        Thread.__init__(self)
        self.serverIP = serverIP
        self.timeout = 5
        self.username = input('Select a username : ')
        self.sock=socket(2, 2)
        self.sock.sendto(bytes(_CHECKSTR+' '+self.username, 'utf-8'), (self.serverIP, _DEFPORT))
        testlog('Client : Client Listener initialization with port : '+str(self.sock.getsockname()[1]+1))
        self.listener = ClientListener(self.sock.getsockname()[1]+1)
        self.listener.start()
        
    def run(self):
        testlog('Client : server test')
        if str(self.sock.recvfrom(_BUFFSIZE)[0])[2:-1] == _CHECKSTR:
            testlog('Client : Server reached '+self.serverIP+str(_DEFPORT))
        self.sock.sendto(bytes(self.username, 'utf-8'), (self.serverIP, _DEFPORT))
        system('title LANCHAT '+self.username+'@'+self.serverIP+':'+str(_DEFPORT))
        print('\nHello %s, Send messages to the network now. Send a blank text to Exit.\n'%self.username)
        testlog('Client : LoopStart')
        while True:
            data = input()
            if not data:
                testlog('Client : no data detected')
                self.sock.sendto(bytes(_TERMCODE+' '+self.username, 'utf-8'), (self.serverIP, _DEFPORT))
                break;
            else:
                self.sock.sendto(bytes(data+' < '+self.username, 'utf-8'), (self.serverIP, _DEFPORT))
        testlog('Client : listener Termination')
        self.sock.sendto(bytes(_TERMCODE, 'utf-8'), (gethostbyname(gethostname()), self.sock.getsockname()[1]+1)) ##getsockname()[0] for ip ?
        self.listener.join(1.0)
        self.sock.close()

class ClientListener(Thread):
    def __init__(self, listeningport):
        testlog('Client : Listener initializing')
        Thread.__init__(self)
        self.sock = socket(2, 2)
        self.sock.bind(('', listeningport))
        testlog('Client : Listener initialized at '+str(listeningport))
    def run(self):
        while True:
            data, sender = self.sock.recvfrom(_BUFFSIZE)
            if str(data)[2:2+len(_TERMCODE)] == _TERMCODE: break
            with lock: print(str(data)[2:-1])
        self.sock.close()

try:
    servorclient = input('Enter ip of Master\nPress Enter to start Master on this system\n')
    if servorclient == '': UI = Server(); UI.start()
    else: UI = Client(servorclient); UI.start()
    UI.join()
except Exception as e:
    print('\nAn error has occured.\n', e, '\nContact github.com/madhaven', sep='')
    input()
finally:
    try: UI.sock.close()
    except: pass
