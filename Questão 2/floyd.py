from grafo import Graph

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


def floyd_warshall(g):
    vertices = sorted(list(g.vertices()), key=lambda v: v.element())
    n = len(vertices)
    v_para_idx = {v: i for i, v in enumerate(vertices)}

    dist = [[float('inf')] * n for _ in range(n)]
    prox = [[None] * n for _ in range(n)]

    for i in range(n):
        dist[i][i] = 0
        prox[i][i] = i

    for aresta in g.edges():
        u, v = aresta.endpoints()
        i, j = v_para_idx[u], v_para_idx[v]
        
        if aresta.element() < dist[i][j]:
             dist[i][j] = aresta.element()
             prox[i][j] = j 

    for k in range(n):    
        for i in range(n): 
            for j in range(n): 
                
                custo_via_k = dist[i][k] + dist[k][j]
                
                if dist[i][j] > custo_via_k:
                    dist[i][j] = custo_via_k
                    prox[i][j] = prox[i][k] 
                    
    for i in range(n):
        if dist[i][i] < 0:
            print(f"ALERTA: Ciclo negativo detectado envolvendo o nó {vertices[i].element()}!")
            
    return dist, prox, vertices

def reconstruir_caminho_floyd(i, j, prox, vertices):
    if prox[i][j] is None:
        return None, float('inf')
        
    caminho = []
    atual_idx = i
    
    while atual_idx != j:
        caminho.append(vertices[atual_idx].element())
        atual_idx = prox[atual_idx][j]
        
        if atual_idx is None: 
             return None, float('inf')
             
    caminho.append(vertices[j].element())
        
    return caminho

def imprimir_matriz(matriz, vertices, cabecalho):
    print(f"\n{cabecalho}:")
    n = len(vertices)
    
    print("De\\Para| ", end="")
    for v in vertices:
        print(f"{v.element():>5}", end=" ")
    print()
    print("-" * (7 + 6 * n))

    for i, v_origem in enumerate(vertices):
        print(f" {v_origem.element():>4} | ", end="")
        for j in range(n):
            valor = matriz[i][j]
            if valor == float('inf'):
                print(f"{'inf':>5}", end=" ")
            elif valor is None:
                print(f"{'N/A':>5}", end=" ")
            else:
                if cabecalho.startswith("Matriz de Próximos"):
                     print(f"{vertices[valor].element():>5}", end=" ")
                else:
                     print(f"{valor:>5.0f}", end=" ")
        print() 

if __name__ == "__main__":
    lista_vertices = [1, 2, 3, 4, 5, 6]
    
    lista_arestas = [
        (1, 2, 2),
        (3, 1, -4),
        (3, 2, 3),
        (3, 4, -7),
        (4, 1, 2),
        (5, 3, 10),
        (5, 4, 5),
        (5, 6, 4),
        (6, 1, 5),
        (6, 4, 1)
    ]

    G_direcionado, vertices_map = criar_grafo(lista_vertices, lista_arestas, direcionado=True)

    print("--- Executando Algoritmo de Floyd-Warshall (Todos-para-Todos) ---")
    
    dist_matrix, prox_matrix, vertices_fw = floyd_warshall(G_direcionado)

    imprimir_matriz(dist_matrix, vertices_fw, "Matriz de Distâncias Mínimas")
    imprimir_matriz(prox_matrix, vertices_fw, "Matriz de Próximos (Predecessores)")

    print("\n" + "="*40)
    print("--- Reconstrução de Caminho (Exemplo 5 -> 2) ---")
    
    idx_map_fw = {v.element(): i for i, v in enumerate(vertices_fw)}
    rotulo_inicio = 5
    rotulo_fim = 2
    
    idx_inicio = idx_map_fw[rotulo_inicio]
    idx_fim = idx_map_fw[rotulo_fim]

    caminho_fw = reconstruir_caminho_floyd(idx_inicio, idx_fim, prox_matrix, vertices_fw)
    custo_fw = dist_matrix[idx_inicio][idx_fim]

    if caminho_fw:
        print(f"  -> Caminho Mínimo ({rotulo_inicio} para {rotulo_fim}): {' -> '.join(map(str, caminho_fw))}")
        print(f"  -> Custo Total: {custo_fw}")
    else:
        print(f"Não foi encontrado um caminho de {rotulo_inicio} para {rotulo_fim}.")

    print("\n" + "="*40)
    print("--- Verificação de Ciclo (Exemplo 1 -> ... -> 1) ---")
    idx_ciclo = idx_map_fw[1]
    custo_ciclo = dist_matrix[idx_ciclo][idx_ciclo]
    print(f"Custo do caminho (1 -> 1): {custo_ciclo}")
    if custo_ciclo < 0:
        print("  -> Ciclo negativo detectado!")