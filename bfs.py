def search(G, start_vertex):
    Visited = {start_vertex} #set of edges? darts? vertices?
    Waiting = [start_vertex]
    Parent = {}
    Level = {start_vertex:0}
    while len(Waiting) > 0:
        v = Waiting.pop()
        for incoming_dart in G.incoming(v):
            outgoing_dart = G.rev(incoming_dart)
            w = G.head[outgoing_dart]
            if w not in Visited:
                Visited.add(w)
                Level[w] = 1 + Level[v]
                Parent[w] = outgoing_dart
                Waiting.insert(0,w)
    return Level, Parent
    
