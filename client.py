import sys
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ClientFactory as ClFactory
from twisted.protocols.basic import Int32StringReceiver
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog,QPlainTextEdit
import pickle
import chat
import os

class Client(Int32StringReceiver):

    factory: 'ClientFactory'
    def connectionMade(self):
        self.factory.window.client = self

    def stringReceived(self, string):
        data = pickle.loads(string)
        if 'mess' in data:
            self.factory.window.get_mess(data)
        elif 'spisok' in data:
            self.factory.window.get_spisok(data)
        elif 'messf' in data:
            self.factory.window.get_file(data)
        else:
            pass


    def send_data(self,mess):
        mess = pickle.dumps(mess)

        self.sendString(mess)
class ClientFactory(ClFactory):
    window: 'MyWindowClass'
    protocol = Client
    def __init__(self,app_window):
        self.window = app_window
        self.protocol.MAX_LENGTH = 99999999


    def clientConnectionFailed(self, connector, reason):
        print(reason)


    def clientConnectionLost(self, connector, reason):
        print(reason)


class MyWindowClass(QMainWindow, chat.Ui_MainWindow):
    client: 'Client'
    reactor = None
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_handlers()
        self.name = ''
        self.d = dict()
        self.progressBar.setValue(0)
    def init_handlers(self):
        self.pushButton.clicked.connect(self.send_mess)
        self.pushButton_2.clicked.connect(self.send_file)
        self.buttonBox.accepted.connect(self.send_name)
        self.pushButton_3.clicked.connect(self.sendf)
        self.pushButton_4.clicked.connect(self.clear)
    def clear(self):
        self.listWidget.clearSelection()
    def send_name(self):
        mess = self.lineEdit_2.text()
        if len(mess) >0:
            self.lineEdit_2.setText('')
            self.name = mess
            d = dict()
            d['user'] = mess
            self.client.send_data(d)
        else:
            self.plainTextEdit.appendPlainText('Имя не было введено!')
    def send_mess(self):
        message = self.lineEdit.text()

        if self.listWidget.selectedItems():
            q = self.listWidget.selectedItems()[0].text()
        else:
            q = ''
        if len(message) > 0:
            d = dict()
            d['mess'] = message
            d['client'] = ''
            d['nameg'] = q
            self.client.send_data(d)
            self.lineEdit.setText('')
        else:
            self.plainTextEdit.appendPlainText('Empty message')
    def send_file(self):
        options = QFileDialog.Options()
        fileName,_ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*)", options=options,)
        if fileName:
            self.lineEdit_3.setText('')
            self.progressBar.setValue(0)
            file_size = os.path.getsize(fileName)
            s_file_size = 0
            l = []
            s = fileName.split('/')
            s = s[-1]
            self.lineEdit_3.setText(s)
            s_send= ''

            if self.listWidget.selectedItems():
                q = self.listWidget.selectedItems()[0].text()
            else:
                q=''
            f = open(fileName,'rb')
            while s_send!=b'':
                s_send = f.read(2048)
                s_file_size+=len(s_send)
                self.progressBar.setValue(int(s_file_size/file_size*100))
                l.append(s_send)
            f.close()
            self.d['messf'] = {
                'names' : self.name,
                'namef' : s,
                'f' : l,
                'nameg': q
            }
    def sendf(self):
        self.client.send_data(self.d)
        self.progressBar.setValue(0)
        self.lineEdit_3.setText('')
        if self.d['messf']['nameg'] == '':
            self.plainTextEdit.appendPlainText(
                f"Вы отправили {self.d['messf']['namef']} всем пользователям")
        else:
            self.plainTextEdit.appendPlainText(f"Вы отправили {self.d['messf']['namef']} пользователю {self.d['messf']['nameg']}")
    def get_mess(self,mess):
        if self.name == mess['client']:
            self.plainTextEdit.appendPlainText(f"You: {mess['mess']}")
        else:
            self.plainTextEdit.appendPlainText(f"{mess['client']}: {mess['mess']}")
    def get_spisok(self,data):
        self.listWidget.clear()
        self.listWidget.addItems(data['spisok'])
    def get_file(self,data):
        options = QFileDialog.Options()
        fileName = QFileDialog.getExistingDirectory(self)
        print(fileName)

        f1 = open(fileName+'/'+data['messf']['namef'],'wb')
        for i in data['messf']['f']:
            f1.write(i)
        f1.close()

        self.plainTextEdit.appendPlainText(f"{data['messf']['names']} отправил вам файл {data['messf']['namef']}")



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    import qt5reactor
    qt5reactor.install()
    myWindow = MyWindowClass()
    myWindow.show()
    from twisted.internet import reactor
    reactor.connectTCP(
        '192.168.0.8',
        4000,
        ClientFactory(myWindow)
    )
    myWindow.reactor = reactor
    reactor.run()


