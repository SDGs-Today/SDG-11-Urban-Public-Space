#08/22/2024

#SDG Indicator 11.7.1
#Step 4b: Areas- Roads Dissolve

import arcpy, sys, os
from collections import defaultdict
from arcpy import env
from arcpy.sa import *
import time
import datetime
import pandas as pd
import numpy as np
import multiprocessing
arcpy.env.overwriteOutput = True

GADMGlobal = r'D:\Projects\SDG Indicators\SDG11\data\GADM\gadm_410-gdb\gadm_410.gdb\gadm'
UCDB = r'D:\Projects\SDG Indicators\data\GHS\processing.gdb\GHS_UCDB_THEME_GENERAL_CHARACTERISTICS_GLOBE_R2024A_edited'
RegionalRoadWidths = r'D:\Projects\SDG Indicators\data\OSM\RegionalRoadWidths.csv'

#Start Time
Start_Time = time.time()

def process(iso):
    message = None
    if message is None:
        try:
            gdb = r'D:\Projects\SDG Indicators\SDG11\SDG11_7_1\output\%s.gdb' % iso
            arcpy.env.workspace = gdb
            #Get Data
            out_ucdb = '%s_ucdb' % iso
            out_le_polygon = '%s_osm_le_polygons' % iso
            out_la_polygon = '%s_osm_la_polygons' % iso
            out_na_polygon = '%s_osm_na_polygons' % iso
            out_roads = '%s_osm_roads' % iso
            df = pd.read_csv(RegionalRoadWidths)
            ## Roads ##
            #buffer
            buffered_roads = '%s_roads_buffered' % iso
            #dissolve
            dissolved_roads = '%s_roads_buff_dissolved' % iso
            #arcpy.Delete_management(dissolved_roads)
            arcpy.RepairGeometry_management(buffered_roads)
            arcpy.Dissolve_management(buffered_roads,dissolved_roads)
            #arcpy.PairwiseDissolve_analysis(buffered_roads,dissolved_roads)
            message = 'Done: ' + iso
        except Exception as e:
            message = 'Failed: ' + iso + ' ' + str(e)

    return message

iso_list = ['POL','DEU','IND']
for iso_to_process in iso_list:
    process(iso_to_process)
