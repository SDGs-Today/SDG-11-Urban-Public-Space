# fill out columns

'osm_daily_public_transport_20241124'
def tag_to_col(fl,col):
    with arcpy.da.UpdateCursor(fl,
                               ['other_tags',col]) as cursor:
        for row in cursor:
            if row[0]:
                tag_list=row[0].split(',')
                for tag in tag_list:
                    if f'"{col}"' in tag:
                        thing = tag.split('"')[3]
                        row[1]=thing
                        cursor.updateRow(row)
                    else:
                        pass
