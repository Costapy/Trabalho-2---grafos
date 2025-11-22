import time
import random
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# --- Importações dos seus arquivos ---
from grafo import Graph
from dijkstra1 import dijkstra
from djikstra_estendido import dijkstra_estendido
from floyd import floyd_warshall

# Função auxiliar de reconstrução (caso não esteja exportada nos módulos)
def reconstruir_caminho_generico(origem_obj, destino_obj, predecessores):
    path = []
    curr = destino_obj
    while curr is not None:
        path.append(curr.element())
        if curr == origem_obj:
            break
        curr = predecessores.get(curr)
    
    if path and path[-1] == origem_obj.element():
        return path[::-1] # Inverte para ficar Inicio -> Fim
    return None

# --- 1. Geração do Grafo ---
def criar_grafo_labirinto(n):
    g = Graph(directed=True)
    grid = {}
    
    # Vértices
    for r in range(n):
        for c in range(n):
            nome = f"{r},{c}"
            v = g.insert_vertex(nome)
            grid[(r,c)] = v
            
    # Arestas
    for r in range(n):
        for c in range(n):
            u = grid[(r,c)]
            # Direita
            if c + 1 < n:
                v = grid[(r, c+1)]
                peso = random.randint(1, 20)
                g.insert_edge(u, v, peso)
                g.insert_edge(v, u, peso)
            # Baixo
            if r + 1 < n:
                v = grid[(r+1, c)]
                peso = random.randint(1, 20)
                g.insert_edge(u, v, peso)
                g.insert_edge(v, u, peso)
    return g

# --- 2. Função de Visualização ---
def desenhar_grafo(grafo_obj, caminho, algoritmo_nome, dimensao):
    """
    Plota o grafo usando NetworkX.
    """
    G_nx = nx.DiGraph()
    pos = {}
    
    # Construir grafo NetworkX e posições
    for v in grafo_obj.vertices():
        nome = v.element()
        G_nx.add_node(nome)
        try:
            r, c = map(int, nome.split(','))
            # (coluna, -linha) para ficar estilo matriz visualmente
            pos[nome] = (c, -r) 
        except:
            pos[nome] = (0,0)

    edge_colors = []
    edge_widths = []
    
    # Mapear arestas para verificar se pertencem ao caminho
    caminho_arestas = set()
    if caminho and len(caminho) > 1:
        for i in range(len(caminho)-1):
            caminho_arestas.add((caminho[i], caminho[i+1]))

    for e in grafo_obj.edges():
        u = e.endpoints()[0].element()
        v = e.endpoints()[1].element()
        G_nx.add_edge(u, v)
        
        if (u, v) in caminho_arestas:
            edge_colors.append('red')
            edge_widths.append(2.5)
        else:
            edge_colors.append('lightgray')
            edge_widths.append(0.5)

    # Configuração visual baseada no tamanho
    plt.figure(figsize=(10, 8))
    node_size = 600 if dimensao <= 10 else 100
    font_size = 8 if dimensao <= 10 else 0 # Esconde texto em grafos grandes
    
    # Desenhar
    nx.draw_networkx_nodes(G_nx, pos, node_size=node_size, node_color='lightblue')
    nx.draw_networkx_edges(G_nx, pos, edge_color=edge_colors, width=edge_widths, arrows=True, arrowsize=10)
    
    if font_size > 0:
        nx.draw_networkx_labels(G_nx, pos, font_size=font_size)

    # Destacar Caminho (Nós)
    if caminho:
        nx.draw_networkx_nodes(G_nx, pos, nodelist=caminho, node_color='orange', node_size=node_size)
        nx.draw_networkx_nodes(G_nx, pos, nodelist=[caminho[0]], node_color='green', node_size=node_size+50) # Início
        nx.draw_networkx_nodes(G_nx, pos, nodelist=[caminho[-1]], node_color='red', node_size=node_size+50)   # Fim

    plt.title(f"{algoritmo_nome} - Grid {dimensao}x{dimensao} - Custo Visualizado")
    plt.axis('off')
    
    # Pausa para visualizar sem travar o loop (ou block=False)
    print(f"  -> Exibindo gráfico para {algoritmo_nome} ({dimensao}x{dimensao}). Feche a janela para continuar.")
    plt.show()

# --- 3. Execução Principal ---
def main():
    dimensoes = [5, 10, 15, 20] 
    resultados_tabela = []

    for dim in dimensoes:
        print(f"\n=== PROCESSANDO DIMENSÃO {dim}x{dim} ===")
        g = criar_grafo_labirinto(dim)
        
        # Definir Início (0,0) e Fim (N-1, N-1) para garantir caminho longo visualmente
        mapa = {v.element(): v for v in g.vertices()}
        v_inicio = mapa["0,0"]
        v_fim = mapa[f"{dim-1},{dim-1}"]
        
        # --- DIJKSTRA SIMPLES ---
        # Nota: Dijkstra simples do seu código retorna apenas distâncias, não predecessores.
        # Não conseguimos desenhar o caminho apenas com distâncias. 
        # Vou pular o desenho dele ou teria que alterar o dijkstra1.py para retornar predecessores.
        start = time.perf_counter()
        dists_simples = dijkstra(g, v_inicio)
        tempo_dijkstra = time.perf_counter() - start
        # (Sem desenho para Dijkstra Simples pois ele não retorna caminho)

        # --- DIJKSTRA ESTENDIDO ---
        start = time.perf_counter()
        dists_ext, preds_ext = dijkstra_estendido(g, v_inicio)
        tempo_ext = time.perf_counter() - start
        
        caminho_ext = reconstruir_caminho_generico(v_inicio, v_fim, preds_ext)
        desenhar_grafo(g, caminho_ext, "Dijkstra Estendido", dim)

        # --- FLOYD WARSHALL ---
        start = time.perf_counter()
        matriz_dist, matriz_prox, lista_vertices_floyd = floyd_warshall(g)
        tempo_floyd = time.perf_counter() - start
        
        # Reconstrução Floyd
        # Precisamos mapear objetos para índices da matriz
        v_indices = {v: i for i, v in enumerate(lista_vertices_floyd)}
        idx_inicio = v_indices[v_inicio]
        idx_fim = v_indices[v_fim]
        
        caminho_floyd = []
        if matriz_prox[idx_inicio][idx_fim] is not None:
            atual = idx_inicio
            caminho_floyd.append(lista_vertices_floyd[atual].element())
            while atual != idx_fim:
                atual = matriz_prox[atual][idx_fim]
                caminho_floyd.append(lista_vertices_floyd[atual].element())
        
        desenhar_grafo(g, caminho_floyd, "Floyd-Warshall", dim)

        # Coleta de dados para Tabela
        resultados_tabela.append({
            "Dimensão": f"{dim}x{dim}",
            "Vértices": g.vertex_count(),
            "Arestas": g.edge_count(),
            "Dijkstra (s)": f"{tempo_dijkstra:.5f}",
            "Dijkstra Est (s)": f"{tempo_ext:.5f}",
            "Floyd (s)": f"{tempo_floyd:.5f}"
        })

    # Exibir Tabela Final
    df = pd.DataFrame(resultados_tabela)
    print("\n" + "="*60)
    print("TABELA DE RESULTADOS FINAIS")
    print("="*60)
    try:
        print(df.to_markdown(index=False))
    except:
        print(df.to_string(index=False))

if __name__ == "__main__":
    main()