#James Gibson
#08/22/2024

#SDG Indicator 11.7.1
#Step 1: Data Prep
#Create gdbs for each nation and extract GUPPDv2 polygons per nation

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

GADMGlobal = r'C:\Users\Mike\SDSN Dropbox\Michael Andrews\SDGs Today\Projects\SDG Indicators by CIESIN\data\GADM\gadm_410-gdb\gadm_410.gdb\gadm'
UCDB = r'C:\Users\Mike\SDSN Dropbox\Michael Andrews\SDGs Today\Projects\SDG Indicators by CIESIN\data\GHS\processing.gdb\GHS_UCDB_THEME_GENERAL_CHARACTERISTICS_GLOBE_R2024A_edited'

#Start Time
Start_Time = time.time()

def process(iso):
    message = None
    if message is None:
        try:
            gdb = r'E:\Projects\SDG Indicators by CIESIN\SDG11\SDG11_7_1\output\%s.gdb' % iso
            arcpy.CreateFileGDB_management(r'E:\Projects\SDG Indicators by CIESIN\SDG11\SDG11_7_1\output','%s.gdb' % iso)
            arcpy.env.workspace = gdb
            #Select UCDB polygons
            where_clause = '"ISO_code" = \'%s\'' % iso
            out_ucdb = '%s_ucdb' % iso
            arcpy.Select_analysis(UCDB,out_ucdb,where_clause)
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


