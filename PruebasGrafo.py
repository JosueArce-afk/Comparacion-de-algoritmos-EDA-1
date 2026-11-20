"""
Pruebas simples de correccion. Ejecutar:  python PruebasGrafo.py
"""
import unittest
from Grafo import Grafo
from Redes import generar_red_aleatoria, generar_red_peor_caso


def red_cormen():
    """Red clasica de Cormen et al. (2009), Fig. 26.1. Flujo maximo = 23."""
    g = Grafo(6)  # 0=s, 1=v1, 2=v2, 3=v3, 4=v4, 5=t
    for u, v, c in [(0, 1, 16), (0, 2, 13), (1, 3, 12), (2, 1, 4), (2, 4, 14),
                    (3, 2, 9), (3, 5, 20), (4, 3, 7), (4, 5, 4)]:
        g.agregar_arista(u, v, c)
    return g


class PruebasFlujoMaximo(unittest.TestCase):

    def test_red_de_cormen(self):
        self.assertEqual(red_cormen().fordFulkerson(0, 5), 23)
        self.assertEqual(red_cormen().edmonds_karp(0, 5), 23)

    def test_sin_camino(self):
        g = Grafo(3)
        g.agregar_arista(0, 1, 5)          # el nodo 2 no esta conectado
        self.assertEqual(g.fordFulkerson(0, 2), 0)
        self.assertEqual(g.caminosAumento, 0)
        h = Grafo(3)
        h.agregar_arista(0, 1, 5)
        self.assertEqual(h.edmonds_karp(0, 2), 0)

    def test_camino_unico_cuello_de_botella(self):
        g = Grafo(3)
        g.agregar_arista(0, 1, 7)
        g.agregar_arista(1, 2, 3)
        self.assertEqual(g.copiar().fordFulkerson(0, 2), 3)
        self.assertEqual(g.copiar().edmonds_karp(0, 2), 3)

    def test_copiar_no_modifica_el_original(self):
        g = red_cormen()
        antes = [fila[:] for fila in g.matrizCapacidades]
        g.copiar().edmonds_karp(0, 5)
        self.assertEqual(g.matrizCapacidades, antes)

    def test_ambos_algoritmos_coinciden_y_cumplen_corte_minimo(self):
        for semilla in range(30):
            original = generar_red_aleatoria(40, 50, semilla)
            gf, ge = original.copiar(), original.copiar()
            ff = gf.fordFulkerson(0, 39)
            ek = ge.edmonds_karp(0, 39)
            self.assertEqual(ff, ek)
            self.assertEqual(ff, gf.capacidadCorteMinimo(original, 0))
            self.assertEqual(ek, ge.capacidadCorteMinimo(original, 0))

    def test_peor_caso(self):
        c = 50
        g = generar_red_peor_caso(c)
        self.assertEqual(g.copiar().fordFulkerson(0, 3, estrategia="cuello_minimo"), 2 * c)
        peor = g.copiar()
        peor.fordFulkerson(0, 3, estrategia="cuello_minimo")
        self.assertEqual(peor.caminosAumento, 2 * c)     # 2C caminos
        bueno = g.copiar()
        self.assertEqual(bueno.edmonds_karp(0, 3), 2 * c)
        self.assertEqual(bueno.caminosAumento, 2)        # solo 2 caminos

    def test_estrategia_invalida(self):
        with self.assertRaises(ValueError):
            red_cormen().fordFulkerson(0, 5, estrategia="otra")

    def test_misma_semilla_misma_red(self):
        a = generar_red_aleatoria(30, 50, 7)
        b = generar_red_aleatoria(30, 50, 7)
        self.assertEqual(a.matrizCapacidades, b.matrizCapacidades)


if __name__ == "__main__":
    unittest.main(verbosity=2)
