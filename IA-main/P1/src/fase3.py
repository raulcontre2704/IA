import random
import math
import copy

def calcular_matriz_distancias(grafo, nodos_visita, algoritmo_busqueda, heuristica):
    """
    Precomputa la matriz de distancias NxN usando A* entre todos los puntos seleccionados.
    """
    matriz = {}
    for origen in nodos_visita:
        matriz[origen] = {}
        for destino in nodos_visita:
            if origen == destino:
                matriz[origen][destino] = 0.0
            else:
                res = algoritmo_busqueda(grafo, origen, destino, heuristica)
                matriz[origen][destino] = res['metros'] if res else float('inf')
    return matriz

def costo_ruta(ruta, matriz_distancias):
    """Calcula la distancia total de una permutacion de nodos (ciclo cerrado)."""
    costo = 0.0
    for i in range(len(ruta)):
        u = ruta[i]
        v = ruta[(i + 1) % len(ruta)]
        costo += matriz_distancias[u][v]
    return costo

def operador_2opt(ruta):
    """Aplica una mutacion/movimiento de vecindad 2-opt invirtiendo un subsegmento."""
    n = len(ruta)
    if n <= 3:
        return ruta[:]
    i = random.randint(0, n - 2)
    j = random.randint(i + 1, n - 1)
    
    nueva_ruta = ruta[:i] + ruta[i:j+1][::-1] + ruta[j+1:]
    return nueva_ruta

def simulated_annealing(nodos, matriz_distancias, t_inicial=1000.0, alpha=0.95, t_min=1e-3, max_iter=1000):
    """
    Simulated Annealing con enfriamiento geometrico T = alpha * T.
    """
    ruta_actual = nodos[:]
    random.shuffle(ruta_actual)
    costo_actual = costo_ruta(ruta_actual, matriz_distancias)
    
    mejor_ruta = ruta_actual[:]
    mejor_costo = costo_actual
    
    historial_costos = [mejor_costo]
    t = t_inicial
    
    for _ in range(max_iter):
        if t <= t_min:
            break
            
        candidata = operador_2opt(ruta_actual)
        costo_cand = costo_ruta(candidata, matriz_distancias)
        delta = costo_cand - costo_actual
        
        # Criterio de Metropolis
        if delta < 0 or random.random() < math.exp(-delta / t):
            ruta_actual = candidata
            costo_actual = costo_cand
            if costo_actual < mejor_costo:
                mejor_costo = costo_actual
                mejor_ruta = ruta_actual[:]
                
        t *= alpha
        historial_costos.append(mejor_costo)
        
    return mejor_ruta, mejor_costo, historial_costos

def cruza_ox(padre1, padre2):
    """Operador Order Crossover (OX) para permutaciones."""
    n = len(padre1)
    i, j = sorted(random.sample(range(n), 2))
    
    hijo = [None] * n
    hijo[i:j+1] = padre1[i:j+1]
    
    pos = (j + 1) % n
    for gen in padre2[j+1:] + padre2[:j+1]:
        if gen not in hijo:
            hijo[pos] = gen
            pos = (pos + 1) % n
            
    return hijo

def algoritmo_genetico(nodos, matriz_distancias, tam_poblacion=50, generaciones=200, prob_mutacion=0.2):
    """
    Algoritmo Genetico para TSP con representacion de permutacion y cruza OX.
    """
    poblacion = [random.sample(nodos, len(nodos)) for _ in range(tam_poblacion)]
    mejor_global = min(poblacion, key=lambda r: costo_ruta(r, matriz_distancias))
    mejor_costo = costo_ruta(mejor_global, matriz_distancias)
    historial = [mejor_costo]
    
    for _ in range(generaciones):
        # Seleccion por torneo
        nueva_poblacion = []
        for _ in range(tam_poblacion // 2):
            t1, t2 = random.sample(poblacion, 2)
            padre1 = t1 if costo_ruta(t1, matriz_distancias) < costo_ruta(t2, matriz_distancias) else t2
            
            t3, t4 = random.sample(poblacion, 2)
            padre2 = t3 if costo_ruta(t3, matriz_distancias) < costo_ruta(t4, matriz_distancias) else t4
            
            # Cruza OX
            h1 = cruza_ox(padre1, padre2)
            h2 = cruza_ox(padre2, padre1)
            
            # Mutacion por intercambio o 2-opt
            if random.random() < prob_mutacion:
                h1 = operador_2opt(h1)
            if random.random() < prob_mutacion:
                h2 = operador_2opt(h2)
                
            nueva_poblacion.extend([h1, h2])
            
        poblacion = nueva_poblacion
        actual_mejor = min(poblacion, key=lambda r: costo_ruta(r, matriz_distancias))
        actual_costo = costo_ruta(actual_mejor, matriz_distancias)
        
        if actual_costo < mejor_costo:
            mejor_costo = actual_costo
            mejor_global = actual_mejor[:]
            
        historial.append(mejor_costo)
        
    return mejor_global, mejor_costo, historial
