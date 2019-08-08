'''
Detect bee coordinate box by detecting bright clusters. 
The idea was first filter out all dim pixels, then count connected bright components. Drop all components which have less area than size_threshold. It is not a learning process.
'''

# After promoting the table in SAS
myCAS.loadactionset(actionset="image")
import pandas as pd
import shutil
import numpy as np
np.set_printoptions(threshold=sys.maxsize)

image_width = 220
image_height = 640
image_path = 'bees/foreground_rank823'

# Reading pictures from image_path and load to CAS server.
myCAS.loadImages(
        path= image_path,
        casOut={"name":"images_s", "replace":True},
        decode=False,
        recurse=False
        )

# Changing color images to gray scale.
myCAS.processImages(
        casout={"name":'gray_images_s', "replace":True}, 
    	imagefunctions=[{"functionOptions":{"functiontype":"CONVERT_COLOR", "type": "COLOR2GRAY"}}],
                     #{"functionOptions":{"functiontype":"MUTATIONS", "type": "LIGHTEN"}},
                     #{"functionOptions":{"functiontype":"RESIZE", "width": image_width, "height": image_height}},],
    	decode = True,
    	table={"name":"images_s"}
        )

myCAS.flattenImageTable(
        casout={"name":'gray_table_s', "replace":True},
    	table={"name":'gray_images_s'},
    	width = image_width,
		height = image_height
        )

###################################### Main function to detect bees by detecting bright clusters ############################################
# New version that detects multiple adjacent pixels. Number of pixels are to be specified in the global variable "direction"
def detect_bee_boundingbox(image, size_threshold):
    # DFS for each bright cluster until all its bright neighbors are traversed.
    def dfs(image, row, col):
        nonlocal size, output_coord, visited, n
        global direction
        index = row*n + col
        if index not in visited and image[row][col] > 0:
            visited.add(index)
            size += 1
            output_coord[0] = min(output_coord[0], row)
            output_coord[1] = min(output_coord[1], col)
            output_coord[2] = max(output_coord[2], row)
            output_coord[3] = max(output_coord[3], col)
            for i in range(len(direction)):
                cur_row = row + direction[i][0]
                cur_col = col + direction[i][1]
                if cur_row < 0 or cur_row >= m or cur_col < 0 or cur_col >= n:
                    continue;
                dfs(image, cur_row, cur_col)
                
    m,n = image.shape
    visited = set([])
    output = []
    # entry at (i,j) is represented by index i*n+j
    for i in range(m):
        for j in range(n):
            index = i*n+j
            if (index in visited or image[i][j] == 0):
                continue
            size = 0
            output_coord = [i,j,i,j]
            dfs(image, i, j)
            # If cluster size smaller than size_threshold, ignore the threshold. Or add bounding box to output and add all pixels in bounding box to "visited" 
            if (size >= size_threshold):
                # Set all pixels in the bounding box to "visited"
                to_add = set([x*n+y for x in range(output_coord[0], output_coord[2]+1) for y in range(output_coord[1], output_coord[3]+1)])
                visited |= to_add
                output.append(output_coord)   # Track the output by array of form lrow, lcol, rrow, rcol              
    return output

def detect_bee_boundingbox_V2(image, size_threshold):
    def dfs(image, row, col):
        nonlocal size, output_coord, visited, n
        global direction
        index = row*n + col
        if index not in visited and image[row][col] > 0:
            visited.add(index)
            size += 1
            output_coord[0] = min(output_coord[0], row)
            output_coord[1] = min(output_coord[1], col)
            output_coord[2] = max(output_coord[2], row)
            output_coord[3] = max(output_coord[3], col)
            for i in range(len(direction)):
                cur_row = row + direction[i][0]
                cur_col = col + direction[i][1]
                if cur_row < 0 or cur_row >= m or cur_col < 0 or cur_col >= n:
                    continue;
                dfs(image, cur_row, cur_col)
                
    m,n = image.shape
    visited = set([])
    output = []
    # entry at (i,j) is represented by index i*n+j
    for i in range(m):
        for j in range(n):
            index = i*n+j
            if (index in visited or image[i][j] == 0):
                continue
            size = 0
            output_coord = [i,j,i,j]
            dfs(image, i, j)
            if (size >= size_threshold):
                output.append(output_coord)   # Track the output by array of form lrow, lcol, rrow, rcol              
    return output

# Generate search directions based on how many adjacent pixels to be searched. 
def generate_search_list(dim):
    toReturn = []
    for i in range(1,dim+1):
        for j in range(i+1):
            toReturn.append([j, i])
        for j in range(-i, i):
            toReturn.append([i, j])
    return toReturn

############################## Test ##########################################################################
images = myCAS.fetch(table={"name":"gray_table_s"}, to = 10, maxRows = 10)['Fetch']

color_threshold = 15
size_threshold = 30

image_index = 1401
#images = images.iloc[:,0:image_width*image_height+1]
image_data = images.iloc[image_index,1:].values
image_name = images['_path_'][image_index][-14:]
image_data = image_data.reshape(image_height, image_width)
image_data[image_data < color_threshold] = 0

detect_bee_boundingbox(image_data, size_threshold)

#################################### Full run ##############################################################

color_threshold = 20
size_threshold = 30
search_dim = 3
direction = generate_search_list(search_dim)
col_labels = ['c' + str(idx) for idx in range (0, image_width*image_height+1)]
col_labels[0] = "_path_"

images = myCAS.fetch(table={"name":"gray_table_s", "vars":col_labels}, to = 100000, maxRows = 100000, sortBy={"name":"_path_"}, )['Fetch']
# Or read existing data from local
images = pd.read_csv("data_matrix.csv")
images.pop('Unnamed: 0')

output = []
for i in range (len(images)):
    if (i%100 == 0):
        print('working on image '+str(i))
    image_data = images.iloc[i,1:].values
    image_data = image_data.reshape(image_height, image_width)
    # Set all pixels that has lower value than color_threshold to 0.
    image_data[image_data < color_threshold] = 0
    image_name = images['_path_'][i][-14:]
    current_output = (image_name,detect_bee_boundingbox(image_data, size_threshold))
    output.append(current_output)

# Write output into .txt file
with open('bee_position_color_'+str(color_threshold)+'_size_'+str(size_threshold)+'searchdim_' + str(search_dim)+'.txt', 'w') as fp:
    fp.write('\n'.join('%s : %s' % x for x in output))