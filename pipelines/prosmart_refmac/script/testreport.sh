export CCP4I2_TOP=/Volumes/home/martin/Dropbox/Programming/ccp4i2
export CCP4MG=/Applications/QtMG.app/Contents/ccp4mg-2.7.3
#IBRARY_PATH=$CCP4MG/Contents/ccp4mg-2.7.3/lib DYLD_FALLBACK_LIBRARY_PATH=$CCP4MG/Contents/ccp4mg-2.7.3/lib PYTHONPATH=$CCP4MG/../ccp4mg-2.7.3/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages:$CCP4I2_TOP/report:$CCP4I2_TOP/core:$CCP4I2_TOP/qtcore:$CCP4MG/../ccp4mg-2.7.3/lib:$PYTHONPATH python ./prosmart_refmac_report.py ~/Dropbox/CCP4/Nutlin3aDemo/I2Project2/CCP4_JOBS/job_12/XMLOUT.xml 36149ae196f611e2aa7f001f5b379fa0
PYTHONPATH=$PYTHONPATH:$CCP4I2_TOP/report:$CCP4I2_TOP/core $CCP4I2_TOP/bin/pyi2 ./prosmart_refmac_report.py ~/Dropbox/CCP4/Nutlin3aDemo/I2Project2/CCP4_JOBS/job_12/XMLOUT.xml 36149ae196f611e2aa7f001f5b379fa0