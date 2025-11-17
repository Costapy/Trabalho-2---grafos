from grafo import Graph
import heapq

def criar_grafo(vertices_nomes, arestas_dados, direcionado=False):
    g = Graph(directed=direcionado)
    mapeamento_vertices = {}

    for nome in vertices_nomes:
        vertice_obj = g.insert_vertex(nome)
        mapeamento_vertices[nome] = vertice_obj

    for u_nome, v_nome, peso in arestas_dados:
        if u_nome in mapeamento_vertices and v_nome in mapeamento_vertices:
            u = mapeamento_vertices[u_nome]
            v = mapeamento_vertices[v_nome]
            g.insert_edge(u, v, peso)

    return g, mapeamento_vertices

def dijkstra(g, vertice_inicial):
    distancias = {v: float('inf') for v in g.vertices()}
    predecessores = {v: None for v in g.vertices()}
    distancias[vertice_inicial] = 0
    
    # Fila: (distancia, contador_desempate, vertice)
    pq = []
    counter = 0 
    heapq.heappush(pq, (0, counter, vertice_inicial))
    
    while pq:
        d, _, u = heapq.heappop(pq) # _ descarta o contador
        
        if d > distancias[u]:
            continue
            
        for aresta in g.incident_edges(u, outgoing=True):
            v = aresta.opposite(u)
            peso = aresta.element()
            
            if distancias[u] + peso < distancias[v]:
                distancias[v] = distancias[u] + peso
                predecessores[v] = u
                counter += 1
                # Adiciona o contador para evitar comparação direta entre Vértices
                heapq.heappush(pq, (distancias[v], counter, v))
                
    return distancias, predecessores

def reconstruir_caminho(inicio_obj, fim_obj, predecessores):
    caminho = []
    atual = fim_obj
    
    while atual is not None:
        caminho.append(atual.element())
        if atual == inicio_obj:
            break
        atual = predecessores.get(atual)
    
    if not caminho or caminho[-1] != inicio_obj.element():
        return None
        
    return caminho[::-1]

if __name__ == "__main__":
    
    lista_vertices = [1, 2, 3, 4, 5, 6]
    
    lista_arestas = [
        (1, 2, 2), (3, 1, 1), (3, 2, 3), (4, 1, 2), (4, 3, 2),
        (5, 3, 10), (5, 4, 5), (5, 6, 4), (6, 1, 5), (6, 4, 1)
    ]

    G_direcionado, vertices_map = criar_grafo(lista_vertices, lista_arestas, direcionado=True)

    rotulo_inicio = 5
    rotulo_fim = 1
    
    vertice_inicio = vertices_map[rotulo_inicio]
    vertice_fim = vertices_map[rotulo_fim]
    
    distancias, predecessores = dijkstra(G_direcionado, vertice_inicio)
    caminho_minimo = reconstruir_caminho(vertice_inicio, vertice_fim, predecessores)
    custo_total = distancias.get(vertice_fim)
    
    print("\nResultados:")
    if caminho_minimo:
        print(f"  -> Caminho Mínimo (5 para 1): {' -> '.join(map(str, caminho_minimo))}")
        print(f"  -> Custo Total: {custo_total}")
    else:
        print(f"Não foi encontrado um caminho.")