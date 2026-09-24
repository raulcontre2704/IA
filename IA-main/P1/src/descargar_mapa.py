import osmnx as ox

def descargar_y_guardar_grafo():
    # Habilitar caché para evitar descargar el grafo repetidamente en fase de pruebas
    ox.settings.use_cache = True
    ox.settings.log_console = True

    # Coordenadas céntricas de la CDMX (Zócalo/Bellas Artes)
    punto_central = (19.4326, -99.1332)
    
    # Radio de 4000 metros (4 km) para abarcar el centro y parte de la zona norte
    print("Descargando el grafo de calles desde OpenStreetMap...")
    
    # network_type='drive' asegura descargar solo calles transitables por vehículos para logística
    G = ox.graph_from_point(punto_central, dist=4000, network_type='drive')

    # Guardar el grafo en la carpeta de datos para las siguientes fases
    ruta_archivo = '../data/mapa_cdmx.graphml'
    ox.save_graphml(G, filepath=ruta_archivo)
    print(f"Grafo descargado exitosamente: {len(G.nodes)} nodos (intersecciones).")

if __name__ == "__main__":
    descargar_y_guardar_grafo()