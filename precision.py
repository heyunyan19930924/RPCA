'''
Function that calculates accuracy, precision, recall from comparing scoring output with hand labeled negatives
Enter negatives in <defects>
'''

import numpy as np
# Input index of defects
defects = set()
defects.add('/u/yunhe/GSK_data/scoring/5026#017443052_S207_HubAngle.20170901-005747.jpg')
defects.add('/u/yunhe/GSK_data/scoring/5026#017445399_S207_HubAngle.20170901-015203.jpg')
defects.add('/u/yunhe/GSK_data/scoring/5026#017445887_S207_HubAngle.20170901-020239.jpg')
defects.add('/u/yunhe/GSK_data/scoring/5026#017446005_S207_HubAngle.20170901-020455.jpg')
defects.add('/u/yunhe/GSK_data/scoring/5026#017455497_S207_HubAngle.20170901-053954.jpg')
defects.add('/u/yunhe/GSK_data/scoring/5026#017457231_S207_HubAngle.20170901-081732.jpg')
defects.add('/u/yunhe/GSK_data/scoring/5026#017458092_S207_HubAngle.20170901-084024.jpg')
defects.add('/u/yunhe/GSK_data/scoring/5026#017459688_S207_HubAngle.20170901-101026.jpg')
defects.add('/u/yunhe/GSK_data/scoring/5026#017454100_S207_HubAngle.20170901-050721.jpg')
            
# Output is a 5*5 table with row: para1 and col: para2 and entries of triples. First element shows number of anomalies. Second: precision (TP/ALL P). Third: recall (TP/ALL T).
# TFmatrix stores TP, TN, FP, FN
# accuracy stores accuracy and F1-measure
num_para1, num_para2 = len(parameter_list_1), len(parameter_list_2)
num_total_sample = len(outlier_result_store[0][0])
t = len(defects)
ADmatrix = np.zeros((num_para1, num_para2,3))
TFmatrix = np.zeros((num_para1, num_para2,4))  
accuracy = np.zeros((num_para1, num_para2,2)) 
for i in range(num_para1):
    for j in range(num_para2):
        num_TP,num_FP,num_TN,num_FN = 0, 0, 0, 0
        if (type(outlier_result_store[i][j][0,1]) == float):
            ADmatrix[i,j,0] = np.count_nonzero(outlier_result_store[i][j][:,1])
            num_TP = 0
            for p in outlier_result_store[i][j]:
                if ((p[0] in defects) & (p[1] == 1.0)):
                    num_TP += 1
            ADmatrix[i,j,1] = num_TP*1.0/(ADmatrix[i,j,0]*1.0)
            ADmatrix[i,j,2] = num_TP*1.0/(t*1.0)
        else:
            ADmatrix[i,j,0] = np.count_nonzero(outlier_result_store[i][j][:,0])
            num_TP = 0
            for p in outlier_result_store[i][j]:
                if ((p[1] in defects) & (p[0] == 1.0)):
                    num_TP += 1
            ADmatrix[i,j,1] = num_TP*1.0/(ADmatrix[i,j,0]*1.0)
            ADmatrix[i,j,2] = num_TP*1.0/(t*1.0)
        num_FP = ADmatrix[i,j,0] - num_TP
        num_TN = t - num_TP
        num_FN = num_total_sample - num_TP - num_FP - num_TN
        TFmatrix[i,j,0] = num_TP
        TFmatrix[i,j,1] = num_FP
        TFmatrix[i,j,2] = num_TN
        TFmatrix[i,j,3] = num_FN
        accuracy[i,j,0] = (num_TP + num_FN) / num_total_sample
        accuracy[i,j,1] = 2/(1/ADmatrix[i,j,1] + 1/ADmatrix[i,j,2])

