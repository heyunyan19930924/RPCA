'''
Manipulate downloaded castable locally and upload to castable again.
'''

import numpy as np
import pandas as pd
import swat.cas.datamsghandlers as dmh

# Before uploading, Make sure the numeric data are in correct format, for example float, int etc., not 'object'  

# Function that converts columns into numeric datatype.
# Convert column by column. Inefficient when column number is huge.
def coerce_df_columns_to_numeric(df, column_list):
    df[column_list] = df[column_list].apply(pd.to_numeric, errors='ignore')

# Function that upload dataframe to CAS server as CAStable.
def convert_dataframe_to_castable(df, output):
    handler = dmh.PandasDataFrame(df)
    myCAS.addtable(table=output, replace = True, **handler.args.addtable)
    
# Did some modification to numerical data
target_dataframe = lowrank
mapped = target_dataframe.values[:,1:]
mapped = mapped.astype(np.float)
#mapped[:,:-1] = np.clip(mapped[:,:-1], 0, 255)
mapped += np.min(mapped)

# Initialize column list as input when initializing dataframe.
col_name = ['c'+str(x) for x in range(1, image_width*image_height+2)]
col_name[-1] = '_outlier_detection_score_'
df = pd.DataFrame(mapped, columns = col_name)
df['_path_'] = lowrank['_path_']
convert_dataframe_to_castable(df, 'score_lowrank_mapped')
mapped_castable = myCAS.fetch(table={"name":"mat_score_lowrank_mapped"})['Fetch']

# Plot mapped image
myCAS.condenseImages(
        casout={"name":"scored_images", "replace":True},
        width = image_width,
		height = image_height,
        #copyvars = {"_path_"},
        numberOfChannels='GRAY_SCALE_IMAGE',
        table = {"name" : "score_lowrank_mapped", "where" :'_path_=\"/u/yunhe/GSK_data/HubAngle_for_RPCA/5015#087967904_S207_HubAngle.20170901-000004.jpg\"'}
        )

myCAS.saveImages(
        caslib = "CASUSER",
        subDirectory = 'GSK_data/background',
		images={"table":"scored_images"},
        type = 'jpg',
		prefix = 'mapped_add_all'
        )