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
        else:
            print(f"Aviso: Vértice em aresta ({u_nome}, {v_nome}) não encontrado. Aresta ignorada.")

    return g, mapeamento_vertices

import heapq

def dijkstra(grafo, origem):
    dist = {v: float('inf') for v in grafo.vertices()}
    dist[origem] = 0

    fila = []
    contador = 0  # serve para desempatar
    
    heapq.heappush(fila, (0, contador, origem))

    while fila:
        distancia_atual, _, u = heapq.heappop(fila)

        if distancia_atual > dist[u]:
            continue

        for aresta in grafo.incident_edges(u, outgoing=True):
            v = aresta.opposite(u)
            peso = aresta.element()

            nova_dist = distancia_atual + peso

            if nova_dist < dist[v]:
                dist[v] = nova_dist
                contador += 1
                heapq.heappush(fila, (nova_dist, contador, v))

    return dist

if __name__ == "__main__":
    lista_vertices = [1, 2, 3, 4, 5, 6]
    lista_arestas = [
        (1, 2, 2),  # C[1,2]
        (3, 1, 1),  # C[3,1]
        (3, 2, 3),  # C[3,2]
        (4, 1, 2),  # C[4,1]
        (4, 3, 2),  # C[4,3]
        (5, 3, 10), # C[5,3]
        (5, 4, 5),  # C[5,4]
        (5, 6, 4),  # C[5,6]
        (6, 1, 5),  # C[6,1]
        (6, 4, 1)   # C[6,4]
    ]

    G_direcionado, vertices_map = criar_grafo(lista_vertices, lista_arestas, direcionado=True)
    
    print("--- Representação Computacional do Grafo (Questão 1.i) ---")
    print(f"O grafo é direcionado? {G_direcionado.is_directed()}")
    print(f"Número de vértices: {G_direcionado.vertex_count()}")
    print(f"Número de arestas: {G_direcionado.edge_count()}")
    
    print("\nArestas e seus pesos (Origem -> Destino: Peso):")
    for aresta in G_direcionado.edges():
        origem, destino = aresta.endpoints()
        print(f"  - Aresta ({origem.element()} -> {destino.element()}) com peso {aresta.element()}")

    print("\n--- Verificação Cruzada (Saídas do Nó 5) ---")
    v5 = vertices_map[5] 
    print(f"Grau de saída (out-degree) do nó 5: {G_direcionado.degree(v5, outgoing=True)}")
    print("Arestas de saída do nó 5:")
    for e in G_direcionado.incident_edges(v5, outgoing=True):
        print(f"  - 5 -> {e.opposite(v5).element()} (Peso: {e.element()})")
    
    
    distancias = dijkstra(G_direcionado, vertices_map[5])
    for v, d in distancias.items():
        print(f"Distância até {v.element()}: {d}")
