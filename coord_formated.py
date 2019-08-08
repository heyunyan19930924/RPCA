'''
Read image table. Save bees coordinate output into format for Brad to feed into ESP.
The format is:
    Each row represents each observation. Column labels: opcode	flags(ESP settings) _id_(image id) _image_(image 64bit code)	_nObjects_(number of objects)
	_Object0_(object id) P_Object0_(probability) _Object0_x	_Object0_y(object left lower coordinate) _Object0_width	_Object0_height(object width and height)
    Then other objects. Repeat the columns for objects
'''

myCAS.loadactionset(actionset="image")
import pandas as pd
import shutil
import numpy as np
np.set_printoptions(threshold=sys.maxsize)
import base64

def detect_bee_boundingbox(image, size_threshold):
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
                to_add = set([x*n+y for x in range(output_coord[0], output_coord[2]+1) for y in range(output_coord[1], output_coord[3]+1)])
                visited |= to_add
                output.append(output_coord)   # Track the output by array of form lrow, lcol, rrow, rcol              
    return output

def generate_search_list(dim):
    toReturn = []
    for i in range(1,dim+1):
        for j in range(i+1):
            toReturn.append([j, i])
        for j in range(-i, i):
            toReturn.append([i, j])
    return toReturn

# Convert original format [x_upperleft, y_upperleft, x_lowerright, y_lowerright] to Brad's format [ObjectID, P_Object, x_lowerleft, y_lowerleft, width, height]. 
def convert_format(coord):
    output = []
    for bee_coords in coord:
        bee_formated = ['bee',1,bee_coords[2], bee_coords[1], bee_coords[3]-bee_coords[1], bee_coords[2]-bee_coords[0]]
        output.extend(bee_formated)
    return output

image_width = 220
image_height = 640
# Read image table
images = pd.read_csv("data_matrix.csv")
images.pop('Unnamed: 0')

# Parameters to be tweaked.
color_threshold = 25
size_threshold = 30
search_dim = 3
direction = generate_search_list(search_dim)

# Output original format.
output = []
for i in range(len(images)):
    if (i%100 == 0):
        print('working on image '+str(i))
    image_data = images.iloc[i,1:].values
    image_data = image_data.reshape(image_height, image_width)
    image_data[image_data < color_threshold] = 0
    image_name = images['_path_'][i][-14:]
    current_output = (image_name,detect_bee_boundingbox(image_data, size_threshold))
    output.append(current_output)

# Convert original output format to Brad's format row by row.
image_file_path = 'cropped/foreground_rank823/'
num_rows = len(output)
max_num_object = 0
formated = []
for i in range(6, num_rows - 6):
    _id_ = np.int64(i)
    filename = output[i][0]
    with open(image_file_path + filename, "rb") as image_file:
        _image_ = base64.b64encode(image_file.read()).decode('utf8')
    _nObjects_ = len(output[i][1])
    formated_coord = convert_format(output[i][1])
    # If number of bees exceeds df column numbers, we need to expand df variable names
    max_num_object = max(max_num_object, len(output[i][1]))
    to_append = [_id_, _image_, _nObjects_]
    to_append.extend(formated_coord)
    formated.append(to_append)
    
# Create column names
col_names = ['_id_','_image_','_nObjects_']
for i in range(max_num_object):
    col_names.extend(['_Object'+str(i)+'_', 'P_Object'+str(i)+'_', '_Object'+str(i)+'_x',
                      '_Object'+str(i)+'_y', '_Object'+str(i)+'_width', '_Object'+str(i)+'_height'])
df = pd.DataFrame(formated, columns = col_names)
df.insert(loc = 0, column = 'opcode', value = 'I')
df.insert(loc = 1, column = 'flags', value = 'N')
# Save to .csv file
df.to_csv('bee_position_color_'+str(color_threshold)+'_size_'+str(size_threshold)+'searchdim_' + str(search_dim)+'.csv', index = False)