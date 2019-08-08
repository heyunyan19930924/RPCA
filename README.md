# RPCA
RPCA image processing
Robust Principal Component Analysis (RPCA) is a modification of classical PCA that enhances the robustness against corrupted observations.
RPCA decomposes data matrix M into two parts, M = L + S, where L usually has a lower rank, and S is sparse and contains noise and outliers.
While the low rank matrix L helps learning the data property and can be used for dimension reduction, the sparse matrix S provides information about anomalies

This work contains image processing pipeline that does image foreground extraction and defect detection using RPCA on CAS server. 

Pipeline: 
1. Read in image data (LOADIMAGES)                                                                 -> process images (PROCESSIMAGES)                                                              -> convert images into one table (FLATTENIMAGETABLE).

2. Apply RPCA on table. Foreground information contained in S matrix.                                                                                  CAS memory issue may occur if image table is too large.                  Solution: Resize images/ train on one part, score on the other.

3. Convert table back to a list of images (CONDENSEIMAGES)                               -> Export images (SAVEIMAGES)

Requirements: 
Need to connect to cas server and is able to get access to actionsets including 'images', 'robustPCA', etc.
