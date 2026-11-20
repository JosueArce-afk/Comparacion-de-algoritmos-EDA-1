from Redes import generar_red_aleatoria
import time

tamanos_red = [50, 100, 200, 400, 800]  # cantidad de vertices
capacidad_maxima = 50                   # capacidad maxima que pueda pasar por una arista
instancias = 10                         # redes distintas por tamaño

print("Algoritmo: Edmonds-Karp (BFS)")
print("Vertices, Aristas(prom), Caminos(prom), Flujo(prom), Tiempo(s)(prom)")

for v in tamanos_red:  # prueba cada tamaño de red
    aristas, caminos, flujos, tiempos = [], [], [], []
    for k in range(instancias):
        # misma semilla que TestAlgoritmoFord.py: ambos algoritmos reciben las mismas redes
        g = generar_red_aleatoria(v, capacidad_maxima, semilla=1000 * k + (v % 997))
        aristas.append(g.contarAristas())

        origen = 0       # donde empieza el flujo
        destino = v - 1  # donde termina

        inicio = time.perf_counter()               # iniciamos contador
        flujo = g.edmonds_karp(origen, destino)    # llamamos a la funcion en la clase
        fin = time.perf_counter()                  # terminamos contador

        tiempos.append(fin - inicio)
        caminos.append(g.caminosAumento)
        flujos.append(flujo)

    n = instancias
    print(f"{v}, {sum(aristas)/n:.1f}, {sum(caminos)/n:.1f}, {sum(flujos)/n:.1f}, {sum(tiempos)/n:.8f}")
