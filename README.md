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

add (Message_add(id, emb)):

定义：添加新项目的id和它内容的Bert编码

输入参数：id(int64):新项目的id              
        emb(str):新项目内容的Bert编码列表形式，以json形式存储

返回值：如果新增成功，返回Message_tag(tag = 'add success')



#### 删除旧项目接口：

remove(Message_int(num))

定义：删除输入id的item

输入参数：num(int64):要删除的item的id

返回值：如果删除成功，返回Message_tag(tag = 'remove success')



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

#### 制作备份：

write(Message_None())

定义：对编码和index做备份，存储为当前目录下的backup.index和backup.npy

输入参数：无

返回值：如果备份成功，返回Message_tag(tag = 'write success')


## 4.24 更新

**更新了add功能，在加入新项目时可以增加项目的创建时间戳(ms)。**

add (Message_add(id, emb, time)):

定义：添加新项目的id和它内容的Bert编码

输入参数：

        id(int64):新项目的id

        emb(str):新项目内容的Bert编码列表形式，以json形式存储
        
        time(int64):新项目的创建时间。如果缺省，以调用的时间戳作为该项目的创建时间。          

返回值：如果新增成功，返回Message_tag(tag = 'add success')。**更新时不再备份index，需要调用write**


**更新了recall功能，在召回语义项目时可以多少天以内的条件限制。**

recall(Message_recall(his_ids , topk, time))

定义：根据history_ids召回topk个语义相似的项目

输入参数：

        his_ids(str): 用户历史id的列表，用json形式存储

        topk(int32): 召回topk个语义相似的项目
        
        time(in32): 以天数作为单位，过滤距今天数大于time天的项目。

返回值：Message_json.json_str, 召回的用户id和语义相似度得分，例如：[{'id': 776734, 'score': 0.6223110556602478}, {'id': 764666, 'score': 0.6223109364509583}, {'id': 745903, 'score': 0.6129276752471924}]

由于faiss库对时间的优化比较高，所以不支持条件过滤的topk检索。目前只能检索topk个，然后过滤掉不符合条件的项目。https://github.com/facebookresearch/faiss/issues/40

**更新了备份和删除机制**

删除时，只删除faiss库中的index，从而保证检索时间不会因数据量的增加而变大。而存储入过库的item的编码信息的内存删除大于180天的，尽量可以进行召回。在入库新内容备份时，对于item的编码等信息追加备份到backup.txt文件中，对于faiss的index的信息整体备份到backup.index文件中。


**remove.py 脚本每日删除过期item**

在启动remove.p后会立刻根据备份的backup.txt文件删除faiss中过期的item（index删除>30天的，memory删除>180天的。remove后会备份index。由于backup.txt数量很多，所以每次会记录已经删除过的item并存在have_removed.npy下。这样已经删除过的项目就不必要每次启动remove.py时打扰faiss服务。6w条item删除2w条item耗时一分钟左右，耗时不会太长。





