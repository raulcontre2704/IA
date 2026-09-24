import os
import sys
import networkx as nx
import pytest

# 1. Configurar ruta absoluta para importar desde src/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PATH = os.path.join(BASE_DIR, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from fase1 import bfs_rutas, dfs_rutas, ucs_rutas, verificar_accesibilidad
from fase2 import algo_estrella, algo_greedy, heuristica_Haversine, heuristica_Euclidiana
from fase3 import operador_2opt, cruza_ox, costo_ruta


@pytest.fixture
def grafo_prueba():
    """
    Grafo MultiDiGraph similar al descargado por osmnx,
    el cual requiere la key 0 para acceder a los atributos de las aristas.
    """
    G = nx.MultiDiGraph()
    
    # Nodos con coordenadas ficticias
    G.add_node(1, x=-99.1332, y=19.4326)
    G.add_node(2, x=-99.1350, y=19.4350)
    G.add_node(3, x=-99.1370, y=19.4380)
    G.add_node(4, x=-99.2000, y=19.5000)  # Nodo desconectado

    # Aristas con 'key=0' y peso en 'length'
    G.add_edge(1, 2, key=0, length=100.0)
    G.add_edge(2, 3, key=0, length=150.0)
    G.add_edge(1, 3, key=0, length=600.0)
    return G


# ==========================================
# Pruebas de Fase 1: Búsqueda No Informada
# ==========================================

def test_bfs_prioriza_menor_numero_de_arcos(grafo_prueba):
    res = bfs_rutas(grafo_prueba, 1, 3)
    assert res['arcos'] == 1
    assert res['camino'] == [1, 3]


def test_ucs_garantiza_menor_distancia_en_metros(grafo_prueba):
    res = ucs_rutas(grafo_prueba, 1, 3)
    assert res['metros'] == 250.0
    assert res['camino'] == [1, 2, 3]


def test_verificar_accesibilidad_detecta_inalcanzables(grafo_prueba):
    clasificacion = verificar_accesibilidad(grafo_prueba, deposito=1, puntos_entrega=[2, 3, 4])
    assert 2 in clasificacion['alcanzables']
    assert 3 in clasificacion['alcanzables']
    assert 4 in clasificacion['no_alcanzables']


# ==========================================
# Pruebas de Fase 2: Búsqueda Informada
# ==========================================

def test_a_estrella_optimalidad_con_haversine(grafo_prueba):
    res = algo_estrella(grafo_prueba, 1, 3, heuristica_Haversine)
    assert res['metros'] == 250.0
    assert res['camino'] == [1, 2, 3]


def test_greedy_encuentra_camino(grafo_prueba):
    res = algo_greedy(grafo_prueba, 1, 3, heuristica_Haversine)
    assert res is not None
    assert res['camino'][0] == 1
    assert res['camino'][-1] == 3


# ==========================================
# Pruebas de Fase 3: Búsqueda Local (TSP)
# ==========================================

def test_operador_2opt_conserva_tamano_y_elementos():
    ruta_original = [1, 2, 3, 4, 5]
    ruta_mutada = operador_2opt(ruta_original)
    assert len(ruta_mutada) == len(ruta_original)
    assert set(ruta_mutada) == set(ruta_original)


def test_cruza_ox_genera_permutacion_valida():
    p1 = [1, 2, 3, 4, 5]
    p2 = [5, 4, 3, 2, 1]
    hijo = cruza_ox(p1, p2)
    assert len(hijo) == 5
    assert sorted(hijo) == [1, 2, 3, 4, 5]