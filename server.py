import time
from concurrent import futures
import grpc
from data_pb2_grpc import FaissServiceServicer, add_FaissServiceServicer_to_server
from data_pb2 import *
import faiss
import numpy as np
import json
from log import g_log_inst
import os
g_log_inst.start('logs/test.log', 'INFO')

HOST = "0.0.0.0"
PORT = 3457
ONE_DAY_IN_SECONDS = 60 * 60 * 24

class FaissServic(FaissServiceServicer):
    """Summary of class here.

    Stores the item's Bert code and supports searching for topk nearest neighbors

    Attributes:
        Bert_dim: Number of dimensions for Bert encoding before PCA
        PCA_dim: Number of dimensions for Bert encoding after PCA

    """
    def __init__(self, Bert_dim = 768, PCA_dim = 100, train_PCA_path = './train_PCA.npy'):
        self.Bert_dim = Bert_dim
        self.item_emb = {}
        self.PCA_dim = PCA_dim
        self.PCA = faiss.PCAMatrix (Bert_dim, PCA_dim)
        X = np.load(train_PCA_path,allow_pickle=True)
        self.PCA.train(X)
        self.index = faiss.IndexFlatIP(PCA_dim)
        self.index = faiss.IndexIDMap(self.index)
        print(X.shape,'init Done!')
        g_log_inst._inst.info('init Done!')

        file_path = os.getcwd() #获得当前工作目录
        if os.path.exists(file_path + "/backup.npy") and os.path.exists(file_path + "/backup.index"):
            self.index = faiss.read_index("backup.index")
            self.item_emb = np.load("backup.npy", allow_pickle=True).item()
            print('load success')

    def add(self, request, context):
        """ Add one item's id and this item's Bert embedding
        Args:
            request.id: The item's id
            request.Bert_embedding: The item's Bert_embedding in list form in json

        Returns: 
            None
        """
        id = request.id
        if id in self.item_emb: 
            g_log_inst._inst.warning(str(request.id) + 'has been added')
            return Message_tag(tag = str(request.id) + 'has been added')

        Bert_embedding = np.array([json.loads(request.emb)]).astype('float32')
        Bert_embedding = self.PCA.apply_py(Bert_embedding)
        self.item_emb[id] = Bert_embedding
        faiss.normalize_L2(Bert_embedding)
        self.index.add_with_ids(Bert_embedding, np.array((id,)).astype('int64'))
        
        g_log_inst._inst.info(str(request.id) + 'add success')
        return Message_tag(tag = 'add success')

    def remove(self, request, context):
        """ Remove the item with the input id
        Args:
            request.json: The id to be removed

        Returns: 
            None
        """
        if request.num not in self.item_emb: 
            g_log_inst._inst.warning(str(request.num) + 'has not been added, can not remove')
            return Message_tag(tag = str(request.num) + 'has not been added')

        del self.item_emb[request.num]
        self.index.remove_ids(np.array([request.num], dtype=np.int64))
        g_log_inst._inst.info(str(request.num) + 'remove success')
        return Message_tag(tag = 'remove success')

    def get_size(self, request, context):
        g_log_inst._inst.info('get size success')
        return Message_int(num = self.index.ntotal)

    def recall_by_ids(self, request, context):
        """ Recall the topk nearest neighbors of the ids' everage embedding
        Args:
            request.his_ids: A list of history ids in json. Use the everage embedding of the ids as feature_search
            request.topk: The topk nearest neighbors of feature_search

        Returns: 
            json list contains topk items's scores and id
        """
        his_ids = json.loads(request.his_ids)
        feat = np.zeros([1,self.PCA_dim]).astype('float32')
        for id in his_ids:
            if id not in self.item_emb:
                g_log_inst._inst.debug('recall fail, his_ids not in faiss')
                continue
            feat += self.item_emb[id]
        feat /= len(his_ids)
        faiss.normalize_L2(feat)
        scores, I = self.index.search(feat, request.topk)
        res = []
        for dim_id, i in enumerate(I[0]):
            i = int(i)
            if i == -1: continue
            dic = {'id':i, 'score':scores[0][dim_id].item()} 
            # self.item_data[i]['emb'] = self.item_emb[i].tolist()
            res.append(dic)
        g_log_inst._inst.info('recall success') 
        return Message_json(json_str = json.dumps(res))

    def cal_by_ids(self, request, context):
        """ Get the similarity scores of his_ids' average embeddings and ids' embeddings
        Args:
            request.his_ids: A list of his_ids. Their average embeddings will be used to calculate the similarity scores.
            request.cal_ids: A list of ids which need to caculate the similarity scores

        Returns: 
            json list contains topk items's scores and id
        """
        his_ids = json.loads(request.his_ids)
        ids = json.loads(request.cal_ids)
        feat = np.zeros([1,self.PCA_dim]).astype('float32')
        for id in his_ids:
            if id not in self.item_emb:
                g_log_inst._inst.debug('calaculate fail, his_ids not in faiss')
            feat += self.item_emb[id]
        feat /= len(his_ids)
        faiss.normalize_L2(feat)
        res = []
        for id in ids:
            if id not in self.item_emb:
                g_log_inst._inst.debug('calaculate fail, ids for calculate not in faiss')
            score = (self.item_emb[id][0] * feat).sum()
            dic = {'id':id, 'score':score.item()} 
            # self.item_data[i]['emb'] = self.item_emb[i].tolist()
            res.append(dic)
        g_log_inst._inst.info('cal success') 
        return Message_json(json_str = json.dumps(res))

    def write(self, request, context):
        faiss.write_index(self.index, 'backup.index')
        np.save('backup.npy', self.item_emb)
        return Message_tag(tag = 'write success')

        
   
    

def main():
    grpcServer = grpc.server(futures.ThreadPoolExecutor(max_workers=30))
    add_FaissServiceServicer_to_server(FaissServic(), grpcServer)
    print(f'"msg":"grpc start @ grpc://{HOST}:{PORT}"')
    grpcServer.add_insecure_port(f"{HOST}:{PORT}")
    grpcServer.start()
    try:
        while True:
            time.sleep(ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        grpcServer.stop(0)
    except Exception as e:
        grpcServer.stop(0)
        raise

if __name__ == "__main__":
    main()
