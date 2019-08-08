'''
Python pipeline to import images to cas and convert images into table. 
'''
myCAS.loadactionset(actionset="image")

def convert_image_to_table(image_path, image_height, image_weight, table_name):
    myCAS.loadImages(
        path= image_path,
        casOut={"name":"images_t", "replace":True},
        decode=False,
        recurse=False
        )

# Changing color images to gray scale.
    myCAS.processImages(
        casout={"name":table_name, "replace":True}, 
    	imagefunctions=[{"functionOptions":{"functiontype":"CONVERT_COLOR", "type": "COLOR2GRAY"}},
                     {"functionOptions":{"functiontype":"GET_PATCH", "width": image_width, "height": image_height, "x": 0, "y": 290}}],
    	decode = True,
    	table={"name":"images_t"}
        )

# Make flat table (number_of_obs, number_of_pixels)
    myCAS.flattenImageTable(
        casout={"name":'gray_table_t', "replace":True },
    	table={"name":'gray_images_t'},
    	width = image_width,
		height = image_height
        )
    
def convert_table_to_image(table_name, image_label, output_dir, output_name, output_format, image_height, image_width):
    myCAS.condenseImages(
        casout={"name":"scored_images", "replace":True},
        width = image_width,
		height = image_height,
        #copyvars = {"_path_"},
        numberOfChannels='GRAY_SCALE_IMAGE',
        table = {"name" : table_name, "where" :image_label}
        )

myCAS.saveImages(
        caslib = "CASUSER",
        subDirectory = output_dir,
		images={"table":"scored_images"},
        type = output_format,
		prefix = output_name
        )