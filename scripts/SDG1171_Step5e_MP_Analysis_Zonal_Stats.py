#08/22/2024

#SDG 11.7.1
#"Average share of the built-up area of cities that is open space for public use for all,
#by sex, age and persons with disabilities"
#Step 5e: Compute percent of population with access to OPS

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
            #Get WP
            WP = r'D:\Projects\SDG Indicators\SDG11\data\WP\%s_ppp_2020_UNadj.tif' % (iso.lower())
            #Get Data
            ucdb_ops_clip = '%s_ucdb_OPS_clip' % iso
            out_ucdb = '%s_ucdb' % iso
            out_buf = '%s_ucdb_union_buf' % iso
            out_dis = '%s_ucdb_union_dis' % iso
            out_clip = '%s_ucdb_union_clip' % iso
            ucdb_access_intersect = '%s_ucdb_access_intersect' % iso
            complete = '%s_complete' % iso
            #Zonal Stats to compute total pop of each ucdb polygon
            arcpy.env.snapRaster = WP
            arcpy.env.cellSize = WP
            outtablename = '%s_UCDB_POP_Table' % iso
            ZonalStatisticsAsTable(out_ucdb,"UCDBID",WP,outtablename,"DATA","SUM")
            arcpy.JoinField_management(complete,"UCDBID",outtablename,"UCDBID",["SUM"])
            new_zone = 'Total_POP' 
            arcpy.AlterField_management(complete,"SUM",new_zone,new_zone)
            #Zonal Stats
            arcpy.env.snapRaster = WP
            arcpy.env.cellSize = WP
            outtablename2 = '%s_Access_POP_Table' % iso
            ZonalStatisticsAsTable(ucdb_access_intersect,"UCDBID",WP,outtablename2,"DATA","SUM")
            arcpy.JoinField_management(complete,"UCDBID",outtablename2,"UCDBID",["SUM"])
            new_zone = 'Access_POP'
            arcpy.AlterField_management(complete,"SUM",new_zone,new_zone)
            #Add percent access field
            pct_access_field = 'Pct_Access_to_Ops' 
            arcpy.AddField_management(complete,pct_access_field,'DOUBLE')
            expression = "(!Access_POP!/!Total_POP!)*100"
            arcpy.CalculateField_management(complete,pct_access_field,expression,"PYTHON")
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


