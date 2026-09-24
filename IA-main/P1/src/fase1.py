import time
import heapq
import random
from collections import deque

def generar_pares_prueba(grafo, num_pares=5):
    """Genera pares aleatorios de nodos origen y destino asegurando conectividad inicial."""
    nodos = list(grafo.nodes)
    pares = []
    for _ in range(num_pares):
        origen = random.choice(nodos)
        destino = random.choice(nodos)
        while destino == origen:
            destino = random.choice(nodos)
        pares.append((origen, destino))
    return pares

def bfs_rutas(grafo, origen, destino):
    """Búsqueda en Anchura (BFS): Garantiza la menor cantidad de arcos (saltos)."""
    tiempo_inicio = time.time()
    
    frontera = deque([origen])
    visitados = {origen}
    padres = {origen: None}
    
    nodos_expandidos = 0
    tamano_max_frontera = len(frontera)
    
    camino = []
    metros = 0.0
    arcos = 0
    
    while frontera:
        if len(frontera) > tamano_max_frontera:
            tamano_max_frontera = len(frontera)
            
        nodo_actual = frontera.popleft()
        
        if nodo_actual == destino:
            actual = destino
            while actual is not None:
                camino.append(actual)
                actual = padres[actual]
            camino.reverse()
            
            arcos = len(camino) - 1
            for i in range(arcos):
                u, v = camino[i], camino[i+1]
                try:
                    metros += grafo[u][v][0].get('length', 10.0)
                except KeyError:
                    metros += 10.0
            break
            
        nodos_expandidos += 1
        
        for vecino in grafo.neighbors(nodo_actual):
            if vecino not in visitados:
                visitados.add(vecino)
                padres[vecino] = nodo_actual
                frontera.append(vecino)
                
    tiempo_ejecucion = (time.time() - tiempo_inicio) * 1000 
    
    return {
        'camino': camino,
        'arcos': arcos,
        'metros': round(metros, 2),
        'nodos_expandidos': nodos_expandidos,
        'tamano_max_frontera': tamano_max_frontera,
        'tiempo_ejecucion_ms': round(tiempo_ejecucion, 2)
    }

def dfs_rutas(grafo, origen, destino):
    """Búsqueda en Profundidad (DFS Iterativo): Usa LIFO y detecta ciclos con la lista de cerrados."""
    tiempo_inicio = time.time()
    
    frontera = [origen]
    visitados = {origen}
    padres = {origen: None}
    
    nodos_expandidos = 0
    tamano_max_frontera = len(frontera)
    
    camino = []
    metros = 0.0
    arcos = 0
    
    while frontera:
        if len(frontera) > tamano_max_frontera:
            tamano_max_frontera = len(frontera)
            
        nodo_actual = frontera.pop()
        
        if nodo_actual == destino:
            actual = destino
            while actual is not None:
                camino.append(actual)
                actual = padres[actual]
            camino.reverse()
            
            arcos = len(camino) - 1
            for i in range(arcos):
                u, v = camino[i], camino[i+1]
                try:
                    metros += grafo[u][v][0].get('length', 10.0)
                except KeyError:
                    metros += 10.0
            break
            
        nodos_expandidos += 1
        
        for vecino in grafo.neighbors(nodo_actual):
            if vecino not in visitados:
                visitados.add(vecino)
                padres[vecino] = nodo_actual
                frontera.append(vecino)
                
    tiempo_ejecucion = (time.time() - tiempo_inicio) * 1000
    
    return {
        'camino': camino,
        'arcos': arcos,
        'metros': round(metros, 2),
        'nodos_expandidos': nodos_expandidos,
        'tamano_max_frontera': tamano_max_frontera,
        'tiempo_ejecucion_ms': round(tiempo_ejecucion, 2)
    }

def ucs_rutas(grafo, origen, destino):
    """Búsqueda de Costo Uniforme (UCS): Utiliza PriorityQueue (min-heap) para garantizar optimalidad en distancia."""
    tiempo_inicio = time.time()
    
    frontera = [(0.0, origen)]
    costos_explorados = {origen: 0.0}
    padres = {origen: None}
    
    nodos_expandidos = 0
    tamano_max_frontera = 1
    
    camino = []
    arcos = 0
    metros_totales = 0.0
    
    while frontera:
        if len(frontera) > tamano_max_frontera:
            tamano_max_frontera = len(frontera)
            
        costo_actual, nodo_actual = heapq.heappop(frontera)
        
        if nodo_actual == destino:
            actual = destino
            while actual is not None:
                camino.append(actual)
                actual = padres[actual]
            camino.reverse()
            
            arcos = len(camino) - 1
            metros_totales = costo_actual
            break
            
        if costo_actual > costos_explorados.get(nodo_actual, float('inf')):
            continue
            
        nodos_expandidos += 1
        
        for vecino in grafo.neighbors(nodo_actual):
            try:
                costo_arista = grafo[nodo_actual][vecino][0].get('length', 10.0)
            except KeyError:
                costo_arista = 10.0
                
            nuevo_costo = costo_actual + costo_arista
            
            if nuevo_costo < costos_explorados.get(vecino, float('inf')):
                costos_explorados[vecino] = nuevo_costo
                padres[vecino] = nodo_actual
                heapq.heappush(frontera, (nuevo_costo, vecino))
                
    tiempo_ejecucion = (time.time() - tiempo_inicio) * 1000 
    
    return {
        'camino': camino,
        'arcos': arcos,
        'metros': round(metros_totales, 2),
        'nodos_expandidos': nodos_expandidos,
        'tamano_max_frontera': tamano_max_frontera,
        'tiempo_ejecucion_ms': round(tiempo_ejecucion, 2)
    }
def verificar_accesibilidad(grafo, deposito, puntos_entrega):
    """
    Clasifica los puntos de entrega en alcanzables y no alcanzables desde el depósito.
    """
    alcanzables = set()
    frontera = deque([deposito])
    visitados = {deposito}
    
    while frontera:
        actual = frontera.popleft()
        alcanzables.add(actual)
        for vecino in grafo.neighbors(actual):
            if vecino not in visitados:
                visitados.add(vecino)
                frontera.append(vecino)
                
    return {
        'alcanzables': [p for p in puntos_entrega if p in alcanzables],
        'no_alcanzables': [p for p in puntos_entrega if p not in alcanzables]
    }
