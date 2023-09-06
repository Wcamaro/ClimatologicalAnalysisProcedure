"""
Author: Walther C.A. Camaro G. : walther.camaro@gmail.com
"""

import process_trmm_3b42_daily
from process_trmm_3b42_daily import mat_to_dict, nvalues_dict, WriteGTiff_nvalues, calendardays
import datetime
from datetime import timedelta, date
import numpy as np
import os


folder_root = r'D:\Python_Projects\Data\TRMM\TRMM_3B42_daily'  #Original Not Real Time DataSet
for month in range(12,13):
    for year in range(1998,2017):
        initial_date = datetime.date(year,month,1)
        end_date = datetime.date(year,month,calendardays(year, month))
##        if month == 1:
##            end_date = datetime.date(year,month,15)
##            initial_date = datetime.date(year-1,12,16)
##        else:
##            end_date = datetime.date(year,month,15)
##            initial_date = datetime.date(year,month-1,16)
        idate = date.toordinal(initial_date)
        edate = date.toordinal(end_date)
        days = date.toordinal(end_date)-date.toordinal(initial_date)+1
        minvalue = 0
        dict_nvalues = {}
        for i in range(50,-50,-2):
            bbox1 = {
                    'top': i,
                    'bottom': i-2,
                    'left': -180,
                    'right': 180
                    }
            dict_matrix = mat_to_dict(folder_root,idate,edate,bbox1=bbox1,rt=None)
            nvalues_array = nvalues_dict(dict_matrix,minvalue)
            nvalues_array = np.asarray(nvalues_array, dtype=np.int)
            dict_nvalues[i]=nvalues_array
            folder_output = r'D:\Python_Projects\Results\TRMM\Rainfall_Days_TRMM_Daily'
        if not os.path.exists(folder_output):
            os.makedirs(folder_output)
        if len(str(initial_date.month))==1:
            init_month = '0'+str(initial_date.month)
        else:
            init_month = str(initial_date.month)
        if len(str(end_date.month))==1:
            end_month = '0'+str(end_date.month)
        else:
            end_month = str(end_date.month)
        if len(str(initial_date.day))==1:
            init_day = '0'+str(initial_date.day)
        else:
            init_day = str(initial_date.day)
        period_name = '%s.%s.%s_%s.%s.%s' % (initial_date.year,init_month,init_day,end_date.year,end_month,end_date.day)
        WriteGTiff_nvalues(dict_nvalues,folder_output,period_name,bbox1['left'],bbox1['right'],'NValuesBigger0mm')
        print 'Date = %s' % str(end_date)
print 'Thank You, Procedure Finished. By W.Camaro'

