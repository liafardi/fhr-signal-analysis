# fhr-signal-analysis
Biomedical signal analysis of fetal heart rate (FHR) data with statistical feature extraction and pH classification

## Overview
This project analyzes fetal heart rate (FHR) signals and investigates their relationship with neonatal pH levels. The goal is to identify statistical differences between normal and abnormal cases using signal-derived features.

## Objectives
- Process fetal heart rate (FHR) signals  
- Extract meaningful statistical features  
- Compare normal and abnormal pH groups  
- Identify significant differences using statistical testing  

## Dataset
The dataset is obtained from PhysioNet (CTU-UHB CTG database).  
It contains fetal heart rate signals along with clinical information such as pH values.

## Methods
### Signal Processing
- Removal of invalid values and noise  
- Interpolation of missing signal segments  
- Filtering based on signal quality

### Feature Extraction
The following features were computed:
- Mean  
- Standard deviation  
- Skewness  
- Kurtosis  
- Root Mean Square (RMS)  
- Shannon Entropy

### Statistical Analysis
- Two-sample t-tests were applied  
- Comparison between:
  - Normal pH (≥ 7.20)  
  - Abnormal pH (< 7.20)  

## Tools & Technologies
- Python  
- NumPy  
- Pandas  
- SciPy  
- Matplotlib
  
## Key Results
- Significant differences were observed in selected statistical features
- Entropy and variability-related metrics showed strong discriminative power  
- Signal characteristics vary noticeably between normal and abnormal cases
