"""
Author: Walther C.A. Camaro G. : walther.camaro@gmail.com
"""
"""
Import process,gets data from hdf and creates matrix to calculate SPI,
calculate media and ln media from a array dictionary. 
"""

from osgeo import gdal
import numpy as np
from exceptions import TypeError, ImportError
import os,sys
import datetime
from PIL import Image
from netCDF4 import Dataset
from datetime import timedelta, date
from osgeo import gdal_array
from osgeo import osr
global bbox_trmm2_daily
global cells_degree
global cells_size
import scipy as sp
from scipy import stats


"""
bbox bin
"""

bbox_trmm2_daily = {
        'top': 50,
        'bottom': -50,
        'left': -180,
        'right': 180
}


"""
General Parameters
"""

cells_size = 0.25
cells_degree = 1/cells_size

def init(filename,bbox=None,rt=None):
    """
    Loads a TRMM data into a matrix. The Open method is set to load the :0 band of the file
    which corresponds to the precipitation data. To load the error switch to the :1.
    """
    ext = os.path.splitext(filename)[-1]
    bbox = checkBbox(bbox)
    reshaped = reshape(filename,ext,rt)
    ##masked = mask(reshaped)
    rearranged = rearrange(reshaped)
    matrix = cut(rearranged,bbox)
    return matrix, bbox 
    
    

def checkBbox(bbox):
    """
    Returns the correct bbox.
    """
    if not bbox:
                    bbox = bbox_trmm2_daily
    elif not isinstance(bbox,dict):
            raise TypeError('BBOX must be a dictionary in key: values pairs !!!!')
    return bbox

def reshape(filename,ext,rt=None):
    """
    Opens and reshapes an image file.
    """
    if ext == '.bin':
        fp = open(filename, 'rb')
        data_string = fp.read()
        fp.close()
        raw_file = np.fromstring(data_string, np.float32)
        raw_file = raw_file.byteswap()
        raw_file = np.asarray(raw_file, np.float32)
        if rt == 1:
            reshaped_matrix = raw_file.reshape(480, 1440)
            reshaped_matrix = reshaped_matrix[40:440]
        else:
            reshaped_matrix = raw_file.reshape(400, 1440)
        reshaped_matrix = np.flipud(reshaped_matrix)
        return reshaped_matrix
    elif ext == '.nc4':
        raw_file = Dataset(filename)
        array = raw_file['precipitation'][:]
        array_rot = np.rot90(array)
        right_array = array_rot[:, 720:]
        left_array = array_rot[:, :720]
        reversed_array = np.hstack((right_array, left_array))
        if rt == 1:
            reversed_array = reversed_array[40:440]
        return reversed_array

def mask(matrix):
    """
    Applies a mask to image in order to remove the water cells.

    """
    mask_image = r'D:\Python_Projects\Data\TRMM\Mask_image\trmm_land_sea_wide_bin.png'
    img = Image.open(mask_image)
    imgarray = np.array(img)
    matrix = np.array(matrix)
    masked = matrix / imgarray
    return masked

def rearrange(matrix):
    b = np.split(matrix,2,axis=1)[0]
    a = np.split(matrix,2,axis=1)[1]
    rearranged = np.concatenate((a,b),axis=1)
    return rearranged
    
def cut(raw_matrix,bbox):
    """
    Fuction for slicing the given matrix based on the passed bounding box

    """

    bbox_matrix = bbox_trmm2_daily
    cell_bbox_size = {
            'x': abs(bbox['left']-bbox['right'])*cells_degree,
            'y': abs(bbox['top']-bbox['bottom'])*cells_degree
    }
    slice_start = {
            'x': abs(bbox_matrix['left']-bbox['left'])*cells_degree,
            'y': abs(bbox_matrix['top']-bbox['top'])*cells_degree
    }
    slice_end = {
            'x': slice_start['x']+cell_bbox_size['x'],
            'y': slice_start['y']+cell_bbox_size['y'],
    }
    matrix_sliced_y = raw_matrix[slice_start['y']:slice_end['y']]
    matrix_sliced = [row[slice_start['x']:slice_end['x']] for row in matrix_sliced_y]
    return matrix_sliced

def media(dict_x):
    """
    Calculate average value between differents arrays inside at an dictionary,
    for values bigger or equal to zero.
    """
    n_elements = np.empty([len(dict_x[dict_x.keys()[0]]),len((dict_x[dict_x.keys()[0]])[0])])
    cumulate_value = np.empty([len(dict_x[dict_x.keys()[0]]),len((dict_x[dict_x.keys()[0]])[0])])

    for key in dict_x.keys():
        n_elements = n_elements +(dict_x[key]>=0)*1
        n_elements[np.isnan(dict_x[key])] = np.nan
        n_elements[np.isinf(dict_x[key])] = np.inf
        cumulate_value = cumulate_value +(dict_x[key]*(dict_x[key]>=0))
    mean = cumulate_value / n_elements
    return mean,n_elements

def medialn(dict_x,n_elements):
    """
    Calculate average value (lnvalue) between differents arrays inside at an dictionary,
    for values differents to zero.
    """
    cumulate_value = np.empty([len(dict_x[dict_x.keys()[0]]),len((dict_x[dict_x.keys()[0]])[0])])

    for key in dict_x.keys():
        cumulate_value = cumulate_value +(dict_x[key])
    mean = cumulate_value / n_elements
    return mean

def probnorain(dict_x):
    """
    Calculate zero discrete prob.
    """
    n_elements = np.empty([len(dict_x[dict_x.keys()[0]]),len((dict_x[dict_x.keys()[0]])[0])])
    NR = np.empty([len(dict_x[dict_x.keys()[0]]),len((dict_x[dict_x.keys()[0]])[0])])

    for key in dict_x.keys():
        n_elements = n_elements +(dict_x[key]==0)*1
        n_elements[np.isnan(dict_x[key])] = np.nan
        n_elements[np.isinf(dict_x[key])] = np.inf
        NR = NR +(dict_x[key]*(dict_x[key]>0))
    NR = n_elements / len(dict_x.keys())
    return NR

def cumulatedict(dict_x):

    cumulate_value = np.empty([len(dict_x[dict_x.keys()[0]]),len((dict_x[dict_x.keys()[0]])[0])])

    for key in dict_x.keys():
        cumulate_value = cumulate_value +(dict_x[key]*(dict_x[key]>=0))
    return cumulate_value

def calendardays(year,month):
    if (year % 4 == 0 and not year % 100 == 0)or year % 400 == 0:
        days = [31,29,31,30,31,30,30,31,30,31,30,31]
    else:
        days = [31,28,31,30,31,30,30,31,30,31,30,31]
    return days[month-1]

def WriteGTiff(dict_x,folder,month,xmin,xmax,ymin,ymax,cumulated,name):
    """
    Write a Gtiff, from a dictionary (Elements = Numpy Array type) defining each
    element from the dictionary like a band in the Raster.
    """
    gdal.AllRegister()
    driver = gdal.GetDriverByName('Gtiff')
    nyears = len(dict_x.keys())
    nrows,ncols = np.shape(dict_x[dict_x.keys()[0]])
    xres = (xmax-xmin)/float(ncols)
    yres = (ymax-ymin)/float(nrows)
    geotransform = (xmin,xres,0,ymax,0,-yres)
    filename = r'%s/Trmm3B42_%s_%s.%s.tif' % (folder,str(cumulated),month,name)
    outDataset = driver.Create(filename,ncols,nrows,nyears,gdal.GDT_Float32)
    outDataset.SetGeoTransform(geotransform)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    outDataset.SetProjection(srs.ExportToWkt())
    a = (map(int,dict_x.keys()))
    yearmin = min(a)
    yearmax = max(a)
    a = sorted(a)
    array = np.empty([nrows,ncols])
    nband = 1
    file = open(r'%s_Band_year_relations.csv' % filename,'w')
    file.write('Year,Gtiff_Band\n')
    for y in a:
        year = str(y)
        array = dict_x[year]
        array[np.isnan(array)] = -99
        array[np.isinf(array)] = -99
        outband = outDataset.GetRasterBand(nband)
        outband.SetNoDataValue(-99)
        outband.WriteArray(array)
        file.write('%s,%s\n' %(year,str(nband)))
        nband = nband+1
        outband.GetStatistics(0,1)
        outband = None
    outDataset = None
    file.close()
        

def WriteGTiff_2(dict_x,folder,name,xmin,xmax,ymin,ymax,cumulated,dday):
    """
    Write a Gtiff, from a dictionary (Elements = Numpy Array type) defining each
    element from the dictionary like a Raster.
    """
    gdal.AllRegister()
    driver = gdal.GetDriverByName('Gtiff')
    nrows,ncols = np.shape(dict_x[dict_x.keys()[0]])
    xres = (xmax-xmin)/float(ncols)
    yres = (ymax-ymin)/float(nrows)
    geotransform = (xmin,xres,0,ymax,0,-yres)
    for year in dict_x.keys():
        endd = datetime.date(int(year),cumulated,dday)
        if len(str(endd.day))==1:
            end_day = '0%s' %str(endd.day)
        else:
            end_day = str(endd.day)
        if len(str(endd.month))==1:
            end_month = '0%s' %str(endd.month)
        else:
            end_month = str(endd.month)
        end_date = '%s%s%s' %(endd.year,end_month,end_day)
        filename = r'%s/Trmm3B42_%s_%s.tif' % (folder,name,end_date)
        outDataset = driver.Create(filename,ncols,nrows,1,gdal.GDT_Float32)
        outDataset.SetGeoTransform(geotransform)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        outDataset.SetProjection(srs.ExportToWkt())
        nband = 1
        array = np.empty([nrows,ncols])
        array = dict_x[year]
        array[np.isnan(array)] = -99
        array[np.isinf(array)] = -99
        outband = outDataset.GetRasterBand(nband)
        outband.SetNoDataValue(-99)
        outband.WriteArray(array)
        outband.GetStatistics(0,1)
        outband = None
        outDataset = None

def WriteGTiff_media(dict_x,folder,name,xmin,xmax,ymin,ymax,dday):
    """
    Write a Gtiff, from a dictionary (Elements = Numpy Array type) defining each
    element from the dictionary like a Raster.
    """
    gdal.AllRegister()
    driver = gdal.GetDriverByName('Gtiff')
    nrows,ncols = np.shape(dict_x[dict_x.keys()[0]])
    xres = (xmax-xmin)/float(ncols)
    yres = (ymax-ymin)/float(nrows)
    geotransform = (xmin,xres,0,ymax,0,-yres)
    for month in dict_x.keys():
        if len(str(dday))==1:
            end_day = '0%s' %str(dday)
        else:
            end_day = str(dday)
        if len(str(month))==1:
            end_month = '0%s' %str(month)
        else:
            end_month = str(month)
        end_date = '%s%s' %(end_month,end_day)
        filename = r'%s/Trmm3B42_%s_%s.tif' % (folder,name,end_date)
        outDataset = driver.Create(filename,ncols,nrows,1,gdal.GDT_Float32)
        outDataset.SetGeoTransform(geotransform)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        outDataset.SetProjection(srs.ExportToWkt())
        nband = 1
        array = np.empty([nrows,ncols])
        array = dict_x[month]
        array[np.isnan(array)] = -99
        array[np.isinf(array)] = -99
        outband = outDataset.GetRasterBand(nband)
        outband.SetNoDataValue(-99)
        outband.WriteArray(array)
        outband.GetStatistics(0,1)
        outband = None
        outDataset = None

def nvalues_dict(dict_matrix,minvalue):
    dict_shape = np.shape(dict_matrix[0])
    dim_flat = dict_shape[0]*dict_shape[1]
    quantvector = []
    for pos in range(0,dim_flat):
        vect =np.asarray([dict_matrix[k].flat[pos] for k in dict_matrix.keys()],dtype = np.float32)
        vect = vect[vect>minvalue]
        ##vect = vect[vect == minvalue]  ##Min value = 0 mi da giorni non piovosi
        quantvector = np.append(quantvector, len(vect))
    quantarray = np.reshape(quantvector, dict_shape)
    return quantarray


def mat_to_dict(folder_root,idate,edate,bbox1=None,rt=None):
    dict_matrix = {}
    for cdate in range(idate,edate+1):
            year_curr = str(date.fromordinal(cdate).year)
            if len(str(date.fromordinal(cdate).month))==2:
                month_curr = str(date.fromordinal(cdate).month)
            else:
                month_curr = '0%s' % str(date.fromordinal(cdate).month)
            if len(str(date.fromordinal(cdate).day))==2:
                day_curr = str(date.fromordinal(cdate).day)
            else:
                day_curr = '0%s' % str(date.fromordinal(cdate).day)
            if os.path.exists(r'%s/%s/%s/3B42_daily.%s.%s.%s.7.bin' % (folder_root, year_curr, month_curr, year_curr, month_curr, day_curr)):
                filename = r'%s/%s/%s/3B42_daily.%s.%s.%s.7.bin' % (folder_root, year_curr, month_curr, year_curr, month_curr, day_curr)
                RT = None
            elif os.path.exists(r'%s\%s\%s\3B42_Daily.%s%s%s.7.nc4' % (folder_root, year_curr, month_curr, year_curr, month_curr, day_curr)):
                filename = r'%s\%s\%s\3B42_Daily.%s%s%s.7.nc4' % (folder_root, year_curr, month_curr, year_curr, month_curr, day_curr)
                RT = None
            else:
                filename = None
                print 'Not current_date file: %s' % date.fromodinal(cdate)
                continue
            (matrix,bbox) = init(filename, bbox=bbox1, rt=RT)
            matrix = np.asarray(matrix)
            matrix [matrix == -9999.9] = -99
            dict_matrix[cdate-idate] = matrix
    return dict_matrix

def dict_to_mat(dict_x):
    coords = sorted(dict_x.keys(), reverse=True)
    array = dict_x[coords[0]]
    for coord in coords[1:]:
        array = np.append(array, dict_x[coord], axis=0)
    return array 


def WriteGTiff_nvalues(dict_x,folder,datename,xmin,xmax,name):
    """
    Write a Gtiff, from a dictionary (Elements = Numpy Array type) defining each
    element from the dictionary like a Raster.
    """
    gdal.AllRegister()
    driver = gdal.GetDriverByName('Gtiff')
    array = dict_to_mat(dict_x)
    nrows,ncols = np.shape(array)
    array[np.isnan(array)] = -99
    array[np.isinf(array)] = -99
    xres = (xmax-xmin)/float(ncols)
    ymax = max(dict_x.keys())
    ymin = min(dict_x.keys())-2
    yres = (ymax-ymin)/float(nrows)
    geotransform = (xmin,xres,0,ymax,0,-yres)
    filename = r'%s/Trmm3B42_%s_%s.%s_%s.tif' % (folder,str(name),datename,str(ymax),str(ymin))
    outDataset = driver.Create(filename,ncols,nrows,1,gdal.GDT_Int32)
    outDataset.SetGeoTransform(geotransform)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    outDataset.SetProjection(srs.ExportToWkt())
    nband = 1
    outband = outDataset.GetRasterBand(nband)
    outband.SetNoDataValue(-99)
    outband.WriteArray(array)
    outband.GetStatistics(0,1)
    outband = None
    outDataset = None

def WriteGTiff_daily(dict_x,folder,name,xmin,xmax,ymin,ymax):
    """
    Write a Gtiff, from a dictionary (Elements = Numpy Array type) defining each
    element from the dictionary like a Raster.
    """
    gdal.AllRegister()
    driver = gdal.GetDriverByName('Gtiff')
    nrows,ncols = np.shape(dict_x[dict_x.keys()[0]])
    xres = (xmax-xmin)/float(ncols)
    yres = (ymax-ymin)/float(nrows)
    geotransform = (xmin,xres,0,ymax,0,-yres)
    for kcum in dict_x.keys():
        endd = date.fromordinal(kcum)
        if len(str(endd.day))==1:
            end_day = '0%s' %str(endd.day)
        else:
            end_day = str(endd.day)
        if len(str(endd.month))==1:
            end_month = '0%s' %str(endd.month)
        else:
            end_month = str(endd.month)
        end_date = '%s%s%s' %(endd.year,end_month,end_day)
        filename = r'%s/Trmm3B42_%s_%s.tif' % (folder,name,end_date)
        outDataset = driver.Create(filename,ncols,nrows,1,gdal.GDT_Float32)
        outDataset.SetGeoTransform(geotransform)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        outDataset.SetProjection(srs.ExportToWkt())
        nband = 1
        array = np.empty([nrows,ncols])
        array = dict_x[kcum]
        array[np.isnan(array)] = -99
        array[np.isinf(array)] = -99
        outband = outDataset.GetRasterBand(nband)
        outband.SetNoDataValue(-99)
        outband.WriteArray(array)
        outband.GetStatistics(0,1)
        outband = None
        outDataset = None