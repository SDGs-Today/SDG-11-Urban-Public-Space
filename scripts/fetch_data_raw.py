import geopandas as gpd
import requests
import time
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from shapely.geometry import mapping
#import zipfile

settlements = gpd.read_file("GHS_UCDB_GLOBE_R2024A.gpkg", layer="GHS_UCDB_THEME_GENERAL_CHARACTERISTICS_GLOBE_R2024A")
settlements = settlements.to_crs(4326)

API_BASE = "https://api-prod.raw-data.hotosm.org/v1"
OUTPUT_DIR = Path("osm_output")
OUTPUT_DIR.mkdir(exist_ok=True)

HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json"
}

MAX_WORKERS = 12
POLL_INTERVAL = 10

def request_export(polygon_geojson, settlement_id):
    payload = {
        "outputType": "geojson",
        "fileName": f"settlement_{settlement_id}",
        "geometry": polygon_geojson,
        "geometryType": ["line", "polygon"],
        "filters": {
            "tags": {
                "line": {
                    "Roads" : ['motorway','trunk','primary','secondary','tertiary',
                                'unclassified','residential','motorway_link','trunk_link','primary_link',
                                'secondary_link','tertiary_link','living_street','pedestrian','road',
                                'busway','sidewalk','cycleway','footway','track',
                                'bridleway','path']
                },
                "polygon": {
                    "leisure": ['park', 'nature_reserve', 'playground', 'common', 'garden', 'allotments', 'recreation_ground',
                                'pitch', 'dog_park', 'fitness_station'],
                    "natural": ['fell', 'grassland', 'heath', 'scrub', 'wood'],
                    "landuse": ['forest', 'village_green', 'recreation_ground', 'allotments', 'conservation']
                }
            }
        },
        "joinFilterType": "OR"
    }

    r = requests.post(f"{API_BASE}/snapshot/", data=json.dumps(payload), headers=HEADERS)

    if not r.ok:
        raise RuntimeError(f"Submit failed {r.status_code}: {r.text}")

    return r.json()["track_link"]


def poll_and_download(idx, track_link, timeout=600):
    out_file = OUTPUT_DIR / f"settlement_{idx}.geojson.zip"
    url = f"{API_BASE}{track_link}"
    start = time.time()

    while time.time() - start < timeout:
        r = requests.get(url, headers=HEADERS)
        data = r.json()
        status = data.get("status")

        if status == "SUCCESS":
            download_url = data["result"]["download_url"]
            content = requests.get(download_url).content
            out_file.write_bytes(content)
            return idx, True, None
        elif status == "FAILED":
            return idx, False, f"Job failed: {data}"

        time.sleep(POLL_INTERVAL)

    return idx, False, "Timed out"


def process_settlement(idx, row):
    out_file = OUTPUT_DIR / f"settlement_{idx}.geojson.zip"
    if out_file.exists():
        return idx, True, "already done"

    geom = row.geometry.__geo_interface__
    if geom["type"] == "MultiPolygon":
        geom = mapping(row.geometry.convex_hull)

    try:
        track_link = request_export(geom, idx)
        return poll_and_download(idx, track_link)
    except Exception as e:
        return idx, False, str(e)


total = len(settlements)
done = 0
failed = []

print(f"Processing {total} settlements with {MAX_WORKERS} parallel workers...\n")
start_all = time.time()

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {
        executor.submit(process_settlement, idx, row): idx
        for idx, row in settlements.iterrows()
    }

    for future in as_completed(futures):
        idx, success, msg = future.result()
        done += 1
        elapsed = time.time() - start_all
        rate = elapsed / done
        eta_hours = (rate * (total - done)) / 3600

        if success:
            if msg != "already done":
                print(f"[{idx}] s, {done}/{total} done, ETA: {eta_hours:.1f}h")
        else:
            failed.append(idx)
            print(f"[{idx}] f, {msg}, {done}/{total} done")

print(f"\nFinished. {total - len(failed)} succeeded, {len(failed)} failed.")

if failed:
    print(f"Failed indices: {failed}")