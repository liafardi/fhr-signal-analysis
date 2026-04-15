import wfdb
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re
from scipy.stats import skew, kurtosis, ttest_ind
from scipy.interpolate import PchipInterpolator
import os

files = wfdb.get_record_list('ctu-uhb-ctgdb')
file_locations={}

#----Check if records already existing---
#---If not download from Physionet-----


for root,dirs,filenames in os.walk(os.getcwd()):
    for f in filenames:
         if f.endswith(".dat"):
            name=f.replace(".dat","")
            file_locations[name]=root
      
        
def find(record_name):
    if record_name in file_locations:
        found_dir=file_locations[record_name]
        original_cwd=os.getcwd()
        try:
            os.chdir(found_dir)
            return wfdb.rdrecord(record_name)
        finally:
            os.chdir(original_cwd)
    else:
        
        print(f"Το record {record_name} δεν βρεθηκε τοπικά και θα κατέβει από το PhysioNet...")
        return wfdb.rdrecord(record_name,pn_dir='ctu-uhb-ctgdb')
 


processed_signals=[]
ph_values=[]
results=[]
initial_records=len(files)


for record_name in files[:]:
    try:
        #---Read signal---
        record=find(record_name)

        
        is_normal = False
        ph = None

        for comment in record.comments:
            comment = comment.lower()

                #-----Delivery type % pH---
            if "deliv" in comment and "1" in comment:
                is_normal=True
                            
            if "ph" in comment:
                match=re.search(r"\d+\.\d+",comment)
                if match:
                    ph=float(match.group())
        
              
            #-----filter records------
        if is_normal and ph is not None:

             #----FHR signal---
            fhr=record.p_signal[:,0]
            
            fhr=fhr[~np.isnan(fhr)]
            #----Calculate the percentage of signal loss-----
            zeros_percent=np.sum(fhr==0)/len(fhr)*100

            #---Reject if signal loss > 15%
            if zeros_percent > 15:
                continue
            #--- Valid signals between 50 and 200
            valid=np.where((fhr>=50)&(fhr<=200))[0]

            if len(valid)>100:
                x=np.arange(len(fhr))
                            
                interp=PchipInterpolator(valid,fhr[valid])
                fhr_interp=interp(x)

                processed_signals.append(fhr_interp)
                ph_values.append(ph)
               
               
    except Exception as e:
        print(f"Error in {record_name}:{e}")

print(f"\nInitital dataset size: {len(files)} records")
print(f"Total records rejected: {len(files)-len(processed_signals)}")
print(f"Final dataset for analysis: {len(processed_signals)} signals\n")

#--------FEATURES------------------


#---Define necessary functions----

#--RMS------

def rms(x):
    return np.sqrt(np.mean(x**2))

#--Shannon Entropy--
def shannon_entropy(signal):
    hist,_= np.histogram(signal,bins=50)
    p = hist/np.sum(hist)
    p=p[p>0]
    return -np.sum(p*np.log2(p))

#----Means----
means = [np.mean(s) for s in processed_signals]
#----Standard Errors----
stds= [np.std(s) for s in processed_signals]
#----Skewness-----
skews=[skew(s) for s in processed_signals]
#----Kurtosis----
kurt=[kurtosis(s) for s in processed_signals]
#-----RMS---
RMS=[rms(s) for s in processed_signals]
#------Shannon Entropy-----
sh_en=[shannon_entropy(s) for s in processed_signals]


#------normal(ph>=7.2) and abnormal ph values----
ph_values = np.array(ph_values)

normal_ph = ph_values >= 7.20
abnormal_ph = ph_values < 7.20



#-------Features (MEAN,STD,SKEWNESS,KURTOSIS,RMS,SHANNON ENTROPY)----
features={
    "Mean": means,
    "Standard Error": stds,
    "Skewness": skews,
    "Kurtosis":kurt,
    "RMS":RMS,
    "Shannon Entropy":sh_en
    }


#-----T-Test for features (a=0.05)----
def ttest_feature(feature):
    return ttest_ind(np.array(feature)[normal_ph],np.array(feature)[abnormal_ph]).pvalue


for name,values in features.items():
    p = ttest_feature(values)
    
    if p<0.05:
        status = "Significant"
    else:
        status = "Not significant"
        
        
    results.append([name,p,status])

df=pd.DataFrame(results,columns=["Feature","p_value","Status"])
print(df)



#Boxplot Shannon Entropy
entropy=np.array(sh_en)

normal_entropy = entropy[normal_ph]
abnormal_entropy = entropy[abnormal_ph]


plt.figure()
plt.boxplot([normal_entropy,abnormal_entropy],tick_labels=["Normal pH>=7.20","Abnormal pH<7.20"])

plt.title("Shannon Entropy Distribution")
plt.ylabel("Shannon Entropy")
plt.xlabel("Groups")

plt.show()
                
