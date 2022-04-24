from email import message
import grpc
from data_pb2_grpc import FaissServiceStub
from data_pb2 import *
import time, datetime
import json
import numpy as np
import random
import os
url = "localhost:3457"
channel = grpc.insecure_channel(url)
client = FaissServiceStub(channel=channel)

day_ms = 60 * 60 * 24 * 1000

def remove():
    file_path = os.getcwd()
    if os.path.exists(file_path + "/have_removed.npy"):
        index_removed, memory_removed = np.load(file_path + "/have_removed.npy", allow_pickle=True)
    else:
        index_removed, memory_removed = set(), set()
    now_ms = int(round(time.time() * 1000))
    file_path = os.getcwd()
    f = open(file_path + "/backup.txt")
    line = f.readline()
    while line: 
        line_dic = json.loads(line)

        if line_dic['id'] not in index_removed and now_ms - line_dic['time'] > day_ms * 30:
            client.remove_index(Message_int(num = line_dic['id']))
            index_removed.add(line_dic['id'])

        if line_dic['id'] not in memory_removed and now_ms - line_dic['time'] > day_ms * 180:
            client.remove_memory(Message_int(num = line_dic['id']))
            memory_removed.add(line_dic['id'])

        line = f.readline() 
    
    f.close() 
    np.save("have_removed.npy", [index_removed, memory_removed])
    
    print("remove success")

def main():
    remove()
    client.write(Message_None())
    




if __name__ == '__main__':
    t1 = time.time()
    main()
    t2 = time.time()
    print(t2 - t1)
