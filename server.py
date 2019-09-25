import multiprocessing as mp
import socket
import time
import os
import select
from packet import Packet

SIZE_LIMIT = 32000 # In bytes
TIMEOUT = 20 # In Seconds
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

path = 'file_example/'

#Initiate available files
# r=root, d=directories, f = files
AVAILABLE_FILES = []
for r, d, f in os.walk(path):
        for file in f:
            AVAILABLE_FILES.append(file)
AVAILABLE_PORTS = range(5007, 5500, 2)


def send_data(port, q, file_request, data_id):
    sock2 = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    sock2.bind((UDP_IP, port))
    sock2.settimeout(5)
    print(file_request)

    try:
        f = open(file_request,'rb')
        bytes_to_send = os.path.getsize(file_request)
        packets_to_send = bytes_to_send // SIZE_LIMIT
        ten_percent = packets_to_send // 10
        
        # Initiate file sending
        i = 0
        j = 0
        while ((i+(j*256))<=packets_to_send):
            # print(packets_to_send - (i + j*256))
            packet_data = bytearray(f.read(SIZE_LIMIT))
            p = Packet(parsed_data=packet_data, data_id=data_id, sequence_number=i)
            sock2.sendto(p.parse(), (UDP_IP, port+1))
            data, addr = sock2.recvfrom(1024)
            res = Packet(parsed_bytes=bytearray(data)) # Read packet
            if ((i+(j*256))%ten_percent == 0):
                print((i+(j*256)) // ten_percent * 10, '% done sending ', file_request)
            if (res.data_type==1):
                i += 1
                if (i==256):
                    i=0
                    j+=1
            if (res.data_type>1):
                break
        
        # Finishing file transfer
        p = Packet(2,data_id,i)
        sock2.sendto(p.parse(), (UDP_IP, port+1))
        f.close()

    except(FileNotFoundError):
        data = bytearray(b'File not found!')
        p = Packet(parsed_data=data, data_type=3, data_id=data_id)
        MESSAGE = p.parse()
        sock2.sendto(MESSAGE, (UDP_IP, port+1))

    finally:
        q.put(port)



def receiver(data, addr, q, sock):
    p = Packet(parsed_bytes=bytearray(data))
    file_request = bytes(p.data).decode()
    print("received file request:", file_request)
    # print(p.parse())
    if (p.sum_checker() and AVAILABLE_FILES.count(file_request)>0):
        port = q.get()
        print("Beginning transfer, starting on port: ", port)
        data_id = AVAILABLE_FILES.index(file_request)
        file_request = 'file_example/' + file_request
        p = Packet(parsed_data=bytearray(str(port).encode()), data_id=data_id)
        sock.sendto(p.parse(), (UDP_IP, UDP_PORT+1))
        send_data(port, q, file_request, data_id)
    else:
        if(not p.sum_checker()):
            print('Checksum Failed')
        if(AVAILABLE_FILES.count(file_request)==0):
            print('No such files')
        print("Message fail")
        p = Packet(3,0)
        sock.sendto(p.parse(), (UDP_IP, UDP_PORT+1))

    return 0

if __name__ == '__main__':

    for file in AVAILABLE_FILES:
        print(file)

    #Initiate socket
    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    # sock.settimeout(TIMEOUT)
    pool = mp.Pool(processes=10)
    m = mp.Manager()
    q = m.Queue()
    for x in AVAILABLE_PORTS:
        q.put(x)
    while True:
        # start = input('Start? (Y/N)')
        # if (start == 'N' or start == 'n'):
        #     break
        # try:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        # except:
        #     print('time out')
        # receiver(data, addr)
        # receiver(data,addr,q,sock)
        results = pool.apply_async(receiver, (data, addr, q, sock))
        # print(results.get(6))
    # results.close()

    

# p = Packet()
# p.data_packet(parsed_data=bytearray([4,78]),data_id=0,sequence_number=0)
# print(p.parse())
# print(p.sum_checker())