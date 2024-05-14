# -*- coding: utf-8 -*-
"""
Property of the European Space Agency (ESA-ESRIN) - contact: clement.albinet@esa.int / nuno.miranda@esa.int
Developed for Python 3.5.1 and GDAL 2.0.2
Date  -  Version  -  Author(s)  -  List of changes
17/05/2016 - V1.0 - Clement Albinet - First version of the code.
01/02/2017 - V1.1 - Clement Albinet - Projectors now work with multi-bands files.
14/04/2017 - V1.2 - Clement Albinet - Update of GrdToSlrProj to work with GDAL instead of numpy (~40 times faster).
06,08/2021 - V2.0 - Clement Albinet - Update of both projectors to deal with new lut files.
"""
########## ########## ORCHESTRATOR OF THE BIOMASS ALGORITHM TEST BED ########## ########## 

from osgeo import gdal
import numpy as np

##########################################################################################
def SlrToGrdProj(slrFile, grdFile, lutFile):
    'Projection of an image from Slant Range geometry to Ground Projected geometry'
    # Open original image in slant range geometry:
    slr_image_driver = gdal.Open(slrFile, 0)
    slr_image = slr_image_driver.ReadAsArray(0,0,1,1)
    
    # Open LUT file and read Azimuth and Range coordinates:
    lut_driver = gdal.Open(lutFile, 0)
    Azimuth = lut_driver.GetRasterBand(1).ReadAsArray()
    Range = lut_driver.GetRasterBand(2).ReadAsArray()  
    
    # Mask of the data inside the GRD projected image:
    mask = np.logical_and(Range!=55537, Azimuth!=55537)
    
    # Create an empty image of NaN:
    grd_image = np.full((lut_driver.RasterYSize, lut_driver.RasterXSize), np.NaN, dtype=slr_image.dtype)
    
    # Create the image in the ground projected geometry:
    outdriver = gdal.GetDriverByName('GTiff')
    grd_image_driver = outdriver.Create(grdFile, lut_driver.RasterXSize, lut_driver.RasterYSize, slr_image_driver.RasterCount, slr_image_driver.GetRasterBand(1).DataType)
    grd_image_driver.SetGeoTransform(lut_driver.GetGeoTransform())
    grd_image_driver.SetProjection(lut_driver.GetProjection())
    
    for band in range(slr_image_driver.RasterCount):
        # Read original image in slant range geometry:
        slr_image = slr_image_driver.GetRasterBand(band+1).ReadAsArray()
        
        # Project the image in the ground projected geometry:
        grd_image[mask] = slr_image[Azimuth[mask], Range[mask]]
        
        # Save the corresponding band of the image in the ground projected geometry:
        grd_image_driver.GetRasterBand(band+1).WriteArray(grd_image)
    
    # Close data sets:
    slr_image_driver = None
    lut_driver = None
    grd_image_driver = None

##########################################################################################
def GrdToSlrProj(grdFile, slrFile, lutFile, originalImageFile):
    'Projection of an image from Ground Projected geometry to Slant Range geometry'
    'Remark: Computation can need a long time'
    from osgeo import gdal
    from gdalconst import GA_ReadOnly
    
    # Open original image in slant range geometry:
    grd_image_driver = gdal.Open(grdFile, GA_ReadOnly)
    grd_image = grd_image_driver.ReadAsArray(0,0,1,1)
    
    # Open LUT file and read Azimuth and Range coordinates:
    lut_driver = gdal.Open(lutFile, 0)
    Azimuth = lut_driver.GetRasterBand(1).ReadAsArray()
    Range = lut_driver.GetRasterBand(2).ReadAsArray() 
    
    # Open original image file:
    original_driver = gdal.Open(originalImageFile, GA_ReadOnly)
    
    # Mask of the data inside the GRD projected image:
    mask = np.logical_and(Range!=55537, Azimuth!=55537)
    
    # Create the image in the slant range geometry:
    outdriver = gdal.GetDriverByName('GTiff')
    slr_image_driver = outdriver.Create(slrFile, original_driver.RasterXSize, original_driver.RasterYSize, grd_image_driver.RasterCount, grd_image_driver.GetRasterBand(1).DataType)
    
    for band in range(grd_image_driver.RasterCount):
        # Read original image in slant range geometry:
        grd_image = grd_image_driver.GetRasterBand(band+1).ReadAsArray()
        
        # Create an empty image of NaN:
        slr_image = np.full((original_driver.RasterYSize, original_driver.RasterXSize), np.NaN, dtype=grd_image.dtype)
        
        # Project the image in the slant range geometry:
        slr_image[Azimuth[mask], Range[mask]] = grd_image[mask]
        
        # Save the corresponding band of the image in the ground projected geometry:
        slrBand = slr_image_driver.GetRasterBand(band+1)
        slrBand.WriteArray(slr_image)
        slrBand.FlushCache()
        
        # Get NaN values to interpolate
        maskNaN = ~np.isnan(slr_image)
        
        # Create and fill a dataset with NaN values previously obtained:
        mask_driver = gdal.GetDriverByName('MEM').Create('', original_driver.RasterXSize, original_driver.RasterYSize, grd_image_driver.RasterCount, grd_image_driver.GetRasterBand(1).DataType)
        maskBand = mask_driver.GetRasterBand(1)
        maskBand.WriteArray(maskNaN)
        maskBand.FlushCache()
        
        # Interpolate missing values:
        gdal.FillNodata(targetBand = slrBand, maskBand = maskBand, maxSearchDist = 5, smoothingIterations = 0)
        
        # Close temporary NaN mask dataset:
        mask_driver = None
    
    # Close data sets:
    grd_image_driver = None
    lut_driver = None
    original_driver = None
    slr_image_driver = None


##########################################################################################
if (__name__ == '__main__'):
    
    # Test projection Slant-Range to Ground-Range:
    slrFile = '/projects/s3-drive/catalog-data/Campaign_data/afrisar_dlr/afrisar_dlr_T2-0_SLC_HV.tiff'
    grdFile = '/projects/biomass_GR.tiff'
    lutFile = '/projects/s3-drive/catalog-data/Campaign_data/afrisar_dlr/afrisar_dlr_T2-0_lut.tiff'

    SlrToGrdProj(slrFile, grdFile, lutFile)
    

    # Test projection Ground-Range to Slant-Range:
    grdFile2 = '/projects/s3-drive/catalog-data/Campaign_data/afrisar_dlr/afrisar_dlr_dem_S_T2-0.tiff'
    slrFile2 = '/projects/demSR.tiff'
    slrRefFile = '/projects/s3-drive/catalog-data/Campaign_data/afrisar_dlr/afrisar_dlr_T2-0_SLC_HV.tiff'
    
    GrdToSlrProj(grdFile2, slrFile2, lutFile, slrRefFile)
    
    print(' - Fin -')
