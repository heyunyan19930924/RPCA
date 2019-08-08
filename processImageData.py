'''
Python pipeline to Process image data and generate foreground/background images. 
'''

myCAS.loadactionset(actionset="robustPca")
myCAS.loadactionset(actionset="dataStep")
myCAS.loadactionset(actionset="image")
myCAS.loadactionset(actionset="astore")
import pandas as pd

image_path = 'path_training_images'
scoring_image_path = 'path_scoring_images'
# Enter resolution information of images. orig_image: original image resolution. cropped_: cropping coordinate info. image_: final resolution after resizing. 
orig_image_width, orig_image_height = 720, 1280
cropped_width = 440
cropped_height = 1280
image_width = 220
image_height = 640

# Reading pictures from image_path and load to CAS server.
myCAS.loadImages(
        path= image_path,
        casOut={"name":"gray_table_s", "replace":True},
        decode=False,
        recurse=False
        )

# Changing color images to gray scale.
myCAS.processImages(
        casout={"name":'gray_table_s', "replace":True}, 
    	imagefunctions=[#{"functionOptions":{"functiontype":"CONVERT_COLOR", "type": "COLOR2GRAY"}},
                     {"functionOptions":{"functiontype":"GET_PATCH", "width": cropped_width, "height": cropped_height, "x": orig_image_width-cropped_width, "y": orig_image_height-cropped_height}},
                     {"functionOptions":{"functiontype":"RESIZE", "width": image_width, "height": image_height}},],
    	decode = True,
    	table={"name":"gray_table_s"}
        )

# Make flat table (number_of_obs, number_of_pixels)
myCAS.flattenImageTable(
        casout={"name":'gray_table_s', "replace":True},
    	table={"name":'gray_table_s'},
    	width = image_width,
		height = image_height
        )

# Run this line of code if image dimension changed.
# We don't run this! Just change the RPCA working columns.
'''
myCAS.runCode(
        code="""data working_table; 
        set gray_table_t; 
        keep _path_ c1-c1536304; 
        run;
        """
        )
'''

# Image has already been converted to working table. Now let's do RPCA!
table_name = 'gray_table_s'
# Create working column name list
col_name = ['c'+str(x) for x in range(1, image_width*image_height+1)]
_lambdaWeight=1
_cumEigPctTol=1
myCAS.loadactionset(actionset="robustPca")
RPCAresult = myCAS.robustPca(
   table={"name" : table_name},
   id={"_path_"},
   method="ALM",
   decomp="svd", 
   scale=False, 
   center=True,
   #inputs=col_name,
   cumEigPctTol=_cumEigPctTol,
   lambdaWeight=_lambdaWeight,
   #svdMethod="RANDOM",
   saveState={"name":"store", "replace":True}, 
   outmat={"sparseMat":{"name":"gray_table_s", "replace":True}},
           #"lowrankMat":{"name":"lowrankmat", "replace":True}, 
   anomalyDetection=True,
   anomalyDetectionMethod=0, # 0 : SIGVAR method; 1: R4S methods
   sigmaCoef=1, # Threshold to identify an observation to be outlier
   numSigVars=1, # SIGVAR ONLY: Number of outliers for data to be identified as anomaly
   useMatrix=False # False: Use standard deviation of original data True: Use standard deviation of sparse data   
)
rank = RPCAresult['Summary']['Value'][1]
#sparsemat = myCAS.fetch(table={"name":"sparsemat"}, to=100000, maxrows = 100000)['Fetch']
#sparsemat.to_csv("sparse_mat_lambdaweight_0.5_rank_253.csv", index=False)

###################################### Output processed images #####################################################
'''
myCAS.runCode(
        code="""data scoredw;
			   	set scored;
				name_mod = cats(_name_,'.jpg');
				length   'nm'n varchar(25)             ;
                format 'nm'n $CHAR25.     ;
                'nm'n= PUT('name_mod'n,$CHAR25.);
				run ;
				"""
        )
'''

# Generating image table for output.
# foreground
# Extract file name as row index. Concatenate from the full path.
myCAS.dataStep.runCode(
        code="""data sparsemat_new; 
        set gray_table_s;
        name = substr(_path_,length(_path_)-13, 14);
        run ;"""
        )

myCAS.condenseImages(
        casout={"name":"sparsemat_new", "replace":True},
        width = image_width,
		height = image_height,
        copyvars = {"name"},
        numberOfChannels='COLOR_IMAGE',
        table = {"name" : "sparsemat_new"}
        )

myCAS.saveImages(
        caslib = "CASUSER",
        subDirectory = 'bees/colored_rank'+str(rank),
		images={"table":"sparsemat_new", "path":"name"},
        type = 'jpg',
		prefix = ''
        )

################################### Scoring ###################################################
myCAS.loadImages(
        path= scoring_image_path,
        casOut={"name":"gray_table_s", "replace":True},
        decode=False,
        recurse=False
        )

# Changing color images to gray scale.
myCAS.processImages(
        casout={"name":'gray_table_s', "replace":True}, 
    	imagefunctions=[#{"functionOptions":{"functiontype":"CONVERT_COLOR", "type": "COLOR2GRAY"}},
                     {"functionOptions":{"functiontype":"GET_PATCH", "width": cropped_width, "height": cropped_height, "x": orig_image_width-cropped_width, "y": orig_image_height-cropped_height}},
                     {"functionOptions":{"functiontype":"RESIZE", "width": image_width, "height": image_height}},],
    	decode = True,
    	table={"name":"images_s"}
        )

# Make flat table (number_of_obs, number_of_pixels)
myCAS.flattenImageTable(
        casout={"name":'gray_table_s', "replace":True},
    	table={"name":'gray_table_s'},
    	width = image_width,
		height = image_height
        )

scoring_table_name = 'gray_table_s'

# Score on the store file from training.
# Projection type 1: background. 2: foreground
SCOREresult = myCAS.score(
        table={"name" : scoring_table_name},
        options=[{"name":"RPCA_PROJECTION_TYPE","value":2}],
        rstore={"name":"store"}, 
        out={"name":"gray_table_s","replace":True}
        )

# Remove anomaly detection results column
myCAS.runCode(
        code="""data gray_table_s (drop = _outlier_detection_score_); 
        set gray_table_s; 
        run;
        """
        )

myCAS.runCode(
        code="""
        data working_table; 
        set gray_table_s;
        name = substr(_path_,length(_path_)-13, 14);
        run;
        """
        )

myCAS.condenseImages(
        casout={"name":"working_table", "replace":True},
        width = image_width,
		height = image_height,
        copyvars = {"name"},
        numberOfChannels='COLOR_IMAGE',
        table = {"name" : "working_table"}
        )

myCAS.saveImages(
        caslib = "CASUSER",
        subDirectory = 'bees/colored_rank'+str(rank),
		images={"table":"working_table", "path":"name"},
        type = 'jpg',
		prefix = ''
        )