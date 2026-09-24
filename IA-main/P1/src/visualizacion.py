import folium
from folium import plugins


def generar_mapa_comparativo(G, res_a_star, res_greedy, archivo_salida="mapa.html"):
    """
    Genera un mapa Folium interactivo con capas independientes para A* y Greedy,
    permitiendo activar o desactivar cada ruta con un control de capas.
    """
    camino_a = res_a_star['camino']
    camino_g = res_greedy['camino']

    coords_a = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in camino_a]
    coords_g = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in camino_g]

    # Centrar en el origen
    mapa = folium.Map(location=coords_a[0], zoom_start=14, tiles="cartodbpositron")

    # Grupo de marcadores comunes (Origen y Destino)
    grupo_marcadores = folium.FeatureGroup(name="Puntos Clave", show=True)
    folium.Marker(
        coords_a[0],
        popup=f"<b>Depósito / Origen</b><br>Nodo: {camino_a[0]}",
        icon=folium.Icon(color="green", icon="home", prefix="fa")
    ).add_to(grupo_marcadores)

    folium.Marker(
        coords_a[-1],
        popup=f"<b>Destino de Entrega</b><br>Nodo: {camino_a[-1]}",
        icon=folium.Icon(color="red", icon="flag", prefix="fa")
    ).add_to(grupo_marcadores)
    grupo_marcadores.add_to(mapa)

    # Capa para A* (Ruta óptima en azul)
    grupo_a = folium.FeatureGroup(
        name=f"Ruta A* ({res_a_star['metros']:,.0f} m, {res_a_star['nodos_expandidos']} nodos exp.)",
        show=True
    )
    folium.PolyLine(
        coords_a,
        color="#0066FF",
        weight=6,
        opacity=0.85,
        tooltip="Ruta A* (Óptima)"
    ).add_to(grupo_a)
    grupo_a.add_to(mapa)

    # Capa para Greedy (Ruta subóptima en rojo discontinua)
    grupo_g = folium.FeatureGroup(
        name=f"Ruta Greedy ({res_greedy['metros']:,.0f} m, {res_greedy['nodos_expandidos']} nodos exp.)",
        show=True
    )
    folium.PolyLine(
        coords_g,
        color="#FF3300",
        weight=4,
        opacity=0.85,
        dash_array="6, 8",
        tooltip="Ruta Greedy (Voraz)"
    ).add_to(grupo_g)
    grupo_g.add_to(mapa)

    # Añadir control para prender/apagar capas
    folium.LayerControl(collapsed=False).add_to(mapa)

    mapa.save(archivo_salida)
    print(f"Mapa comparativo generado en: {archivo_salida}")
    return mapa


def generar_snapshots_frontera(G, lista_fronteras_pasos, archivo_salida="mapa_frontera.html"):
    """
    Visualiza la evolución de la frontera de exploración (mínimo 3 snapshots)
    utilizando círculos con diferentes colores por cada paso temporal.
    """
    if not lista_fronteras_pasos:
        return None

    # Tomar la ubicación del primer nodo del primer paso
    primer_nodo = list(lista_fronteras_pasos[0]['nodos'])[0]
    mapa = folium.Map(
        location=[G.nodes[primer_nodo]['y'], G.nodes[primer_nodo]['x']],
        zoom_start=13,
        tiles="cartodbpositron"
    )

    colores = ["#FFAA00", "#FF5500", "#AA00FF", "#00AAFF"]

    for i, paso in enumerate(lista_fronteras_pasos):
        color_paso = colores[i % len(colores)]
        grupo_paso = folium.FeatureGroup(
            name=f"Frontera en Paso {paso['paso']} ({len(paso['nodos'])} nodos)",
            show=True
        )

        for nodo in paso['nodos']:
            lat, lon = G.nodes[nodo]['y'], G.nodes[nodo]['x']
            folium.CircleMarker(
                location=[lat, lon],
                radius=4,
                color=color_paso,
                fill=True,
                fill_color=color_paso,
                fill_opacity=0.6,
                popup=f"Paso {paso['paso']} - Nodo {nodo}"
            ).add_to(grupo_paso)

        grupo_paso.add_to(mapa)

    folium.LayerControl(collapsed=False).add_to(mapa)
    mapa.save(archivo_salida)
    print(f"Mapa de snapshots de frontera generado en: {archivo_salida}")
    return mapa