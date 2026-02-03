from pathlib import Path
from worldpoppy import WorldPopDownloader, wp_manifest

#Set your durectory - local, NOT DROPBOX
DATA_DIR = Path(r"E:\Projects\Updated_WP")
#DATA_DIR = Path("UPDATED_WP")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def pull_data(iso3_codes=None):
    product_name = "pop_g1_unadj"

    if iso3_codes is None:
        manifest = wp_manifest(product_name=product_name)
        iso3_codes = manifest['iso3'].unique().tolist()

    downloader = WorldPopDownloader(directory=DATA_DIR)

    YEAR = 2025

    downloaded_files  = downloader.download(
        product_name=product_name,
        iso3_codes=iso3_codes,
        years=YEAR
    )

def rename_data():
    path_list = DATA_DIR.glob("*.tif")
    for path in path_list:
        iso = path.name[13:16].lower()
        new_name = iso + "_ppp_2020_UNadj.tif"
        new_path=DATA_DIR.joinpath(new_name)
        path.rename(new_path)


pull_data(["JAM", "AUT", "TUV", "LUX"]) #<- For pulling sample data
#pull_data() #<- Leave Parameters empty for pulling all data
rename_data()