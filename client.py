import multiprocessing as mp
import socket
from packet import Packet
import os, sys
import time

path = 'file_example/'

SIZE_LIMIT = 32000
UDP_IP = "127.0.0.1"
UDP_SEND_PORT = 5005
AVAILABLE_FILES = []
#Initiate available files
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        AVAILABLE_FILES.append(file)
# MESSAGE = bytes(bytearray(b"Hello, World!"))

def file_writer(UDP_SEND_IP, p, query, data_id, progress_q):
    file_request = path + query
    port = int(bytes(p.data).decode())
    UDP_SEND_PORT = port
    UDP_RCV_PORT = port+1
    sock2 = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    sock2.bind((UDP_IP, UDP_RCV_PORT))
    sock2.settimeout(2)

    # Sending file
    # try:
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
        # try:
        data, addr = sock2.recvfrom(1024)
        res = Packet(parsed_bytes=bytearray(data)) # Read packet
        # print('received file with seqnum:',res.sequence_number, ', i= ',i)
        if ((i+(j*256))%ten_percent == 0):
            progress_q.put((query,(i+(j*256)) // ten_percent))
        if (res.data_type>1):
            break
        if (res.data_type==1 and res.sequence_number==i):
            i += 1
            if (i==256):
                i=0
                j+=1
        elif (res.sequence_number!=i):
            # print('Mismatched sequence number, readjusting...',i)
            i = res.sequence_number
            f.seek((i + 256*j)*SIZE_LIMIT,0)
        else:
            f.seek((i + 256*j)*SIZE_LIMIT,0)
        # except(Exception):
        #     print('Not acknowledged, trying again...')
        #     f.seek((i + 256*j)*SIZE_LIMIT,0)
    
    # Finishing file transfer
    p = Packet(2,data_id,i)
    sock2.sendto(p.parse(), (UDP_SEND_IP, port))
    # print('Finished sending: ', file_request)
    progress_q.put([query,10])
    f.close()

    # except(FileNotFoundError):
    #     data = bytearray(b'File not found!')
    #     p = Packet(parsed_data=data, data_type=3, data_id=data_id)
    #     MESSAGE = p.parse()
    #     sock2.sendto(MESSAGE, (UDP_SEND_IP, port))

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
    m = mp.Manager()
    progress_q = m.Queue()
    index = input('Number of files to be sent:')
    print('Available files:')
    for file in AVAILABLE_FILES:
        print(file)
    proceed = False
    while(not proceed):
        query=input('Input files to be sent (separated by comma)')
        list_of_files = query.split(',')
        if not(int(len(list_of_files)) == int(index)):
            print('Number of files do not match! Expected: ',index,', Received: ',len(list_of_files))
        else:
            proceed = True
            for file in list_of_files:
                if (AVAILABLE_FILES.count(file) == 0):
                    proceed = False
                    print('File: ',file,' Does not exist!')

    FILE_IN_PROGRESS = []
    for query in list_of_files:
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
                    result = pool.apply_async(file_writer, (UDP_SEND_IP, p, query, data_id, progress_q))
                    print('Starting Upload:', query)
                    FILE_IN_PROGRESS.append([query,0])
                    # result.get()
                    # result.get()
            except(TimeoutError):
                print('No, response. Try again')
        else:
            print('No such files')

    while True:
        if not(progress_q.empty()):
            file_to_be_updated = progress_q.get()
            for file_progress in FILE_IN_PROGRESS:
                if (file_to_be_updated[0] == file_progress[0]):
                    file_progress[1] = file_to_be_updated[1]
            sys.stdout.write(u"\u001b[2J")
            sys.stdout.flush()
            for file_progress in FILE_IN_PROGRESS:
                print(file_progress[0], ':')
                sys.stdout.write('[')
                progress_i = 0
                while(progress_i < file_progress[1]):
                    sys.stdout.write('x')
                    progress_i+=1
                while(progress_i < 10):
                    sys.stdout.write('-')
                    progress_i+=1
                sys.stdout.write(']\n')
                sys.stdout.flush()
        else:
            proceed = True
            for file_progress in FILE_IN_PROGRESS:
                if (file_progress[1] != 10):
                    proceed = False
            if (proceed):
                break
                

