import geopandas
import osmnx

GHS_data_frame = geopandas.read_file("GHS_UCDB_GLOBE_R2024A.gpkg", layer="GHS_UCDB_THEME_GENERAL_CHARACTERISTICS_GLOBE_R2024A")
GHS_data_frame = GHS_data_frame.to_crs(epsg=4326)

OSM_tags = {
    "leisure": ['park', 'nature_reserve', 'playground', 'common', 'garden', 'allotments', 'recreation_ground',
                'pitch', 'dog_park', 'fitness_station'],

    "landuse" : ['forest', 'village_green', 'recreation_ground', 'allotments', 'conservation'],

    "natural" : ['fell', 'grassland', 'heath', 'scrub', 'wood'],

    #"Roads" : ['motorway','trunk','primary','secondary','tertiary',
    #           'unclassified','residential','motorway_link','trunk_link','primary_link',
    #           'secondary_link','tertiary_link','living_street','pedestrian','road',
    #           'busway','sidewalk','cycleway','footway','track',
    #           'bridleway','path']
}

OSM_public_polygons = []

print("Start fetching OSM public polygons...")

for settlement in range(len(GHS_data_frame)):
    current_settlement = GHS_data_frame.iloc[settlement]
    GHS_polygon = current_settlement["geometry"]

    print("[" + str(settlement) + "]" + " Processing: " + str(current_settlement["\ufeffGC_UCN_MAI_2025"]))
    try:
        OSM_data = osmnx.features_from_polygon(GHS_polygon, OSM_tags)

        OSM_polygon = OSM_data[OSM_data.geometry.type.isin(["Polygon", "MultiPolygon"])]

        if "access" in OSM_polygon.columns:
            OSM_polygon = OSM_polygon[~OSM_polygon["access"].isin(["no", "private"])]

        OSM_public_polygons.append(OSM_polygon)

    except Exception as e:
        print(f"Skipping due to error: {e}")
        continue

print("Start exporting geometries as geojson...")

public_spaces = geopandas.pd.concat(OSM_public_polygons, ignore_index=True)
public_spaces = public_spaces["geometry"]
public_spaces.to_file("public_spaces_test.geojson", driver="GeoJSON")