import multiprocessing as mp
import socket
from packet import Packet
import os
import time

path = 'file_example/'

SIZE_LIMIT = 32000
UDP_IP = "192.168.43.150"
UDP_SEND_PORT = 5005
AVAILABLE_FILES = []
#Initiate available files
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        AVAILABLE_FILES.append(file)
# MESSAGE = bytes(bytearray(b"Hello, World!"))

def file_writer(UDP_SEND_IP, p, query, data_id):
    file_request = path + query
    port = int(bytes(p.data).decode())
    UDP_SEND_PORT = port
    UDP_RCV_PORT = port+1
    sock2 = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    sock2.bind((UDP_IP, UDP_RCV_PORT))
    sock2.settimeout(2)

    # Sending file
    try:
        f = open(file_request,'rb')
        bytes_to_send = os.path.getsize(file_request)
        packets_to_send = bytes_to_send // SIZE_LIMIT
        ten_percent = packets_to_send // 10
        if (ten_percent == 0):
            ten_percent = 1
        
        # Initiate file sending
        i = 0
        j = 0
        while ((i+(j*256))<=packets_to_send):
            # print(packets_to_send - (i + j*256))
            packet_data = bytearray(f.read(SIZE_LIMIT))
            p = Packet(parsed_data=packet_data, data_id=data_id, sequence_number=i)
            sock2.sendto(p.parse(), (UDP_SEND_IP, port))
            # print('sent file with seqnum:',p.sequence_number)
            try:
                data, addr = sock2.recvfrom(1024)
                res = Packet(parsed_bytes=bytearray(data)) # Read packet
                # print('received file with seqnum:',res.sequence_number)
                if ((i+(j*256))%ten_percent == 0):
                    print((i+(j*256)) // ten_percent * 10, '% done sending ', file_request)
                if (res.data_type==1 and res.sequence_number==i):
                    i += 1
                    if (i==256):
                        i=0
                        j+=1
                elif (res.sequence_number!=i):
                    print('Mismatched sequence number, readjusting...',i)
                    i = res.sequence_number
                if (res.data_type>1):
                    break
            except(Exception):
                print('Not acknowledged, trying again...')
        
        # Finishing file transfer
        p = Packet(2,data_id,i)
        sock2.sendto(p.parse(), (UDP_SEND_IP, port))
        print('Finished sending: ', file_request)
        f.close()

    except(FileNotFoundError):
        data = bytearray(b'File not found!')
        p = Packet(parsed_data=data, data_type=3, data_id=data_id)
        MESSAGE = p.parse()
        sock2.sendto(MESSAGE, (UDP_SEND_IP, port))

if __name__=='__main__':

    UDP_SEND_IP = input('input target ip:\n')

    print ("UDP target IP:", UDP_SEND_IP)
    print ("UDP target port:", UDP_SEND_PORT)

    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP

    #port setup
    port_accepted = False
    while(not port_accepted):
        UDP_RCV_PORT = int(input('Select port (4500-5000):\n'))
        try:
            sock.bind((UDP_IP, UDP_RCV_PORT))
            port_accepted = True
        except(Exception):
            print('Port not available!')
            port_accepted = False
    sock.settimeout(5)
    pool = mp.Pool(processes=10)

    while True:
        print('Available files:')
        for file in AVAILABLE_FILES:
            print(file)
        query=input()
        if(AVAILABLE_FILES.count(query) > 0):
            data_id = AVAILABLE_FILES.index(query)
            port_information = query + ':' + str(UDP_RCV_PORT)
            p = Packet(parsed_data=bytearray(port_information.encode()), data_id=data_id)
            # print(p.parse())
            sock.sendto(p.parse(), (UDP_SEND_IP, UDP_SEND_PORT))
            try:
                data, addr = sock.recvfrom(1024)
                p = Packet(parsed_bytes=bytearray(data))
                # print(p.parse())
                if (p.data_type < 2):
                    # Setup port
                    # file_writer(p, query)
                    print('Starting Upload:', query)
                    result = pool.apply_async(file_writer, (UDP_SEND_IP, p, query, data_id))
                    # result.get()
                    # result.get()
            except(TimeoutError):
                print('No, response. Try again')
        else:
            print('No such files')