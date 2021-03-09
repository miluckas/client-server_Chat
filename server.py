from twisted.internet import reactor
from twisted.internet.protocol import Protocol, connectionDone
from twisted.internet.protocol import ServerFactory as ServFactory
from twisted.protocols.basic import Int32StringReceiver
from twisted.internet.endpoints import TCP4ServerEndpoint

import pickle

class Server(Int32StringReceiver):
    def __init__(self,users):
        self.users = users
        self.name = ""
        self.MAX_LENGTH = 99999999


    def connectionMade(self):
        print("New connection")


    def add_user(self,name):
        if name not in self.users.values():
            self.users[self] = name
            self.name = name
            print(self,name,self.users)
        else:
            d = dict()
            d['mess'] = 'Wrong username? try another'
            d['client'] = 'System'
            self.sendString(pickle.dumps(d))
    def stringReceived(self, string):
        print(4)
        data = pickle.loads(string)
        if 'user' in data:
            self.add_user(data['user'])
            d = dict()
            d['spisok'] = [i for i in self.users.values()]
            for protocol in self.users.keys():
                protocol.sendString(pickle.dumps(d))
        elif 'mess' in data:
            if data['nameg'] != self.name and data['nameg'] != '':
                for protocol in self.users.keys():
                    if data['nameg'] == self.users[protocol]:
                        data['client'] = self.name
                        protocol.sendString(pickle.dumps(data))
            elif data['nameg'] == self.name:
                d = dict()
                d['mess'] = "Can't send yourself a message"
                d['client'] = 'System'
                self.sendString(pickle.dumps(d))
            else:
                for protocol in self.users.keys():
                    data['client'] = self.name
                    protocol.sendString(pickle.dumps(data))
        elif 'messf' in data:
            if data['messf']['nameg'] != self.name and data['messf']['nameg'] != '':
                for protocol in self.users.keys():
                    if data['messf']['nameg'] == self.users[protocol]:
                        protocol.sendString(pickle.dumps(data))
            elif data['messf']['nameg'] == self.name:
                d = dict()
                d['mess'] = "Can't send yourself a file"
                d['client'] = 'System'
                self.sendString(pickle.dumps(d))
            else:
                for protocol in self.users.keys():
                    if protocol != self:
                        protocol.sendString(pickle.dumps(data))
        else:
            pass



    def connectionLost(self, reason=connectionDone):
        del self.users[self]


class ServerFactory(ServFactory):
    def __init__(self):
        self.users = {}

    def buildProtocol(self, addr):
        return Server(self.users)

if __name__ == '__main__':
    reactor.listenTCP(4000, ServerFactory())
    reactor.run()

