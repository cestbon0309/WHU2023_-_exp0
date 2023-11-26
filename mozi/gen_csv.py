import random
import csv
import os
import networkx as nx





def gen_ipv4_addr(nums):#generate valid ipv4 address
    ret = []
    for x in range(nums):
        addr = ''
        for idx in range(4):
            addr += str(random.randint(0,255))
            addr += '.'if idx <3 else ''
        ret.append(addr)
    return ret

def gen_rand_nodes():#传染节点生成
    infected_ips = gen_ipv4_addr(num_infected)
    uninfected_ips = gen_ipv4_addr(num_uninfected)
    with open('infected_nodes.txt','w',encoding='utf-8') as f:
        for x in infected_ips:
            f.write(f'{x}\n')
    with open('uninfected_nodes.txt','w',encoding='utf-8') as f:
        for x in uninfected_ips:
            f.write(f'{x}\n')

def write2csv():#节点感染攻击流生成
    files = os.listdir()
    if not ('uninfected_nodes.txt' in files and 'infected_nodes.txt' in files):
        gen_rand_nodes()
    with open('infected_nodes.txt','r',encoding='utf-8') as f:
        infected_ips = f.readlines()
    with open('uninfected_nodes.txt','r',encoding='utf-8') as f:
        uninfected_ips = f.readlines()
    with open('infection_flows.csv','w',newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['source_ip','target_ip','weight'])
        for t in uninfected_ips:
            for s in infected_ips:
                weight = round(random.uniform(0.000001,0.000002),16)
                writer.writerow([s,t,weight])

def simulation_si(graph,origin,iter = 100):

    for node in graph:
        graph.nodes[node]['state']=0#0 = uninfected 1 = infected
    
    seed = origin
    #iter = 100 #迭代次数
    graph.nodes[origin]['state']=1
    all_infected = [origin]
    all_infected_round = []
    inf_graph = nx.DiGraph()
    inf_graph.add_node(origin)

    for i in range(iter):
        new_infect = []
        for inf_n in all_infected:
            for nbr in graph.neighbors(inf_n):
                edge_data = graph.get_edge_data(inf_n,nbr)
                if random.uniform(0,1) < 10000 * float(edge_data['weight']):
                    graph.nodes[nbr]['state'] = 1#感染新的节点
                    new_infect.append(nbr)
                    inf_graph.add_edge(inf_n,nbr)
        all_infected.extend(new_infect)
        all_infected_round.append(list(set(all_infected)))
    return all_infected,all_infected_round
    

def analyze():
    global graph
    si = []
    for node in graph:
        ain,ain_r = simulation_si(graph,node)
        graph.nodes[node]['all_infect_nodes'] = list(set(ain))
        graph.nodes[node]['all_infect_nodes_round'] = ain_r
        si.append([node,len(list(set(ain)))])
    
    top_10 = sorted(si,key = lambda x:x[1],reverse=True)[:10]
    return top_10


if __name__ == '__main__':
    write2csv()