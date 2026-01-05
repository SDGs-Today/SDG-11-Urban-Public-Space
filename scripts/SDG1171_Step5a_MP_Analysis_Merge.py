#08/22/2024

#SDG Indicator 11.7.1
#"Average share of the built-up area of cities that is open space for public use for all,
#by sex, age and persons with disabilities"
#Step 5a: Analysis- Merge OPS and Roads

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
UCDB = r'D:\Projects\SDG Indicators\SDG11\SDG11_2_1\SDG11_2_1\SDG11_2_1.gdb\GHS_UCDB_THEME_GENERAL_CHARACTERISTICS_GLOBE_R2024A_edited'
RegionalRoadWidths = r'D:\Projects\SDG Indicators\SDG11\data\OSM\RegionalRoadWidths.csv'


#Start Time
Start_Time = time.time()

def process(iso):
    message = None
    if message is None:
        try:
            gdb = r'D:\Projects\SDG Indicators\SDG11\SDG11_7_1\country_outputs\%s.gdb' % iso
            arcpy.env.workspace = gdb
            #Get Data
            out_ucdb = '%s_ucdb' % iso
            ucdb_ops_clip = '%s_ucdb_OPS_clip' % iso
            ucdb_roads_clip = '%s_ucdb_roads_clip' % iso
            #Add UniqueIDs
            #UCDB
            #arcpy.DeleteField_management(out_ucdb,'UCDBID')
            arcpy.AddField_management(out_ucdb,'UCDBID','TEXT')
            counter = 0
            txt = 'UCDB'
            with arcpy.da.UpdateCursor(out_ucdb,'UCDBID') as cursor:
                for row in cursor:
                    row[0] = counter
                    row[0] = '%s_%s_%s' % (iso,txt,str(counter))
                    cursor.updateRow(row)
                    counter = counter + 1
            #Make a copy
            complete = '%s_complete' % iso
            #arcpy.Delete_management(complete)
            arcpy.CopyFeatures_management(out_ucdb,complete)
            #Merge OPS and Roads
            ucdb_ops_roads_merge = '%s_ucdb_ops_roads_merge' % iso
            #arcpy.Delete_management(ucdb_ops_roads_merge)
            arcpy.Merge_management([ucdb_ops_clip,ucdb_roads_clip],ucdb_ops_roads_merge)
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


