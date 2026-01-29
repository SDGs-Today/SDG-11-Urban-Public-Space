from pathlib import Path
from worldpoppy import WorldPopDownloader, wp_manifest

DATA_DIR = Path("UPDATED_WP")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def pull_data():
    PRODUCT = "pop_g1_unadj"

    manifest = wp_manifest(product_name=PRODUCT)
    iso3_codes = manifest['iso3'].unique().tolist()

    downloader = WorldPopDownloader(directory=DATA_DIR)

    YEAR = 2020

    downloaded_files  = downloader.download(
        product_name=PRODUCT,
        iso3_codes=iso3_codes,
        years=YEAR
    )

def rename_data():
    path_list = DATA_DIR.glob("*.tif")
    for path in path_list:
        iso = path.name[14:16].lower()
        new_name = iso + "_ppp_2020_UNadj.tif"
        new_path=DATA_DIR.joinpath(new_name)
        path.rename(new_path)

pull_data()
rename_data()