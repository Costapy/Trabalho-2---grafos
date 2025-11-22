import time
import random
import pandas as pd

# Importação das classes e funções dos arquivos que você forneceu
from grafo import Graph
from dijkstra1 import dijkstra

from floyd import floyd_warshall
from djikstra_estendido import dijkstra_estendido

def criar_grafo_labirinto(n):
    """
    Cria um grafo planar tipo grade (grid) n x n.
    Representa um labirinto onde cada nó conecta-se aos vizinhos
    (direita e abaixo) com pesos aleatórios.
    """
    g = Graph(directed=True)
    grid = {}
    
    # 1. Criar Vértices
    # O grafo terá n * n vértices
    for r in range(n):
        for c in range(n):
            nome = f"{r},{c}"
            v = g.insert_vertex(nome)
            grid[(r,c)] = v
            
    # 2. Criar Arestas (Conectividade de grade)
    # Pesos aleatórios entre 1 e 20 para simular custos variados
    for r in range(n):
        for c in range(n):
            u = grid[(r,c)]
            
            # Conexão com o vizinho da Direita
            if c + 1 < n:
                v = grid[(r, c+1)]
                peso = random.randint(1, 20)
                # Como é um labirinto "aberto", criamos ida e volta
                g.insert_edge(u, v, peso)
                g.insert_edge(v, u, peso)
            
            # Conexão com o vizinho de Baixo
            if r + 1 < n:
                v = grid[(r+1, c)]
                peso = random.randint(1, 20)
                g.insert_edge(u, v, peso)
                g.insert_edge(v, u, peso)
                
    return g

def executar_testes():
    # Dimensões solicitadas para o teste
    dimensoes = [5, 10, 15, 20] 
    resultados = []

    print("Iniciando execução dos algoritmos...\n")

    for dim in dimensoes:
        # Geração do Grafo
        g = criar_grafo_labirinto(dim)
        
        # Coleta de Métricas do Grafo
        ordem = g.vertex_count()         # Número de Vértices
        tamanho = g.edge_count()         # Número de Arestas
        
        # Cálculo dos graus
        graus = [g.degree(v) for v in g.vertices()]
        grau_medio = sum(graus) / len(graus) if graus else 0
        grau_max = max(graus) if graus else 0
        
        # Escolha de um vértice de origem aleatório para os Dijkstras
        lista_vertices = list(g.vertices())
        origem = random.choice(lista_vertices)
        
        print(f"Processando Grid {dim}x{dim} (V={ordem}, E={tamanho})...")
        
        # --- Benchmark 1: Dijkstra Padrão ---
        inicio = time.perf_counter()
        dijkstra(g, origem)
        fim = time.perf_counter()
        tempo_dijkstra = fim - inicio
        
        # --- Benchmark 2: Dijkstra Estendido ---
        inicio = time.perf_counter()
        dijkstra_estendido(g, origem)
        fim = time.perf_counter()
        tempo_dijkstra_est = fim - inicio
        
        # --- Benchmark 3: Floyd-Warshall ---
        # Nota: Floyd é O(V^3). Para V=400 (20x20), isso pode levar alguns segundos.
        inicio = time.perf_counter()
        floyd_warshall(g)
        fim = time.perf_counter()
        tempo_floyd = fim - inicio
        
        # Armazenar dados na lista
        resultados.append({
            "Dimensão (N)": f"{dim}x{dim}",
            "Ordem (V)": ordem,
            "Tamanho (E)": tamanho,
            "Grau Médio": f"{grau_medio:.2f}",
            "Grau Máx": grau_max,
            "Dijkstra (s)": f"{tempo_dijkstra:.6f}",
            "Dijkstra Est. (s)": f"{tempo_dijkstra_est:.6f}",
            "Floyd (s)": f"{tempo_floyd:.6f}"
        })

    # Criar DataFrame para exibição da tabela
    df = pd.DataFrame(resultados)
    return df

if __name__ == "__main__":
    # Instalar pandas se necessário: pip install pandas tabulate
    df_resultado = executar_testes()
    
    print("\n" + "="*80)
    print("TABELA COMPARATIVA DE DESEMPENHO")
    print("="*80)
    
    # Exibe a tabela formatada no console
    # O parâmetro index=False remove o índice numérico padrão do Pandas
    try:
        print(df_resultado.to_markdown(index=False, numalign="center", stralign="center"))
    except ImportError:
        # Fallback caso a tabulate não esteja instalada
        print(df_resultado.to_string(index=False))

    print("\n" + "="*80)
    print("Observação: O tempo do Floyd cresce cubicamente O(V^3),")
    print("enquanto Dijkstra cresce de forma quase linear para grafos esparsos.")