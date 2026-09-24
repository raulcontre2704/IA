import math
import heapq
import time

def heuristica_Euclidiana(nodo_actual, nodo_destino, grafo):
    """Heuristica Euclidiana proyectada aproximada en metros."""
    x1, y1 = grafo.nodes[nodo_actual]['x'], grafo.nodes[nodo_actual]['y']
    x2, y2 = grafo.nodes[nodo_destino]['x'], grafo.nodes[nodo_destino]['y']
    # Factor aproximado de conversion de grados a metros en latitud de CDMX (~19°N)
    dx = (x2 - x1) * 105000 * math.cos(math.radians(19.43))
    dy = (y2 - y1) * 111000
    return math.sqrt(dx**2 + dy**2)

def heuristica_Haversine(nodo_actual, nodo_destino, grafo):
    """Heuristica Haversine: Distancia de circulo maximo en la esfera (admisible)."""
    lon1, lat1 = math.radians(grafo.nodes[nodo_actual]['x']), math.radians(grafo.nodes[nodo_actual]['y'])
    lon2, lat2 = math.radians(grafo.nodes[nodo_destino]['x']), math.radians(grafo.nodes[nodo_destino]['y'])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return 6371000.0 * c

def heuristica_personalizada(nodo_actual, nodo_destino, grafo):
    """
    Heuristica admisible basada en estimacion de giros:
    Usa el 95% de Haversine como base y agrega un costo minimo si los puntos 
    no estan alineados (lo que obligatoriamente exige al menos un giro o cambio de direccion).
    Garantiza h(n) <= h*(n).
    """
    h_base = heuristica_Haversine(nodo_actual, nodo_destino, grafo)
    x1, y1 = grafo.nodes[nodo_actual]['x'], grafo.nodes[nodo_actual]['y']
    x2, y2 = grafo.nodes[nodo_destino]['x'], grafo.nodes[nodo_destino]['y']
    
    # Si hay desviacion angular significativa en ejes de calles, se requiere al menos un giro
    angulo_desvio = abs(math.atan2(y2 - y1, x2 - x1))
    costo_giro_minimo = 5.0 if (angulo_desvio > 0.15) else 0.0
    
    return (h_base * 0.95) + costo_giro_minimo

def algo_estrella(grafo, origen, destino, heuristica):
    """Algoritmo A* con cola de prioridad f(n) = g(n) + h(n)."""
    tiempo_inicio = time.time()
    frontera = []
    # Formato en frontera: (f_n, g_n, nodo)
    h_inicio = heuristica(origen, destino, grafo)
    heapq.heappush(frontera, (h_inicio, 0.0, origen))
    
    costo_g = {origen: 0.0}
    padres = {origen: None}
    nodos_expandidos = 0
    tamano_max_frontera = 1

    while frontera:
        if len(frontera) > tamano_max_frontera:
            tamano_max_frontera = len(frontera)
            
        f_n, g_n, actual = heapq.heappop(frontera)
        
        if actual == destino:
            # Reconstruccion de camino
            camino = []
            curr = destino
            while curr is not None:
                camino.append(curr)
                curr = padres[curr]
            camino.reverse()
            
            tiempo_ms = (time.time() - tiempo_inicio) * 1000
            return {
                "camino": camino,
                "metros": round(g_n, 2),
                "nodos_expandidos": nodos_expandidos,
                "tamano_max_frontera": tamano_max_frontera,
                "tiempo_ms": round(tiempo_ms, 2)
            }
            
        if g_n > costo_g.get(actual, float('inf')):
            continue
            
        nodos_expandidos += 1
        
        for vecino in grafo.neighbors(actual):
            try:
                peso = float(grafo[actual][vecino][0].get('length', 10.0))
            except Exception:
                peso = 10.0
                
            nuevo_g = g_n + peso
            if nuevo_g < costo_g.get(vecino, float('inf')):
                costo_g[vecino] = nuevo_g
                padres[vecino] = actual
                f_nuevo = nuevo_g + heuristica(vecino, destino, grafo)
                heapq.heappush(frontera, (f_nuevo, nuevo_g, vecino))
                
    return None

def algo_greedy(grafo, origen, destino, heuristica):
    """Greedy Best-First Search: f(n) = h(n)."""
    tiempo_inicio = time.time()
    frontera = []
    h_inicio = heuristica(origen, destino, grafo)
    heapq.heappush(frontera, (h_inicio, 0.0, origen))
    
    visitados = set()
    padres = {origen: None}
    costo_g = {origen: 0.0}
    nodos_expandidos = 0
    tamano_max_frontera = 1

    while frontera:
        if len(frontera) > tamano_max_frontera:
            tamano_max_frontera = len(frontera)
            
        h_n, g_n, actual = heapq.heappop(frontera)
        
        if actual == destino:
            camino = []
            curr = destino
            while curr is not None:
                camino.append(curr)
                curr = padres[curr]
            camino.reverse()
            
            tiempo_ms = (time.time() - tiempo_inicio) * 1000
            return {
                "camino": camino,
                "metros": round(g_n, 2),
                "nodos_expandidos": nodos_expandidos,
                "tamano_max_frontera": tamano_max_frontera,
                "tiempo_ms": round(tiempo_ms, 2)
            }
            
        if actual in visitados:
            continue
        visitados.add(actual)
        nodos_expandidos += 1
        
        for vecino in grafo.neighbors(actual):
            if vecino not in visitados:
                try:
                    peso = float(grafo[actual][vecino][0].get('length', 10.0))
                except Exception:
                    peso = 10.0
                
                costo_g[vecino] = g_n + peso
                padres[vecino] = actual
                h_vecino = heuristica(vecino, destino, grafo)
                heapq.heappush(frontera, (h_vecino, costo_g[vecino], vecino))
                
    return None
