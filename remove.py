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

def remove(have_removed):
    now_ms = int(round(time.time() * 1000))
    file_path = os.getcwd()
    f = open(file_path + "/backup.txt")
    line = f.readline()
    while line: 
        line_dic = json.loads(line)
        if line_dic['id'] not in have_removed and now_ms - line_dic['time'] > day_ms * 30:
            client.remove(Message_int(num = line_dic['id']))
            have_removed.add(line_dic['id'])
        line = f.readline() 
    f.close() 
    print("remove success")

def main():
    have_removed = set()
    remove(have_removed)
    tomorrow_s = int(time.mktime(datetime.date.today().timetuple())) + day_ms / 1000
    now_s = int(round(time.time()))
    print(tomorrow_s - now_s + 3600 * 4)
    time.sleep(tomorrow_s - now_s + 3600 * 4) #凌晨4点开始
    while(True):
        remove(have_removed)
        time.sleep(day_ms / 1000)
    




if __name__ == '__main__':
    main()
