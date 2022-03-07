# GRPC Faiss服务

这里提供了关于faiss召回的grpc接口

### 编译proto

```
python -m grpc_tools.protoc -I=proto_dir --python_out=. --grpc_python_out=. data.proto
```

### 使用

建议在虚拟环境下使用

确保pip是最新版`python -m pip install --upgrade pip`

1. `pip install -r requirements.txt`安装依赖
2. `pip --default-time=1000 install -i https://pypi.tuna.tsinghua.edu.cn/simple faiss-gpu`从清华源安装faiss

2. `python server.py`启动服务端
3. `python client.py`启动客户端

此外，还需要在server.py的同级目录下加上train_PCA.npy文件，内容是多条内容的Bert编码构成的numpy矩阵，供faiss初始化PCA。

### 接口说明

#### 新帖入库接口：

add (Message_add(id, ebm)):

定义：添加新项目的id和它内容的Bert编码

输入参数：id(int64):新项目的id              
        emb(str):新项目内容的Bert编码列表形式，以json形式存储

返回值：None



#### 删除旧项目接口：

remove(Message_int(num))

定义：删除输入id的item

输入参数：num(int64):要删除的item的id

返回值：None



#### 返回Faiss库中item总数接口：

get_size(Message_None())

定义：返回Faiss库中item总数

输入参数：Message_None()

返回值：Message_int.num, item的总数



#### 根据历史ids召回topk项目：

recall(Message_recall(his_ids , topk))

定义：根据history_ids召回topk个语义相似的项目

输入参数：his_ids(str): 用户历史id的列表，用json形式存储

​				   topk(int32): 召回topk个语义相似的项目

返回值：Message_json.json_str, 召回的用户id和语义相似度得分，例如：[{'id': 776734, 'score': 0.6223110556602478}, {'id': 764666, 'score': 0.6223109364509583}, {'id': 745903, 'score': 0.6129276752471924}]



#### 根据历史ids计算指定项目的得分：

cal_by_ids(Message_cal(his_ids, cal_ids)

定义：计算cal_ids中每个id与history_ids的语义相似度得分

输入参数：his_ids(str): 用户历史id的列表，用json形式存储

​				   cal_ids(str): 需要计算的id的列表，用json形式存储

返回值：Message_json.json_str,cal_ids中的id和语义相似度得分，例如：[{'id': 776734, 'score': 0.622310996055603}, {'id': 739866, 'score': 0.3671881854534149}, {'id': 745903, 'score': 0.6129276156425476}]
