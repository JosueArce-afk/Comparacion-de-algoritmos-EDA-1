"""
Experimento comparativo Ford-Fulkerson vs Edmonds-Karp.   Ejecutar:  python Experimento.py

Experimento 1: redes aleatorias de 50 a 800 nodos (10 instancias por tamaño, capacidades 1..50).
Experimento 2: red aleatoria de 200 nodos con capacidades maximas de 10 a 100 000 (10 instancias).
Experimento 3: red de 4 nodos que expone el peor caso de Ford-Fulkerson (capacidades 10 a 100 000).

Para cada instancia ambos algoritmos corren sobre una COPIA de la misma red y se verifica
que el flujo coincida y que sea igual al corte minimo. Guarda CSV y graficos en ./resultados
"""
import csv
import os
import statistics as est
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from Redes import generar_red_aleatoria, generar_red_peor_caso

# ---------------------------- parametros ----------------------------
TAMANOS = [50, 100, 200, 400, 800]            # Experimento 1
CAPACIDAD_MAX_EXP1 = 50
INSTANCIAS = 10
VERTICES_EXP2 = 200                           # Experimento 2
CAPACIDADES_EXP2 = [10, 100, 1000, 10_000, 100_000]
CAPACIDADES_PEOR_CASO = [10, 100, 1000, 10_000, 100_000]   # Experimento 3
CARPETA = "resultados"
# ---------------------------------------------------------------------


def medir(grafo, metodo, *args, **kwargs):
    """Ejecuta un algoritmo y devuelve (flujo, tiempo en segundos, caminos de aumento)."""
    inicio = time.perf_counter()
    flujo = getattr(grafo, metodo)(*args, **kwargs)
    fin = time.perf_counter()
    return flujo, fin - inicio, grafo.caminosAumento


def comparar_instancia(original, origen, destino):
    """Corre FF (DFS) y EK sobre copias de la misma red y valida los resultados."""
    gf, ge = original.copiar(), original.copiar()
    ff, t_ff, c_ff = medir(gf, "fordFulkerson", origen, destino)
    ek, t_ek, c_ek = medir(ge, "edmonds_karp", origen, destino)

    assert ff == ek, f"flujos distintos: FF={ff}, EK={ek}"
    assert ff == gf.capacidadCorteMinimo(original, origen), "FF no cumple flujo = corte minimo"
    assert ek == ge.capacidadCorteMinimo(original, origen), "EK no cumple flujo = corte minimo"
    return dict(flujo=ff, t_ff=t_ff, t_ek=t_ek, c_ff=c_ff, c_ek=c_ek)


def resumir(filas, clave):
    valores = [f[clave] for f in filas]
    return est.mean(valores), (est.stdev(valores) if len(valores) > 1 else 0.0)


def experimento_aleatorio(parametros, fabricar, etiqueta):
    """parametros: lista de valores; fabricar(valor, semilla) -> (red, aristas). Devuelve resumen por valor."""
    resumen = []
    for valor in parametros:
        filas = []
        aristas = []
        for k in range(INSTANCIAS):
            red = fabricar(valor, 1000 * k + (valor % 997))
            aristas.append(red.contarAristas())
            filas.append(comparar_instancia(red, 0, red.size - 1))
        r = dict(parametro=valor, aristas=est.mean(aristas))
        for clave in ("flujo", "t_ff", "t_ek", "c_ff", "c_ek"):
            r[clave], r[clave + "_sd"] = resumir(filas, clave)
        r["aceleracion"] = r["t_ff"] / r["t_ek"] if r["t_ek"] > 0 else float("nan")
        resumen.append(r)
        print(f"{etiqueta}={valor:>7} | aristas={r['aristas']:>7.1f} | flujo={r['flujo']:>9.1f} | "
              f"caminos FF={r['c_ff']:>8.1f} EK={r['c_ek']:>6.1f} | "
              f"t FF={r['t_ff']:.4f}s EK={r['t_ek']:.4f}s | FF/EK={r['aceleracion']:.2f}x", flush=True)
    return resumen


def experimento_peor_caso():
    resumen = []
    for c in CAPACIDADES_PEOR_CASO:
        red = generar_red_peor_caso(c)
        g_adv, g_dfs, g_ek = red.copiar(), red.copiar(), red.copiar()
        f_adv, t_adv, c_adv = medir(g_adv, "fordFulkerson", 0, 3, estrategia="cuello_minimo")
        f_dfs, t_dfs, c_dfs = medir(g_dfs, "fordFulkerson", 0, 3, estrategia="dfs")
        f_ek, t_ek, c_ek = medir(g_ek, "edmonds_karp", 0, 3)
        assert f_adv == f_dfs == f_ek == 2 * c
        resumen.append(dict(capacidad=c, flujo=f_ek, c_adv=c_adv, t_adv=t_adv,
                            c_dfs=c_dfs, t_dfs=t_dfs, c_ek=c_ek, t_ek=t_ek))
        print(f"C={c:>7} | flujo={f_ek:>7} | FF peor caso: {c_adv:>7} caminos, {t_adv:.4f}s | "
              f"FF con DFS: {c_dfs} caminos | EK: {c_ek} caminos, {t_ek:.6f}s", flush=True)
    return resumen


def guardar_csv(nombre, filas):
    with open(os.path.join(CARPETA, nombre), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)


def graficar(exp1, exp2, exp3):
    plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": 0.3})
    azul, naranja = "#1f5fa8", "#d9822b"

    # Figura 1: tamaño de la red
    x = [r["parametro"] for r in exp1]
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    for r_clave, color, nombre in (("t_ff", azul, "Ford-Fulkerson (DFS)"), ("t_ek", naranja, "Edmonds-Karp")):
        ax[0].errorbar(x, [r[r_clave] for r in exp1], yerr=[r[r_clave + "_sd"] for r in exp1],
                       marker="o", capsize=3, color=color, label=nombre)
    ax[0].set(xlabel="Número de nodos", ylabel="Tiempo promedio (s)", title="Tiempo de ejecución")
    ax[0].legend()
    for r_clave, color, nombre in (("c_ff", azul, "Ford-Fulkerson (DFS)"), ("c_ek", naranja, "Edmonds-Karp")):
        ax[1].errorbar(x, [r[r_clave] for r in exp1], yerr=[r[r_clave + "_sd"] for r in exp1],
                       marker="o", capsize=3, color=color, label=nombre)
    ax[1].set(xlabel="Número de nodos", ylabel="Caminos de aumento (promedio)", title="Caminos de aumento")
    ax[1].legend()
    fig.tight_layout()
    fig.savefig(os.path.join(CARPETA, "fig1_tamano_red.png"), dpi=200)
    plt.close(fig)

    # Figura 2: magnitud de las capacidades (redes aleatorias)
    x = [r["parametro"] for r in exp2]
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    for r_clave, color, nombre in (("t_ff", azul, "Ford-Fulkerson (DFS)"), ("t_ek", naranja, "Edmonds-Karp")):
        ax[0].errorbar(x, [r[r_clave] for r in exp2], yerr=[r[r_clave + "_sd"] for r in exp2],
                       marker="o", capsize=3, color=color, label=nombre)
    ax[0].set(xscale="log", xlabel="Capacidad máxima por arista", ylabel="Tiempo promedio (s)",
              title=f"Tiempo ({VERTICES_EXP2} nodos)")
    ax[0].legend()
    for r_clave, color, nombre in (("c_ff", azul, "Ford-Fulkerson (DFS)"), ("c_ek", naranja, "Edmonds-Karp")):
        ax[1].errorbar(x, [r[r_clave] for r in exp2], yerr=[r[r_clave + "_sd"] for r in exp2],
                       marker="o", capsize=3, color=color, label=nombre)
    ax[1].set(xscale="log", xlabel="Capacidad máxima por arista", ylabel="Caminos de aumento (promedio)",
              title=f"Caminos de aumento ({VERTICES_EXP2} nodos)")
    ax[1].legend()
    fig.tight_layout()
    fig.savefig(os.path.join(CARPETA, "fig2_capacidades.png"), dpi=200)
    plt.close(fig)

    # Figura 3: peor caso (4 nodos)
    x = [r["capacidad"] for r in exp3]
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].plot(x, [r["c_adv"] for r in exp3], marker="o", color=azul, label="Ford-Fulkerson (peor caso)")
    ax[0].plot(x, [r["c_dfs"] for r in exp3], marker="s", color="#4c9a2a", label="Ford-Fulkerson (DFS)")
    ax[0].plot(x, [r["c_ek"] for r in exp3], marker="^", color=naranja, label="Edmonds-Karp")
    ax[0].set(xscale="log", yscale="log", xlabel="Capacidad C", ylabel="Caminos de aumento",
              title="Caminos de aumento (red de 4 nodos)")
    ax[0].legend()
    ax[1].plot(x, [r["t_adv"] for r in exp3], marker="o", color=azul, label="Ford-Fulkerson (peor caso)")
    ax[1].plot(x, [r["t_ek"] for r in exp3], marker="^", color=naranja, label="Edmonds-Karp")
    ax[1].set(xscale="log", yscale="log", xlabel="Capacidad C", ylabel="Tiempo (s)",
              title="Tiempo de ejecución (red de 4 nodos)")
    ax[1].legend()
    fig.tight_layout()
    fig.savefig(os.path.join(CARPETA, "fig3_peor_caso.png"), dpi=200)
    plt.close(fig)


def main():
    os.makedirs(CARPETA, exist_ok=True)
    print(f"Python {sys.version.split()[0]}\n")

    print("== Experimento 1: tamaño de la red (capacidades 1..%d, %d instancias) ==" % (CAPACIDAD_MAX_EXP1, INSTANCIAS))
    exp1 = experimento_aleatorio(
        TAMANOS, lambda v, s: generar_red_aleatoria(v, CAPACIDAD_MAX_EXP1, s), "nodos")

    print("\n== Experimento 2: magnitud de capacidades (%d nodos, %d instancias) ==" % (VERTICES_EXP2, INSTANCIAS))
    exp2 = experimento_aleatorio(
        CAPACIDADES_EXP2, lambda c, s: generar_red_aleatoria(VERTICES_EXP2, c, s), "cap_max")

    print("\n== Experimento 3: red de 4 nodos (peor caso de Ford-Fulkerson) ==")
    exp3 = experimento_peor_caso()

    guardar_csv("exp1_tamano_red.csv", exp1)
    guardar_csv("exp2_capacidades.csv", exp2)
    guardar_csv("exp3_peor_caso.csv", exp3)
    graficar(exp1, exp2, exp3)
    print(f"\nListo. CSV y graficos guardados en ./{CARPETA}")


if __name__ == "__main__":
    main()
