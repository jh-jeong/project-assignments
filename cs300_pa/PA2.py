'''
Created on 2014. 12. 6.

@author: biscuit
'''

def main():
    N = int(raw_input())
    nameDict = {}
    edges = {}
    nodes = set([])
    for i in xrange(N):
        dep = raw_input().split()[0]
        dest= raw_input().split()
        dep_low = dep.lower() 
        nameDict[dep_low] = dep
        nodes.add(dep_low)
        edges[dep_low] = {}
        while len(dest) != 0:
            weight = int(dest.pop())
            key = dest.pop()
            key_low = key.lower()
            if not nameDict.has_key(key_low):
                nameDict[key_low] = key
                edges[key_low] = {}
            nodes.add(key_low)
            edges[dep_low][key_low]=weight
    
    while True:
        choice = raw_input('Choose the problem (1 or 2): ')
        if choice == '1':
            Prob_1(nodes, edges, nameDict);break
        if choice == '2':
            Prob_2(nodes, edges, nameDict);break
        
def Prob_1(nodes, edges, nameDict):
    src = raw_input('Src: ').lower()
    dst = raw_input('Dst: ').lower()
    D = {}.fromkeys(nodes,('',[]))
    D[src] = (0,[src])
    S = {}
    while len(D) != 0 :
        u = min(D, key=lambda x: D[x])
        S[u] = D[u]
        D.pop(u)
        for d, v in edges[u].items():
            try:
                if D[d][0] > S[u][0] + v:
                    path = S[u][1][:]
                    path.append(d)
                    D[d] = (S[u][0]+v, path)
            except KeyError:
                continue
            except TypeError:
                break
    
    print "Answer"
    if S[dst][0] == '':
        print "No air routes"
        return
    print "Routes:",
    print '->'.join(map(lambda x: nameDict[x], S[dst][1]))
    print "Flight time:",
    print S[dst][0]
    return

def Prob_2(nodes, edges, nameDict):
    SCC = getSCC(nodes, edges)
    node_map = {}
    n_nodes = map(tuple,SCC)
    n_edges = {}
    source = set(n_nodes)
    sink = set(n_nodes)
    for v in n_nodes:
        for w in v:
            node_map[w]=v
    for v in nodes:
        t = node_map[v]
        if not n_edges.has_key(t):
            n_edges[t] = set([])
        for d in edges[v]:
            dest = node_map[d]
            if dest != t:
                n_edges[t] |= set([dest])
                source.discard(dest)
        if len(n_edges[t]) != 0:
            sink.discard(t)
    isolated = source & sink
    source -= isolated
    sink -= isolated
    I = list(isolated)
    
    V1, W1 = ST(n_nodes, n_edges, source, sink)
    V2, W2 = [], []
    rV = source - set(V1)
    rW = sink - set(W1)
    for i in xrange(min(len(rV), len(rW))):
        V2.append(rV.pop())
        W2.append(rW.pop())
    R = list(rV|rW)
    
    NEW_EDGE = []
    PATH = []
    
    if len(n_nodes) == 1:
        pass
    elif len(W1) == 0:
        PATH = I
        PATH.append(I[0])
    else:
        for i in range(len(W1)-1):
            NEW_EDGE.append((W1[i][0], V1[i][0]))
        for i in range(len(W2)):
            NEW_EDGE.append((W2[i][0], V2[i][0]))
        PATH = [W1[-1]]
        PATH.extend(R)
        PATH.extend(I)
        PATH.append(V1[0])
    for i in range(len(PATH)-1):
        NEW_EDGE.append((PATH[i][0],PATH[i+1][0]))
    
    print "#new air routes: %d" % len(NEW_EDGE)
    if len(NEW_EDGE) == 0:
        print "There is already no airport unreachable"
    for i in range(len(NEW_EDGE)):
        print "Route"+str(i+1)
        print "Src: %s Dst: %s" % (nameDict[NEW_EDGE[i][0]], nameDict[NEW_EDGE[i][1]])
    
    
def ST(DAG_nodes, DAG_edges, source, sink):
    mark = {}.fromkeys(DAG_nodes, False)
    unmarkedSource = set(source)
    ST.sinknotfound = True
    ST.w = 0
    def SEARCH(v):
        if not mark[v]:
            if v in sink:
                ST.w = v
                ST.sinknotfound = False
            mark[v] = True
            unmarkedSource.discard(v)
            for e in DAG_edges[v]:
                if ST.sinknotfound:
                    SEARCH(e)  
    vList = []
    wList = []
    while unmarkedSource != set([]):
        v = unmarkedSource.pop()
        ST.w = 0
        ST.sinknotfound = True
        SEARCH(v)
        if ST.w != 0:
            vList.append(v)
            wList.append(ST.w)
    return vList, wList
        
def getSCC(nodes, edges):
    indexList = {}.fromkeys(nodes,None)
    lowlinkList = {}.fromkeys(nodes,None)
    getSCC.index = 0
    S = []
    SCCList = []
    def SC(v):
        componant = []
        indexList[v] = getSCC.index
        lowlinkList[v] = getSCC.index
        getSCC.index += 1
        S.append(v)
        for d in edges[v]:
            if indexList[d] == None:
                C = SC(d)
                if C != None:
                    SCCList.append(C)
                lowlinkList[v] = min(lowlinkList[v], lowlinkList[d])
            elif d in S:
                lowlinkList[v] = min(lowlinkList[v], indexList[d])
        if lowlinkList[v] == indexList[v]:
            while True:
                w = S.pop()
                componant.append(w)
                if w == v:
                    break
            return componant
    for v in nodes:
        if indexList[v] == None:
            SCCList.append(SC(v))
    return SCCList

if __name__ == '__main__':
    main()