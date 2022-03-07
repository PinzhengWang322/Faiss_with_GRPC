from email import message
import grpc
from data_pb2_grpc import FaissServiceStub
from data_pb2 import *
import time
import json
import numpy as np
import random
url = "localhost:3457"
channel = grpc.insecure_channel(url)
client = FaissServiceStub(channel=channel)

if __name__ == '__main__':
    
    # add 30000 items to Faiss
    for id in range(40000, 70000):
        emb = np.random.random([768])
        emb = json.dumps(emb.tolist())
        result = client.add(Message_add(id = id, emb = emb))
        if result.tag != 'add success':
            raise RuntimeError('add fail!(may be this id has been already added)')
        

    # show the number of items in Faiss
    result = client.get_size(Message_None())
    print(result)


    # recall 120 users' 200 items through their 2 latest history ids
    t1 = time.time()
    for i in range(120):
        his_ids = json.dumps([random.randint(40000, 70000),random.randint(40000, 70000)])
        out = client.recall_by_ids(Message_recall(his_ids = his_ids, topk = 200))
    t2 = time.time()
    print("120 users' recall time:", t2 - t1)
    print(json.loads(out.json_str)[:3])


    # remove 10000 items from Faiss
    for id in range(60000, 70000):
        result = client.remove(Message_int(num = id))
        if result.tag != 'remove success':
            raise RuntimeError('remove fail!(may be this id has not been added)')
    
    result = client.get_size(Message_None())
    print("after remove's size:", result)


    # cal 120 user's 200 items similarity with their history from Faiss
    cal_time = 0
    for i in range(120):
        his_ids = json.dumps([random.randint(40000, 60000),random.randint(40000, 60000)])
        cal_ids = json.dumps([random.randint(40000, 60000) for i in range(200)])
        t1 = time.time()
        out = client.cal_by_ids(Message_cal(his_ids = his_ids, cal_ids = cal_ids))
        t2 = time.time()
        cal_time += t2 - t1
    print("120 users' cal time:", cal_time)
    print(json.loads(out.json_str)[:3])

