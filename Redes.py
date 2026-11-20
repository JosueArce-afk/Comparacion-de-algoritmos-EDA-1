import random
from Grafo import Grafo


def generar_red_aleatoria(num_vertices, max_capacidad, semilla=None):
    """
    Genera una red aleatoria (la misma semilla produce siempre la misma red).
    - origen = 0, destino = num_vertices - 1
    - camino principal 0 -> 1 -> ... -> n-1 (garantiza que el destino sea alcanzable)
    - aristas adicionales u -> v con u < v hasta llegar a ~2 * num_vertices aristas
      (si una arista se repite, se sobreescribe su capacidad; por eso el numero real
      de aristas se obtiene con g.contarAristas())
    - capacidades enteras en [1, max_capacidad]
    """
    rng = random.Random(semilla)
    g = Grafo(num_vertices)

    for i in range(num_vertices):
        g.agregar_vertice(i, f"v{i}")

    # Camino principal
    for i in range(num_vertices - 1):
        g.agregar_arista(i, i + 1, rng.randint(1, max_capacidad))

    # Aristas adicionales (rutas alternativas)
    num_aristas = num_vertices * 2
    aristas_restantes = num_aristas - (num_vertices - 1)
    for _ in range(max(0, aristas_restantes)):
        u = rng.randint(0, num_vertices - 2)
        v = rng.randint(u + 1, num_vertices - 1)
        g.agregar_arista(u, v, rng.randint(1, max_capacidad))

    return g


def generar_red_peor_caso(capacidad):
    """
    Red de 4 nodos que expone el peor caso de Ford-Fulkerson.

            +--> 1 --C--> 3(destino)
      0 -C-+    |  ^
            +--> 2 --C-->     (1 -> 2 tiene capacidad 1)

    origen = 0, destino = 3. Aristas: 0->1 = C, 0->2 = C, 1->2 = 1, 1->3 = C, 2->3 = C.
    Flujo maximo = 2C. Si Ford-Fulkerson elige siempre el camino 0-1-2-3 y luego
    0-2-1-3 (usando la arista residual de vuelta), cada camino envia solo 1 unidad
    y se necesitan 2C caminos. Edmonds-Karp usa solo 2 (0-1-3 y 0-2-3).
    """
    g = Grafo(4)
    for i, nombre in enumerate(["s", "a", "b", "t"]):
        g.agregar_vertice(i, nombre)
    g.agregar_arista(0, 1, capacidad)
    g.agregar_arista(0, 2, capacidad)
    g.agregar_arista(1, 2, 1)
    g.agregar_arista(1, 3, capacidad)
    g.agregar_arista(2, 3, capacidad)
    return g
