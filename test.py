from packet import Packet
import os, sys

# # checksum prototype

# arr = bytearray(10)
# x = 6

# i=1
# length = len(arr)
# while(x>0):
#     arr[length-i] = x%256
#     x = x//256
#     i = i + 1


# # buffer = 0
# # i = 0
# # arr.append(0)
# # arr.append(0)
# # print(arr)

# # while (i<len(arr)):
# #     buffer = buffer*256 + arr[i]
# #     i = i+1

# # polynom = 65535

# # print(buffer)


# buffer = 0
# int_values = [x for x in arr]
# for x in int_values:
#     y = x << 16
#     if (buffer != 0):
#         y = y^buffer
#         buffer = 0
#     y = y << 16
#     while (y>65535):
#         polynom = 65535
#         while polynom<y:
#             polynom = polynom << 1
#         y = y^polynom
#     buffer = y & 65535
# print(buffer)

# p = Packet()
# p.data_packet(parsed_data=bytearray([1]),data_id=0,sequence_number=0)
# print(p.parse())
# print(p.sum_checker())

# f = open('file_example/pre-rebase.sample','rb')

# size = os.path.getsize('file_example/pre-rebase.sample')
# print(size)
# line = f.read(10)
# print(line)
# i = f.tell()
# print(i)

# import time
# import sys
# import multiprocessing as mp

# toolbar_width = 40

# def progress():
#     # setup toolbar
#     sys.stdout.write("[%s]" % (" " * toolbar_width))
#     sys.stdout.flush()
#     time.sleep(1) # do real work here
#     sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['

#     for i in range(toolbar_width):
#         time.sleep(0.1) # do real work here
#         # update the bar
#         sys.stdout.write("-")
#         sys.stdout.flush()

#     sys.stdout.write("]\n") # this ends the progress bar

# if __name__ == '__main__':
#     pool = mp.Pool(processes=10)
#     m = mp.Manager()
#     q = m.Queue()
#     while True:
#         # receiver(data, addr)
#         x = input('start')
#         # receiver(data,addr,q,sock)
#         results = pool.apply_async(progress, ())
#         input()
#         print('\n')

# f = open('file_example/pre-base.sample','rb')

from ctypes import windll, Structure, c_long, byref
import time


class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]



def queryMousePosition(p):
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    p = pt
    return { "x": pt.x, "y": pt.y}

p = POINT()
pos = queryMousePosition(p)
query = u"\u001b[2J"
sys.stdout.write(u"\u001b[s")
sys.stdout.write("\n" + str(pos))
sys.stdout.write(u"\u001b[u")
sys.stdout.flush()
sys.stdout.write(u"\u001b[s")
sys.stdout.write(str(pos))
sys.stdout.write(u"\u001b[u")
time.sleep(2)

sys.stdout.flush()
# sys.stdout.write(str(pos))
# sys.stdout.flush()

