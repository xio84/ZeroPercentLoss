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

path = 'downloads/'
AVAILABLE_PORTS = range(5007, 5500, 2)


def send_data(UDP_SEND_IP, port, q, file_request, data_id):
    sock2 = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    sock2.bind((UDP_IP, port))
    sock2.settimeout(500)
    # print(file_request)

    i = 0    
    f = open(file_request,'wb')
    # res = Packet(1,data_id)
    # sock2.sendto(res.parse(), (UDP_IP, port))
    data, addr = sock2.recvfrom(32678)
    p = Packet(parsed_bytes=bytearray(data))
    # print('received file with seqnum:',p.sequence_number)
    j = 0
    while(p.data_type < 2):
        if (p.sum_checker() and p.sequence_number==i):
            print(i + 256*j)
            # print(p.parse())
            f.write(bytes(p.data))
            res = Packet(1,p.data_id,sequence_number=i)
            print('sent file with seqnum:',res.sequence_number)
            sock2.sendto(res.parse(), (UDP_SEND_IP, port+1))
            try:
                data, addr = sock2.recvfrom(32678)
                p = Packet(parsed_bytes=bytearray(data))
                print('received file with seqnum:',p.sequence_number)
                i+=1
                if (i==256):
                    i=0
                    j+=1
            except(Exception):
                print('Not acknowledge, trying again...')
                f.seek((i + 256*j)*SIZE_LIMIT,0)
        else:
            print('seq_num mismatch',i,'and',p.sequence_number)
            res = Packet(1,p.data_id,sequence_number=i)
            print('sent file with seqnum:',res.sequence_number)
            sock2.sendto(res.parse(), (UDP_SEND_IP, port+1))
            try:
                data, addr = sock2.recvfrom(32678)
                p = Packet(parsed_bytes=bytearray(data))
                print('received file with seqnum:',p.sequence_number)
            except(Exception):
                print('Not acknowledge, trying again...')
                f.seek((i + 256*j)*SIZE_LIMIT,0)
    print('Upload file : ',file_request,' has finished')
    f.close()
    q.put(port)



def receiver(data, addr, q, sock):
    UDP_SEND_IP = addr[0]
    p = Packet(parsed_bytes=bytearray(data))
    first_request = bytes(p.data).decode().split(':')
    file_request = first_request[0]
    primary_send_port = int(first_request[1])
    print("received file request:", file_request)
    # print(p.parse())
    if (p.sum_checker()):
        port = q.get()
        print("Beginning transfer, starting on port: ", port)
        file_request = path + file_request
        data_id = p.data_id
        p = Packet(parsed_data=bytearray(str(port).encode()), data_id=data_id)
        # print(primary_send_port)
        sock.sendto(p.parse(), (UDP_SEND_IP, primary_send_port))
        send_data(UDP_SEND_IP, port, q, file_request, data_id)
    else:
        if(not p.sum_checker()):
            print('Checksum Failed')
        print("Message fail")
        p = Packet(3,0)
        sock.sendto(p.parse(), (UDP_SEND_IP, primary_send_port))

    return 0

if __name__ == '__main__':

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
        # results.get()
        # print(results.get(6))
    # results.close()

    

# p = Packet()
# p.data_packet(parsed_data=bytearray([4,78]),data_id=0,sequence_number=0)
# print(p.parse())
# print(p.sum_checker())