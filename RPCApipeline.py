'''
Python RPCA pipeline 
'''

from swat import *
myCAS = CAS('rdcgrd098', 33836, 'yunhe')
import swat.datamsghandlers as dmh

data_file = '10_Preprocessed' # File name
full_path = 'U:\\weather_data/RaleighAirport_01/'+data_file+'.csv'

# First need to copy data to U:\
def read_file_cvs(data_path):
    handler=dmh.CSV(data_path, skipinitialspace=True) 
    myCAS.addtable(table=data_file, replace=True, **handler.args.addtable)
    LoadedTable=myCAS.fetch(table=data_file)
    print(LoadedTable)

# Upload data to CAS for later actions
read_file_cvs(full_path)
# Run RPCA
myCAS.loadactionset(actionset="robustPca")
result=myCAS.robustPca(
   table={"name" : data_file},
   id={"STATION", "NAME", "DATE"},
   method="ALM",
   decomp="svd", 
   scale=True, 
   center=True,
   #cumEigPctTol=0.99,
   lambdaWeight=1.06,
   saveState={"name":"store", "replace":True}, 
   outmat={"lowrankMat":{"name":"lowrankmat", "replace":True}, 
           "sparseMat":{"name":"sparsemat", "replace":True}},
   outsvd={"svdleft":{"name":"svdleft", "replace":True}, 
           "svddiag":{"name":"svddiag", "replace":True},
           "svdright":{"name":"svdright", "replace":True}},
   anomalyDetection=True,
   anomalyDetectionMethod=1, # 0 : SIGVAR method; 1: R4S methods
   sigmaCoef=1, # Threshold to identify an observation to be outlier
   numSigVars=1, # SIGVAR ONLY: Number of outliers for data to be identified as anomaly
   useMatrix=False # False: Use standard deviation of original data True: Use standard deviation of sparse data   
)

score_path = 'U:\\weather_data/Greensboro_10/'+data_file+'.csv'
# SCoring and anomaly detection
myCAS.loadactionset(actionset="astore")
myCAS.score(
        table={"name" : data_file},
        options=[{"name":"RPCA_PROJECTION_TYPE","value":2}],
        rstore={"name":"store"}, 
        out={"name":"scored","replace":True}
        )
# Visualize cas matrices by downloading cas tables to memory. Watch out for large tables! Might take too long if table size is huge
output_s = myCAS.fetch(table={"name":"scored"}, to=10000, maxrows = 100000)['Fetch']
output_value = output_s.values

###################################################################################################################################
# Some basic manipulation of the table
# Simple analysis
myCAS.loadactionset(actionset = "simple") 
out=myCAS.summary(table=data_file)
print(out)

print(result.keys)
r1 = myCAS.fetch(table = {"name":"sparsemat"}, to = 61)
myCAS.columnInfo(table = {"name":"sparsemat"})
r2 = r1.values # nparray data
