from collections import deque


class Grafo:
    """
    Red de flujo representada con una matriz de capacidades [size][size].

    matrizCapacidades[u][v] = capacidad (residual) de la arista u -> v
    listaVertices: arreglo simple que guarda el nombre de cada nodo
    caminosAumento: cantidad de caminos de aumento usados en la ultima ejecucion

    Importante: los algoritmos modifican la matriz (la convierten en red residual).
    Para comparar dos algoritmos sobre la MISMA red hay que usar copiar().
    """

    def __init__(self, size):
        self.matrizCapacidades = [[0] * size for _ in range(size)]
        self.size = size
        self.listaVertices = [''] * size
        self.caminosAumento = 0

    # ------------------------------------------------------------------
    # Construccion de la red
    # ------------------------------------------------------------------
    def agregar_arista(self, u, v, c):
        """Pone la capacidad maxima de flujo de la arista u (origen) -> v (destino)."""
        self.matrizCapacidades[u][v] = c

    def agregar_vertice(self, indice, nombre):
        """Guarda el nombre de un nodo verificando que no salga del tamaño de la matriz."""
        if 0 <= indice < self.size:
            self.listaVertices[indice] = nombre

    def copiar(self):
        """Devuelve una copia independiente de la red (matriz y nombres de vertices)."""
        otro = Grafo(self.size)
        otro.matrizCapacidades = [fila[:] for fila in self.matrizCapacidades]
        otro.listaVertices = self.listaVertices[:]
        return otro

    def contarAristas(self):
        """Cantidad de aristas con capacidad > 0 (aristas reales, sin duplicados)."""
        return sum(1 for fila in self.matrizCapacidades for c in fila if c > 0)

    # ------------------------------------------------------------------
    # Operaciones comunes a ambos algoritmos
    # ------------------------------------------------------------------
    def _cuelloDeBotella(self, camino):
        """Capacidad residual minima a lo largo del camino (cuanto flujo se puede enviar)."""
        flujo = float("Inf")
        for i in range(len(camino) - 1):
            u, v = camino[i], camino[i + 1]
            flujo = min(flujo, self.matrizCapacidades[u][v])
        return flujo

    def _aumentarFlujo(self, camino, flujo):
        """Resta flujo en el sentido del camino y lo suma en el sentido contrario (red residual)."""
        for i in range(len(camino) - 1):
            u, v = camino[i], camino[i + 1]
            self.matrizCapacidades[u][v] -= flujo
            self.matrizCapacidades[v][u] += flujo

    # ------------------------------------------------------------------
    # Ford-Fulkerson (busqueda en profundidad)
    # ------------------------------------------------------------------
    def dfs(self, origen, destino):
        """
        Busqueda en profundidad (version iterativa, sin recursion).
        Encuentra un camino origen -> destino por aristas con capacidad residual > 0.
        Revisa los vecinos en orden de indice y devuelve el primer camino que encuentra
        (o None si el destino ya no es alcanzable). Usa la lista 'camino' como pila:
        si un nodo no tiene mas vecinos utiles, se retrocede (backtracking).
        """
        visitados = [False] * self.size
        visitados[origen] = True
        camino = [origen]
        siguiente = [0]  # siguiente vecino por revisar de cada nodo del camino

        while camino:
            nodoActual = camino[-1]
            if nodoActual == destino:
                return camino

            fila = self.matrizCapacidades[nodoActual]
            i = siguiente[-1]
            while i < self.size and (visitados[i] or fila[i] <= 0):
                i += 1

            if i == self.size:          # sin salida: retroceder
                camino.pop()
                siguiente.pop()
            else:                       # avanzar al vecino i
                siguiente[-1] = i + 1
                visitados[i] = True
                camino.append(i)
                siguiente.append(0)

        return None

    def caminoCuelloMinimo(self, origen, destino):
        """
        Selector 'adversario': entre TODOS los caminos simples con capacidad residual > 0
        devuelve el de menor cuello de botella.
        Ford-Fulkerson permite elegir cualquier camino de aumento; esta eleccion es la
        peor posible y se usa solo para mostrar el peor caso. Es exponencial, asi que
        solo debe usarse en redes muy pequeñas (por ejemplo, 4 nodos).
        """
        visitados = [False] * self.size
        mejor = [None, None]  # [camino, cuello de botella]

        def explorar(u, camino, cuello):
            if u == destino:
                if mejor[1] is None or cuello < mejor[1]:
                    mejor[0], mejor[1] = camino[:], cuello
                return
            visitados[u] = True
            fila = self.matrizCapacidades[u]
            for v in range(self.size):
                if not visitados[v] and fila[v] > 0:
                    camino.append(v)
                    explorar(v, camino, min(cuello, fila[v]))
                    camino.pop()
            visitados[u] = False

        explorar(origen, [origen], float("Inf"))
        return mejor[0]

    def fordFulkerson(self, origen, destino, estrategia="dfs"):
        """
        Metodo de Ford-Fulkerson: mientras exista un camino de aumento en la red residual,
        envia por el el maximo flujo posible (su cuello de botella).

        estrategia = "dfs"          -> camino hallado con busqueda en profundidad (por defecto)
                     "cuello_minimo" -> camino de menor cuello de botella (peor caso, redes pequeñas)

        Devuelve el flujo maximo. La cantidad de caminos usados queda en self.caminosAumento.
        """
        if estrategia == "dfs":
            buscar = self.dfs
        elif estrategia == "cuello_minimo":
            buscar = self.caminoCuelloMinimo
        else:
            raise ValueError("estrategia debe ser 'dfs' o 'cuello_minimo'")

        self.caminosAumento = 0
        flujoMax = 0

        camino = buscar(origen, destino)
        while camino is not None:
            flujo = self._cuelloDeBotella(camino)
            self._aumentarFlujo(camino, flujo)
            flujoMax += flujo
            self.caminosAumento += 1
            camino = buscar(origen, destino)

        return flujoMax

    # ------------------------------------------------------------------
    # Edmonds-Karp (busqueda en anchura)
    # ------------------------------------------------------------------
    def bfs(self, origen, destino, parent):
        """
        Busqueda en anchura: encuentra el camino con MENOS aristas entre origen y destino
        usando solo aristas con capacidad residual > 0.
        parent[v] guarda el nodo anterior a v en ese camino. Devuelve True si hay camino.
        Se detiene apenas llega al destino (el primer camino encontrado ya es el mas corto).
        """
        for i in range(self.size):
            parent[i] = -1
        visitados = [False] * self.size
        visitados[origen] = True
        cola = deque([origen])

        while cola:
            nodoActual = cola.popleft()
            fila = self.matrizCapacidades[nodoActual]
            for nodoVecino in range(self.size):
                if not visitados[nodoVecino] and fila[nodoVecino] > 0:
                    visitados[nodoVecino] = True
                    parent[nodoVecino] = nodoActual
                    if nodoVecino == destino:
                        return True
                    cola.append(nodoVecino)

        return False

    def edmonds_karp(self, origen, destino):
        """
        Edmonds-Karp = Ford-Fulkerson eligiendo siempre el camino de aumento mas corto (BFS).
        Devuelve el flujo maximo. La cantidad de caminos usados queda en self.caminosAumento.
        """
        self.caminosAumento = 0
        parent = [-1] * self.size
        flujoMax = 0

        while self.bfs(origen, destino, parent):   # encontrar un camino aumentante
            camino = [destino]
            v = destino
            while v != origen:
                v = parent[v]
                camino.append(v)
            camino.reverse()

            flujo = self._cuelloDeBotella(camino)
            self._aumentarFlujo(camino, flujo)
            flujoMax += flujo
            self.caminosAumento += 1

        return flujoMax

    # ------------------------------------------------------------------
    # Verificacion (teorema flujo maximo - corte minimo)
    # ------------------------------------------------------------------
    def capacidadCorteMinimo(self, grafoOriginal, origen):
        """
        Debe llamarse sobre la red YA procesada (residual). Calcula el conjunto S de nodos
        alcanzables desde 'origen' en la red residual y suma las capacidades ORIGINALES de
        las aristas que salen de S. Si el algoritmo es correcto, ese valor es igual al
        flujo maximo (teorema de flujo maximo y corte minimo).
        """
        alcanzables = [False] * self.size
        alcanzables[origen] = True
        cola = deque([origen])
        while cola:
            u = cola.popleft()
            for v in range(self.size):
                if not alcanzables[v] and self.matrizCapacidades[u][v] > 0:
                    alcanzables[v] = True
                    cola.append(v)

        corte = 0
        for u in range(self.size):
            if alcanzables[u]:
                for v in range(self.size):
                    if not alcanzables[v]:
                        corte += grafoOriginal.matrizCapacidades[u][v]
        return corte
