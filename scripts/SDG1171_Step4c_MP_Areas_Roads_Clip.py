#08/22/2024

#SDG Indicator 11.7.1
#Step 4c: Areas- Roads Clip

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
            #dissolve
            dissolved_roads = '%s_roads_buff_dissolved' % iso
            #Clip to UCDB
            ucdb_roads_clip = '%s_ucdb_roads_clip' % iso
            #arcpy.RepairGeometry_management(dissolved_roads)
            arcpy.PairwiseClip_analysis(dissolved_roads,out_ucdb,ucdb_roads_clip)
            #Now we can get road area
            arcpy.AddField_management(ucdb_roads_clip,'Area_squarekm_roads','DOUBLE')
            arcpy.CalculateField_management(ucdb_roads_clip,'Area_squarekm_roads',"!shape.geodesicArea@squarekilometers!",'PYTHON')
            message = 'Done: ' + iso
        except Exception as e:
            message = 'Failed: ' + iso + ' ' + str(e)

    return message

def main():
    print('Starting Script...')
    mylist=[]
    with arcpy.da.SearchCursor(UCDB,['ISO_code']) as cursor:
        for row in cursor:
            if row[0] in mylist:
                pass
            else:
                mylist.append(row[0])
    length = len(mylist)
    print("Ready to start processing {} countries".format(length))
    pool = multiprocessing.Pool(processes=20, maxtasksperchild=1)
    results = pool.imap_unordered(process,mylist)
    counter = 0
    for result in results:
        print(result)
        counter = counter + 1
        print("{} countries processed out of {}".format(counter,length))
        print('---------------------------------------------------------')
    pool.close()
    pool.join()
    End_Time = time.time()
    Total_Time = End_Time - Start_Time
    print('Total Time: %s' % str(Total_Time))
    print('Script Complete')
    
    


if __name__ == '__main__':
    main()


