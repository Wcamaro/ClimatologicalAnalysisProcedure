"""
Author: Walther C.A. Camaro G. : walther.camaro@gmail.com
"""

#import process_trmm_3b42_daily
from process_trmm_3b42_daily import init,  WriteGTiff_daily, calendardays
import datetime
from datetime import timedelta, date
import numpy as np
import os


months = range(1,2)
folder_root = r'D:\Python_Projects\Data\TRMM\TRMM_3B42_daily'  #Original Not Real Time DataSet
folder_rootRT = r'D:\Python_Projects\Data\TRMM\TRMM_3B42RT_daily' #Original Real Time Dataset



for dat in months:
     for year in range(2016,2017):
        initial_date = datetime.date(year, dat, 30)
        ##end_date = datetime.date(year, dat, calendardays(year, month))
        end_date = datetime.date(year, dat, 31)
        dict_matrix = {}
        for kcum in range(date.toordinal(initial_date),date.toordinal(end_date)+1):
            year = str(date.fromordinal(kcum).year)
            if len(str(date.fromordinal(kcum).month))==2:
                month = str(date.fromordinal(kcum).month)
            else:
                month = '0%s' % str(date.fromordinal(kcum).month)
            if len(str(date.fromordinal(kcum).day))==2:
                day = str(date.fromordinal(kcum).day)
            else:
                day = '0%s' % str(date.fromordinal(kcum).day)
            if os.path.exists(r'%s\%s\%s\3B42_daily.%s.%s.%s.7.bin' % (folder_root, year, month, year, month, day)):
                filename = r'%s\%s\%s\3B42_daily.%s.%s.%s.7.bin' % (folder_root, year, month, year, month, day)
                RT = None
            elif os.path.exists(r'%s\%s\%s\3B42RT_daily.%s.%s.%s.bin' % (folder_rootRT, year, month, year, month, day)):
                filename = r'%s\%s\%s\3B42RT_daily.%s.%s.%s.bin' % (folder_rootRT, year, month, year, month, day)
                RT = 1
            elif os.path.exists(r'%s\%s\%s\3B42_Daily.%s%s%s.7.nc4' % (folder_root, year, month, year, month, day)):
                filename = r'%s\%s\%s\3B42_Daily.%s%s%s.7.nc4' % (folder_root, year, month, year, month, day)
                RT = 0
            elif os.path.exists(r'%s\%s\%s\3B42RT_Daily.%s%s%s.7.nc4' % (folder_rootRT, year, month, year, month, day)):
                filename = r'%s\%s\%s\3B42RT_Daily.%s%s%s.7.nc4' % (folder_rootRT, year, month, year, month, day)
                RT = 1
            else:
                filename = None
                continue
            (matrix,bbox) = init(filename, rt=RT)
            matrix = np.asarray(matrix)
            matrix [matrix == -9999.9] = -99
            dict_matrix[kcum] = matrix
        if dict_matrix == {}:
            continue
        else:
            folder_output = r'D:\Python_Projects\Results\TRMM\Cumulated_TRMM_Daily\Daily'
            if not os.path.exists(folder_output):
                os.makedirs(folder_output)
            WriteGTiff_daily(dict_matrix,folder_output,'Daily_TRMMM',bbox['left'],bbox['right'],bbox['bottom'],bbox['top'])
print 'Thank You, Procedure Finished. By W.Camaro'
            
                
                
