# 本文件模拟感染过程
import networkx as nx
import random
import csv
import matplotlib.pyplot as plt
import numpy as np

graph = nx.DiGraph()    #创建图对象

with open(r'infection_flows.csv','r',encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)    #跳过标题行
    for row in reader:
        source_ip,target_ip,weight = row       #line [source_ip,target_ip, weight]
        graph.add_edge(source_ip,target_ip,weight=float(weight))               #添加边信息

def simulation_si(graph, seed, iter_num=100):
    """
    模放SI 模型的感染过程
    :param graph: 拓扑图
    :param seed:种子，感染源
    :param iter_num:  模拟轮数
    ;return: 所有被感染的节点
    """
    for node in graph: # 用state标记该点是否被感染，0: 未被感染，1: 被感染
        graph.nodes[node]['state'] = 0
    graph.nodes[seed]['state'] = 1 # 标记种了节点状态
    all_infect_nodes = [seed] # 记录所有被感染的节点，即下一轮的科子节点
    alL_infect_nodes_round =[] # 轮次记录被感染的节点

    infect_graph = nx.DiGraph()# 彼感染节点纠成的图
    infect_graph.add_node(seed)

    for i in range(iter_num):
        new_infect = []
        for v in all_infect_nodes:
            for nbr in graph.neighbors(v):
                edge_data = graph.get_edge_data(v,nbr)
                if random.uniform(0,1)<10000 * float(edge_data['weight']):
                    graph.nodes[nbr]['state'] = 1
                    new_infect.append(nbr)
                    infect_graph.add_edge(v,nbr)
        all_infect_nodes.extend(new_infect)
        alL_infect_nodes_round.append(list(set(all_infect_nodes)))
    return all_infect_nodes,alL_infect_nodes_round

si = [] # 记录每个节点感染的节点数景
for node in graph:
    all_infect_nodes_round = []
    for i in range(1,11):
        all_infect_nodes, _ = simulation_si(graph,node,iter_num=i)
        all_infect_nodes_round.append(len(all_infect_nodes))
    si.append([node]+ all_infect_nodes_round)

top_10 = sorted(si, key=lambda x: x[-1], reverse=True)[:10]# 获取感染能力最的top10
formatted_top_10 = [(node[0],node[1:]) for node in top_10]
for item in formatted_top_10:
    print(item)

import csv

top_10_ips = [data[0] for data in top_10]
with open(r'infection_flows.csv','r',newline='',encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    header = next(reader)
    top_10_data = [row for row in reader if row[0] in top_10_ips]

# 将数据写入top_10_infection_flows.csv
with open(r'top10_infection_flows.csv','w',newline='',encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(header)   #写入标题行
    writer.writerows(top_10_data)

# 2.计算 top_10中每个source_ip 的weight平均值，并写入top_10_infected_nodes.csv
# 计算top_10 中每个source_ip对应的weight总和和分数
ip_weight_sum = {ip: [0,0] for ip in top_10_ips}

# 重新打开 infection_flows.csv 读取数据
with open(r'infection_flows.csv','r',newline='',encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    next(reader) #跳过标题行

    # 计算每个source_ip的weight平均值
    for row in reader:
        source, target, weight = row
        if source in top_10_ips:
            ip_weight_sum[source][0] += float(weight)
            ip_weight_sum[source][1] += 1
# 计算每个source_ip 的 weight平均值
ip_weight_average = {ip: sum_count[0]/sum_count[1] for ip,sum_count in ip_weight_sum.items()}

# 将数据写入top_10_infected_nodes.csv
with open('top_10_infected_nodes.csv','w',newline='',encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Id','weight'])  #写入标题行
    writer.writerows(ip_weight_average.items())



plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.figure(figsize=(16,9))
marker = ['.', ',', 'v', '^', '>', '*', '+', 'd', 'x', 'p']

def get_rand_color():
    clr = random.getrandbits(24)
    clr = '#'+hex(clr)[2:]
    clr += 'F'*(7-len(clr))
    return clr

for node in top_10[:5]:
    ip = node[0]
    x = [i for i in range(11)]
    y = [0]
    y.extend(node[1:])
    plt.plot(x, y, color=get_rand_color(), marker=marker[top_10.index(node)],label=ip, linewidth=2.5)

plt.xlim(0, len(x))
plt.ylim(0, max(y))
plt.xlabel('Round',fontsize=25)
plt.ylabel('Number',fontsize=25)
plt.legend(fontsize=20,loc='upper right',bbox_to_anchor=(1.13,1.0),borderaxespad=0.)
plt.show()