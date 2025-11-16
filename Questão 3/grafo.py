class Graph:

    # Estrutura de vértice lightweight para um grafo
    class Vertex:
      __slots__ ='_element'
      # Não chamar o construtor diretamente. Usar o método insert_vertex(x) do Grafo
      def __init__(self,x):
          self._element=x

    # Retorna o elemento associado a este vértice
      def element(self):
          return self._element
    
    # Permite que um vértice seja uma chave de um map/set
      def __hash__(self):
          return hash(id(self))

    # Estrutura de aresta lightweight para um grafo
    class Edge:

      __slots__='_origin','_destination','_element'

    # Não chamar o construtor diretamente. Usar o método insert_edge(u,v,x) do Grafo
      def __init__(self,u,v,x):
        self._origin=u
        self._destination=v
        self._element=x

    # Retorna a tupla(u,v) para os vértices u e v  
      def endpoints(self):
        return (self._origin,self._destination)

    # Retorna o vértice que é o oposto de v em esta aresta
      def opposite(self,v):
        return self._destination if v is self._origin else self._origin

    # Retorna o elemento associado a esta aresta
      def element(self):
        return self._element

    # Permite que uma aresta seja uma chave de um map/set
      def __hash__(self):
        return hash((self._origin, self._destination))       

    # Cria um grafo vazio (não direcionado, por padrão)
    # o grafo será direcionado se o parametro é fixado como True
    def __init__(self,directed=False):
        self._outgoing={}
        # Somente cria o segundo mapa para grafos direcionados; Usa alias para não direcionado
        self._incoming={} if directed else self._outgoing
  
    # Retorna True se é um grafo direcionado; False se não direcionado
    # O resultado depende da declaração original do grafo
    def is_directed(self):
        return self._incoming is not self._outgoing # Se os mapas são distintos

    # Retorna o número de vértices de um grafo
    def vertex_count(self):
        return len(self._outgoing)

    # Retorna uma iteração de todos os vértices do grafo
    def vertices(self):
        return self._outgoing.keys()

    # Retorna o número de arestas no grafo
    def edge_count(self):
        total=sum(len(self._outgoing[v]) for v in self._outgoing)
        return total if self.is_directed() else total//2

    # Retorna o conjunto de todas as arestas de um grafo
    def edges(self):
        result=set() # evita reportar arestas repetidamente para grafos não direcionados
        for secondary_map in self._outgoing.values():
            result.update(secondary_map.values()) # adiciona arestas ao conjunto
        return result

    # Retorna a aresta de u para v, ou None se não são adjacentes
    def get_edge(self,u,v):
        return self._outgoing[u].get(v)

    # Retorna o numero de arestas incidentes ao vértice v (externas ou de saida)
    def degree(self, v, outgoing=True):
        adj=self._outgoing if outgoing else self._incoming
        return len(adj[v])

    # Retorna todas as arestas incidentes ao vértice v (externas ou de saida)    
    def incident_edges(self,v,outgoing=True):
        adj=self._outgoing if outgoing else self._incoming
        for edge in adj[v].values():
            yield edge

    # Insere e retorna um novo vértice com elemento x
    def insert_vertex(self,x=None):
        v=self.Vertex(x)
        self._outgoing[v]={}
        if self.is_directed():
           self._incoming[v]={}
        return v

    # Insere e retorna uma nova aresta Edge de u a v com elemento auxiliar x
    def insert_edge(self,u,v,x=None):
        e=self.Edge(u,v,x)
        self._outgoing[u][v]=e
        self._incoming[v][u]=e

# Código adicional

    # Remove uma aresta entre os vértices u e v, se existir
    def remove_edge(self, u, v):
        edge = self.get_edge(u, v)
        if edge is not None:
            del self._outgoing[u][v]
            del self._incoming[v][u]

    # Remove um vértice v e todas as arestas incidentes a ele
    def remove_vertex(self, v):
        # Remove todas as arestas de saída
        for neighbor in list(self._outgoing[v]):
            self.remove_edge(v, neighbor)
        # Remove todas as arestas de entrada (se direcionado)
        if self.is_directed():
            for neighbor in list(self._incoming[v]):
                self.remove_edge(neighbor, v)
        # Remove o vértice dos mapas
        del self._outgoing[v]
        if self.is_directed():
            del self._incoming[v]

    # Permite iterar diretamente sobre os vértices do grafo
    def __iter__(self):
        return iter(self._outgoing)