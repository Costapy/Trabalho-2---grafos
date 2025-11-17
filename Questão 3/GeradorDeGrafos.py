"""
Gerador de grafos para testar Dijkstra / versão estendida.
Cria grafos com N = 10, 50, 100, 500 vértices dos tipos:
 - grafo planar em grade (grid / labirinto)
 - grafo geométrico aleatório (random geometric graph)
 - grafo cubo (hypercube)

Compatível com a classe Graph definida em `grafo.py` (import: from grafo import Graph).
Fornece funções que retornam listas de vértices (rótulos simples) e arestas no formato
  [(u_label, v_label, peso), ...]
pronto para usar com `criar_grafo(vertices, arestas, direcionado=...)` do seu main.py.

Uso rápido:
  from graph_generators import make_all_graphs
  outputs = make_all_graphs(sizes=[10,50,100,500], seed=42)
  # outputs é dict[type][n] -> { 'vertices': [...], 'edges': [...], 'meta': {...} }

Os geradores tentam produzir exatamente N vértices. Quando a construção natural (por ex 2^d)
produz mais vértices, removemos alguns vértices aleatoriamente (mantendo conectividade quando
possível). Pesos são gerados aleatoriamente no intervalo [w_min, w_max] e há opção de gerar
"controlados" (ex: maioria de arestas com peso baixo + algumas arestas "longas").

"""

import math
import random
import itertools
import json
from collections import deque

# ---------- Helpers ----------

def _label(i):
    # rótulo simples como inteiro (compatível com seu main.py que usa inteiros)
    return i

def _assign_weights(edges, seed=None, w_min=1, w_max=20, controlled=False, long_tail_frac=0.05):
    rnd = random.Random(seed)
    weighted = []
    for u,v in edges:
        if not controlled:
            w = rnd.uniform(w_min, w_max)
        else:
            # maioria com peso baixo, uma pequena fracção com peso alto
            if rnd.random() < long_tail_frac:
                w = rnd.uniform((w_max*0.6)+1, w_max)
            else:
                w = rnd.uniform(w_min, max(w_min+1, w_max*0.3))
        # usar pesos inteiros para simplicidade
        weighted.append((u, v, int(round(w))))
    return weighted

# ---------- Grid / planar graph generator ----------

def grid_graph(n_vertices, seed=None, connect_diagonals=False):
    """Cria um grafo grade (2D) com aproximadamente n_vertices.
    Se houver excesso de vértices, remove vértices aleatoriamente (mantendo rótulos sequenciais).
    Retorna (vertices_list, edge_pairs_list) sem pesos.
    """
    rnd = random.Random(seed)
    # encontrar dims
    cols = math.ceil(math.sqrt(n_vertices))
    rows = math.ceil(n_vertices / cols)

    # criar coordenadas e mapear para ids
    coords = []
    for r in range(rows):
        for c in range(cols):
            coords.append((r, c))
    coords = coords[:n_vertices]

    index_of = {coords[i]: i for i in range(len(coords))}
    vertices = [_label(i+1) for i in range(len(coords))]

    edges = []
    for (r,c), i in index_of.items():
        # vizinho direita
        if (r, c+1) in index_of:
            edges.append((vertices[i], vertices[index_of[(r, c+1)]]))
        # vizinho baixo
        if (r+1, c) in index_of:
            edges.append((vertices[i], vertices[index_of[(r+1, c)]]))
        if connect_diagonals:
            if (r+1, c+1) in index_of:
                edges.append((vertices[i], vertices[index_of[(r+1, c+1)]]))
            if (r+1, c-1) in index_of:
                edges.append((vertices[i], vertices[index_of[(r+1, c-1)]]))

    return vertices, edges

# ---------- Maze-like modification (optional) ----------

def grid_maze_like(n_vertices, seed=None):
    """Gera grade e então remove algumas arestas para criar uma aparência de labirinto,
    mantendo o grafo conectado (gera spanning tree + adiciona algumas arestas aleatórias).
    """
    vertices, _ = grid_graph(n_vertices, seed=seed, connect_diagonals=False)
    n = len(vertices)
    # construir vizinhança regular pela posição em grid recalculada
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    coords = [(r, c) for r in range(rows) for c in range(cols)][:n]
    index_of = {coords[i]: i for i in range(n)}

    # possível arestas (grade)
    possible = []
    for (r,c), i in index_of.items():
        u = vertices[i]
        if (r, c+1) in index_of:
            v = vertices[index_of[(r, c+1)]]
            possible.append((u,v))
        if (r+1, c) in index_of:
            v = vertices[index_of[(r+1, c)]]
            possible.append((u,v))

    rnd = random.Random(seed)
    # criar spanning tree (Kruskal-like via shuffle + union-find)
    parent = list(range(n))
    def find(a):
        while parent[a]!=a:
            parent[a]=parent[parent[a]]
            a=parent[a]
        return a
    def union(a,b):
        ra, rb = find(a), find(b)
        parent[ra]=rb

    edges = []
    shuffled = possible[:]
    rnd.shuffle(shuffled)
    for u,v in shuffled:
        ui = int(u)-1
        vi = int(v)-1
        if find(ui)!=find(vi):
            union(ui,vi)
            edges.append((u,v))
    # adiciona algumas arestas extras para criar ciclo e opções
    extras = int(0.15 * len(possible))
    candidates = [e for e in possible if e not in edges and (e[1],e[0]) not in edges]
    rnd.shuffle(candidates)
    edges.extend(candidates[:extras])

    return vertices, edges

# ---------- Random geometric graph ----------

def random_geometric_graph(n_vertices, seed=None, radius=None):
    """Gera um random geometric graph: coloca pontos em [0,1]^2 e conecta pares com distância <= radius.
    Se radius for None, calcula um valor heurístico para garantir conectividade aproximada.
    Retorna (vertices, edges) sem pesos.
    """
    rnd = random.Random(seed)
    points = [(rnd.random(), rnd.random()) for _ in range(n_vertices)]
    if radius is None:
        # heurística: radius ~ sqrt((log n)/(pi n)) * factor
        factor = 1.5
        radius = factor * math.sqrt(max(1e-9, math.log(max(2, n_vertices)) / (math.pi * n_vertices)))

    vertices = [_label(i+1) for i in range(n_vertices)]
    edges = []
    for i in range(n_vertices):
        xi, yi = points[i]
        for j in range(i+1, n_vertices):
            xj, yj = points[j]
            dx = xi-xj; dy = yi-yj
            if dx*dx + dy*dy <= radius*radius:
                edges.append((vertices[i], vertices[j]))
    return vertices, edges

# ---------- Hypercube graph (Q_d) ----------

def hypercube_graph(n_vertices, seed=None):
    """Gera um grafo cubo de dimensão d (2^d vértices). Se 2^d > n_vertices, remove alguns vértices
    aleatoriamente mas tenta manter conectividade.
    Retorna (vertices, edges).
    """
    rnd = random.Random(seed)
    d = math.ceil(math.log2(max(1, n_vertices)))
    N = 2**d
    # rótulos serão inteiros 1..N (representação binária usada apenas internamente)
    vertices_binary = [i for i in range(N)]
    # opcional: se N > n_vertices, remover alguns vértices (escolha aleatória)
    if N > n_vertices:
        remove_count = N - n_vertices
        to_remove = set(rnd.sample(vertices_binary, remove_count))
        vertices_binary = [v for v in vertices_binary if v not in to_remove]

    # map to labels
    index_map = {vertices_binary[i]: i+1 for i in range(len(vertices_binary))}
    vertices = [index_map[b] for b in vertices_binary]

    edges = []
    for b in vertices_binary:
        for bit in range(d):
            nb = b ^ (1<<bit)
            # only add if neighbor still present and to avoid duplicates, only add if nb > b
            if nb in index_map and nb > b:
                edges.append((index_map[b], index_map[nb]))

    # if removing vertices disconnected graph, we do a BFS from node 1 and keep largest component
    if len(vertices) > 0:
        # build adjacency
        adj = {v: [] for v in vertices}
        for u,v in edges:
            adj[u].append(v); adj[v].append(u)
        start = vertices[0]
        visited = set()
        q = deque([start]); visited.add(start)
        while q:
            x = q.popleft()
            for nb in adj[x]:
                if nb not in visited:
                    visited.add(nb); q.append(nb)
        if len(visited) < len(vertices):
            # keep only visited vertices and edges among them
            kept = visited
            vertices = [v for v in vertices if v in kept]
            edges = [(u,v) for (u,v) in edges if u in kept and v in kept]

    return vertices, edges

# ---------- Utility: build weighted edge lists and save/export ----------

def build_weighted_graph(vertices, edges_pairs, seed=None, w_min=1, w_max=20, controlled=False):
    weighted = _assign_weights(edges_pairs, seed=seed, w_min=w_min, w_max=w_max, controlled=controlled)
    return vertices, weighted


def save_as_json(path, vertices, edges):
    data = {
        'vertices': vertices,
        'edges': edges
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------- High-level runner ----------

def make_all_graphs(sizes=[10,50,100,500], seed=1234, w_min=1, w_max=20, controlled_weights=False):
    """Gera e retorna um dicionário com todas as variantes pedidas.
    Estrutura: result["grid"][n] = { 'vertices': [...], 'edges': [(u,v,w), ...], 'meta': {...} }
    """
    result = { 'grid':{}, 'maze':{}, 'geometric':{}, 'hypercube':{} }
    for n in sizes:
        # grid
        v_g, e_g = grid_graph(n, seed=seed)
        vs, ws = build_weighted_graph(v_g, e_g, seed=seed+1+n, w_min=w_min, w_max=w_max, controlled=controlled_weights)
        result['grid'][n] = { 'vertices': vs, 'edges': ws, 'meta': { 'raw_edges': len(e_g) } }

        # maze-like grid (spanning tree + extras)
        v_m, e_m = grid_maze_like(n, seed=seed)
        vs, ws = build_weighted_graph(v_m, e_m, seed=seed+2+n, w_min=w_min, w_max=w_max, controlled=controlled_weights)
        result['maze'][n] = { 'vertices': vs, 'edges': ws, 'meta': { 'raw_edges': len(e_m) } }

        # geometric
        v_r, e_r = random_geometric_graph(n, seed=seed)
        vs, ws = build_weighted_graph(v_r, e_r, seed=seed+3+n, w_min=w_min, w_max=w_max, controlled=controlled_weights)
        result['geometric'][n] = { 'vertices': vs, 'edges': ws, 'meta': { 'raw_edges': len(e_r) } }

        # hypercube
        v_h, e_h = hypercube_graph(n, seed=seed)
        vs, ws = build_weighted_graph(v_h, e_h, seed=seed+4+n, w_min=w_min, w_max=w_max, controlled=controlled_weights)
        result['hypercube'][n] = { 'vertices': vs, 'edges': ws, 'meta': { 'raw_edges': len(e_h), 'actual_vertices': len(v_h) } }

    return result

# ---------- CLI quick test ----------
if __name__ == '__main__':
    # exemplo de execução que salva os grafos em JSON
    outputs = make_all_graphs(sizes=[10,50,100,500], seed=42, w_min=1, w_max=30, controlled_weights=True)
    for kind, mapping in outputs.items():
        for n, data in mapping.items():
            path = f'graph_{kind}_{n}.json'
            save_as_json(path, data['vertices'], data['edges'])
            print(f'Salvo {path}: |V|={len(data["vertices"])}, |E|={len(data["edges"])}, meta={data["meta"]}')

    print('\nPronto. Use criar_grafo(vertices, edges) do seu main.py para carregar e testar Dijkstra.')
