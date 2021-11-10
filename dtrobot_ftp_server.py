from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer
from socket_io_file_client import Client
from dtrobot_reset import Reset
import dtrobot_config as dtrobot
import threading
import time

class Ftp_Server():
    def __init__(self):
        pass
    
    def create_ftp_server(self, fpath):
        authorizer = DummyAuthorizer()
        authorizer.add_user('python', '123456', fpath, perm='elradfmwM')
        handler = FTPHandler
        handler.authorizer = authorizer

        server = FTPServer(('0.0.0.0', 8888), handler)
        server.serve_forever()

if __name__ == '__main__':
    FTP_SERVER = Ftp_Server()
    FILE_CLIETNT = Client()
    DTROBOT_RESET = Reset()
    threads = []
    t_ftp_server = threading.Thread(target = FTP_SERVER.create_ftp_server, args = ('/home/pi/dt_robot/back_up',))
    threads.append(t_ftp_server)
    t_file_client = threading.Thread(target = FILE_CLIETNT.create_client, args = ())
    threads.append(t_file_client)
    for t in threads:
        t.setDaemon(True)
        t.start()
        time.sleep(0.05)
    while True:
        if len(dtrobot.FILE_INFO):
            if dtrobot.FILE_INFO[1] == 0x01:
                DTROBOT_RESET.reset()
            dtrobot.FILE_INFO = []