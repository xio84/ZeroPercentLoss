import multiprocessing as mp
import socket
from packet import Packet

UDP_IP = "127.0.0.1"
UDP_SEND_PORT = 5005
UDP_RCV_PORT = UDP_SEND_PORT+1
# MESSAGE = bytes(bytearray(b"Hello, World!"))

def file_writer(p, query):
    i = 0
    port = int(bytes(p.data).decode())
    UDP_SEND_PORT = port
    UDP_RCV_PORT = port+1
    sock2 = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    sock2.bind((UDP_IP, UDP_RCV_PORT))
    sock2.settimeout(5)
    f = open('downloads/' + query,'wb')
    res = Packet(1,p.data_id)
    sock2.sendto(res.parse(), (UDP_IP, port))
    data, addr = sock2.recvfrom(32678)
    p = Packet(parsed_bytes=bytearray(data))
    while(p.data_type < 2):
        if (p.sum_checker and p.sequence_number==i):
            f.write(bytes(p.data))
            res = Packet(1,p.data_id)
            sock2.sendto(res.parse(), (UDP_IP, port))
            data, addr = sock2.recvfrom(32678)
            p = Packet(parsed_bytes=bytearray(data))
            i+=1
            if (i==256):
                i=0
    print('Download file : ',query,' has finished')
    f.close()

if __name__=='__main__':
    print ("UDP target IP:", UDP_IP)
    print ("UDP target port:", UDP_SEND_PORT)

    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_RCV_PORT))
    sock.settimeout(5)
    pool = mp.Pool(processes=10)

    while True:
        query=input('Available files:\n 1. pre-rebase.sample\n')
        p = Packet(parsed_data=bytearray(query.encode()))
        sock.sendto(p.parse(), (UDP_IP, UDP_SEND_PORT))
        try:
            data, addr = sock.recvfrom(1024)
            p = Packet(parsed_bytes=bytearray(data))
            if (p.data_type < 2):
                # Setup port
                # file_writer(p, query)
                print('Starting...')
                result = pool.apply_async(file_writer, (p, query))
                # result.get()
        except(TimeoutError):
            print('No, response. Try again')