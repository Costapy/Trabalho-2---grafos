import networkx as nx
import matplotlib.pyplot as plt

def visualizar_grafo_e_caminho(grafo_custom, caminho_lista=None, titulo="Visualização do Grafo"):
    """
    Converte o grafo customizado para NetworkX e plota o caminho.
    Args:
        grafo_custom: Instância da classe Graph.
        caminho_lista: Lista de identificadores dos vértices (ex: ['0,0', '0,1', ...]).
    """
    G_nx = nx.DiGraph()
    pos = {}
    edge_labels = {}

    # 1. Converter Vértices e criar Layout de Grid
    for v in grafo_custom.vertices():
        nome = v.element() # Ex: "2,3"
        G_nx.add_node(nome)
        
        # Parse da string "linha,coluna" para coordenadas (x, -y)
        # Usamos -y para que a linha 0 fique no topo e a linha N embaixo
        try:
            r, c = map(int, nome.split(','))
            pos[nome] = (c, -r) 
        except ValueError:
            # Fallback se os nomes não forem coordenadas (ex: 'A', 'B')
            pos = nx.spring_layout(G_nx)

    # 2. Converter Arestas
    for e in grafo_custom.edges():
        u_nome = e.endpoints()[0].element()
        v_nome = e.endpoints()[1].element()
        peso = e.element()
        
        G_nx.add_edge(u_nome, v_nome, weight=peso)
        edge_labels[(u_nome, v_nome)] = peso

    plt.figure(figsize=(10, 8))
    
    # 3. Desenhar Grafo Base (Nós e Arestas cinzas)
    nx.draw_networkx_nodes(G_nx, pos, node_size=700, node_color='lightblue')
    nx.draw_networkx_edges(G_nx, pos, edge_color='gray', arrowstyle='->', arrowsize=10)
    nx.draw_networkx_labels(G_nx, pos, font_size=10, font_family="sans-serif")
    
    # Desenhar pesos apenas se o grafo for pequeno (para não poluir)
    if grafo_custom.vertex_count() <= 25:
        nx.draw_networkx_edge_labels(G_nx, pos, edge_labels=edge_labels, font_size=8)

    # 4. Destacar o Caminho Mínimo (Se fornecido)
    if caminho_lista and len(caminho_lista) > 1:
        # Criar lista de arestas do caminho (pares consecutivos)
        path_edges = list(zip(caminho_lista, caminho_lista[1:]))
        
        # Desenhar nós do caminho
        nx.draw_networkx_nodes(G_nx, pos, nodelist=caminho_lista, node_color='orange', node_size=700)
        # Desenhar nó de Início (Verde) e Fim (Vermelho)
        nx.draw_networkx_nodes(G_nx, pos, nodelist=[caminho_lista[0]], node_color='lightgreen', node_size=800)
        nx.draw_networkx_nodes(G_nx, pos, nodelist=[caminho_lista[-1]], node_color='salmon', node_size=800)
        
        # Desenhar arestas do caminho (Vermelho e mais grossas)
        nx.draw_networkx_edges(G_nx, pos, edgelist=path_edges, edge_color='red', width=2.5)

    plt.title(titulo)
    plt.axis('off')
    plt.tight_layout()
    plt.show()