# -*- coding: utf-8 -*-
"""
Property of the European Space Agency (ESA-ESRIN) - contact: clement.albinet@esa.int / nuno.miranda@esa.int
Developed for Python 3.5.1 and GDAL 2.0.2
Date  -  Version  -  Author(s)  -  List of changes
17/05/2016 - V1.0 - Clement Albinet - First version of the code.
27/01/2016 - V1.1 - Clement Albinet - Correction of the bug that was happening when a ROI was outside the image.
13/02/2017 - V1.2 - Clement Albinet - statistics and plot functions added, Trendline added.
16/03/2017 - V1.3 - Clement Albinet - Matchup figure name changed to matchup (instead of stat).
04/04/2017 - V1.4 - Clement Albinet - Dynamic increased of max values for the matchup figure and Lat Long axis in meters for the quicklook.
20/04/2017 - V1.4 - Clement Albinet - "count" output parameter (nb of values inside ROI) added to "getRoiStats".
23/08/2017 - V1.5 - Clement Albinet - Solved bug of X and Y for QL, default location of legend now set at "best" for "plotFig" and "traceRoiStats".
13/08/2018 - V2.0 - Clement Albinet - stats function updated to deals with NaN, traceRoiStats simplified, plotFig improved.
06/08/2021 - V2.1 - Clement Albinet - stats function updated with new covariance computation.
"""
########## ########## ORCHESTRATOR OF THE BIOMASS ALGORITHM TEST BED ########## ##########

from osgeo import gdal, ogr, osr
from gdalconst import GA_ReadOnly
#import localParameters

##########################################################################################
def getRoiStats(imageFilename, shapeFolderPrefix, rois):
    'Computation of the mean, min, max and std of an image above the corresponding ROIs'
    import numpy as np
    import warnings
    
    # Open image file (reading only):
    image_driver = gdal.Open(imageFilename, GA_ReadOnly)
    
    # Get raster georeference info:
    transform = image_driver.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = transform[5]
    
    # Initialise dictionnary of results:
    stats = {'mean':[], 'min':[], 'max':[], 'std':[], 'count':[]}
    
    # Loop on ROIs:
    for roi in rois:
        
        # Open shape file (reading only):
        shape_driver = ogr.GetDriverByName("ESRI Shapefile")
        shape = shape_driver.Open(shapeFolderPrefix + roi + '.shp', GA_ReadOnly)
        layer = shape.GetLayer()
        
        # Get feature:
        feature = layer.GetFeature(0)
        
        # Reproject vector geometry to same projection as raster:
        sourceSR = layer.GetSpatialRef()
        targetSR = osr.SpatialReference()
        targetSR.ImportFromWkt(image_driver.GetProjectionRef())
        coordTrans = osr.CoordinateTransformation(sourceSR,targetSR)
        geom = feature.GetGeometryRef()
        geom.Transform(coordTrans)
        
        # Get extent of feature:
        geom = feature.GetGeometryRef()
        
        # Process points of the polygon:
        ring = geom.GetGeometryRef(0)
        numpoints = ring.GetPointCount()
        pointsX = []; pointsY = []
        for p in range(numpoints):
            lon, lat, z = ring.GetPoint(p)
            pointsX.append(lon)
            pointsY.append(lat)
        
        # Get extents:
        xmin = min(pointsX)
        xmax = max(pointsX)
        ymin = min(pointsY)
        ymax = max(pointsY)
        
        # Specify offset and rows and columns to read:
        xoff = int((xmin - xOrigin)/pixelWidth)
        yoff = int((yOrigin - ymax)/pixelWidth)
        xcount = int((xmax - xmin)/pixelWidth)+1
        ycount = int((ymax - ymin)/pixelWidth)+1
        
        # Compute stats if ROI in image:
        if xoff < 0 or yoff < 0 or xoff+xcount > image_driver.RasterXSize or yoff+ycount > image_driver.RasterYSize:
            stats['mean'].append(np.NaN)
            stats['min'].append(np.NaN)
            stats['max'].append(np.NaN)
            stats['std'].append(np.NaN)
            stats['count'].append(np.NaN)
        else:
            # Create memory target raster
            target_ds = gdal.GetDriverByName('MEM').Create('', xcount, ycount, 1, gdal.GDT_Byte)
    #        target_ds = gdal.GetDriverByName('GTiff').Create(roi+'.tiff', xcount, ycount, 1, gdal.GDT_Byte) # For debugging
            target_ds.SetGeoTransform((xmin, pixelWidth, 0, ymax, 0, pixelHeight))
            
            # Create for target raster the same projection as for the value raster:
            raster_srs = osr.SpatialReference()
            raster_srs.ImportFromWkt(image_driver.GetProjectionRef())
            target_ds.SetProjection(raster_srs.ExportToWkt())
            
            # Rasterize zone polygon to raster:
            gdal.RasterizeLayer(target_ds, [1], layer, burn_values=[1])
            
            # Read raster as arrays:
            banddataraster = image_driver.GetRasterBand(1)
            dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(np.float)
            
            # Create mask:
            bandmask = target_ds.GetRasterBand(1)
            datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(np.float)
            
            # Mask zone of raster:
            zoneraster = np.ma.masked_array(dataraster, np.logical_not(datamask))
            
            # Calculate statistics of zonal raster:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', category=RuntimeWarning)
                stats['mean'].append(np.nanmean(zoneraster))
                stats['min'].append(np.nanmin(zoneraster))
                stats['max'].append(np.nanmax(zoneraster))
                stats['std'].append(np.nanstd(zoneraster))
                stats['count'].append(zoneraster.count())
        
        # Close data sets:
        shape_driver = None
        target_ds = None
    
    # Close image data set:
    image_driver = None
    
    # Return results:
    return stats
    
##########################################################################################
def stats(measuredValues, estimatedValues):
    'Computation of statistics for two given lists'
    from scipy import stats
    import numpy as np
    
    estimatedValues = np.array(estimatedValues)
    measuredValues = np.array(measuredValues)
    
    # Take out NaN values:
    mask = np.isfinite(estimatedValues) & np.isfinite(measuredValues)
    estimatedValues = estimatedValues[mask]
    measuredValues = measuredValues[mask]
    
    if len(estimatedValues) > 0:
        with np.errstate(invalid='ignore'): # To avoid warnings when computations with NaN
            # Compute basic statistics:
            slope, intercept, r_value, p_value, std_err = stats.linregress(measuredValues, estimatedValues)
            
            # Compute additional statistics:
            bias = np.nanmean(estimatedValues - measuredValues)
            covariance = np.sqrt(np.nansum((estimatedValues - measuredValues - bias)**2) / (len(estimatedValues)-1))
            rmsd = np.sqrt(np.nanmean((estimatedValues - measuredValues)**2))
        
        # Return all the values:
        return [slope, intercept, r_value, p_value, std_err, bias, covariance, rmsd]
    else:
        return [np.NaN]*8

##########################################################################################
def plotFig(measuredValues, estimatedValues, figureFilename, title, Type, slope=None, intercept=None, location='best'):
    'Trace of the estimated versus measured biomass according to the given parameters'
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.lines as mlines
    
    # Define figure:
    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    
    # Trace values:
    ax.plot(measuredValues, estimatedValues, 'bo')
    
    # Trace reference line:
    if Type == 'biomass':
        maximum = (max(max(measuredValues), max(estimatedValues), 399)//200 + 1) * 200
        ax.plot([0,maximum], [0,maximum], '-k')
    if Type == 'height':
        maximum = (max(max(measuredValues), max(estimatedValues), 39)//20 + 1) * 20
        ax.plot([0,maximum], [0,maximum], '-k')
        
    if (slope != None) and (intercept != None):
        ax.plot([0, maximum], [intercept, maximum * slope + intercept], '-g')
        if location != None:
            blue_line = mlines.Line2D([], [], color='green', label='Trendline ($a$=' + str(round(slope, 2)) + ' | $b$=' + str(round(intercept, 2)) + ')')
            ax.legend(handles=[blue_line], fancybox = True, shadow = True, loc = location, prop={'size':12})
    
    # define axis:
    ax.axis([0, maximum, 0, maximum])
    
    # Set figure Layout:
    if Type == 'biomass':
        ax.set_xlabel('Ground truth biomass (ton/ha)')
        ax.set_ylabel('Estimated biomass (ton/ha)')
    if Type == 'height':
        ax.set_xlabel('Ground truth height (m)')
        ax.set_ylabel('Estimated height (m)')
    ax.set_title(title + '\n')
    ax.grid(True)
    
    # Save figure:
    canvas.print_figure(figureFilename + '_' + Type + '_matchup.' + localParameters.roiStatExtension, dpi=150, bbox_inches='tight')
    
##########################################################################################
def traceRoiStats(imageFilename, shapeFolderPrefix, rois, values, figureFilename, Type):
    'Trace of the estimated versus measured biomass for the corresponding ROIs'
#    import math
    
    # Get ROIs measured biomasses:
    measuredValues = [values[roi] for roi in rois]
    
    # Get ROIs estimated values:
    estimatedValues = getRoiStats(imageFilename, shapeFolderPrefix, rois)['mean']
    
    # If there are values to plot only:
    if len(estimatedValues) > 0:
        import os
        
        # Define basic title:
        title = os.path.basename(figureFilename)
        
        if len(estimatedValues) > 2:
            [slope, intercept, r_value, p_value, std_err, bias, variance, rmsd] = stats(measuredValues, estimatedValues)
            title += ' (' + '$r^2$=' + str(round(r_value**2, 2)) + ' | $RMSD$=' + str(round(rmsd, 1)) + ')'
            
            # Plot figure:
            plotFig(measuredValues, estimatedValues, figureFilename, title, Type, slope, intercept, 'best')
        else:
            plotFig(measuredValues, estimatedValues, figureFilename, title, Type, None, None, 'best')


##########################################################################################
def quickL(inputFilename, quickLookBaseFilename, GRD_resol, Type):
    'Create and save a quick look of the input image'
    import os
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.colors import LinearSegmentedColormap
    
    # Open original image in slant range geometry:
    input_image_driver = gdal.Open(inputFilename, 0)
    ratio = max(1, input_image_driver.RasterXSize // 1000, input_image_driver.RasterYSize // 1000) # Ratio of the reduction of the read image (to avoid memory errors) 
    input_image = input_image_driver.ReadAsArray(0, 0, None, None, None, input_image_driver.RasterXSize//ratio, input_image_driver.RasterYSize//ratio)
    
    # Define figure:
    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    
    # Define custom color map:
    if Type == 'biomass':
        customCmap = LinearSegmentedColormap.from_list('biomass', ['#F5F5DC', 'g', '#004500'])
    if Type == 'height':
#        customCmap = LinearSegmentedColormap.from_list('height', ['#F5F5DC', '#966F33', '#452400'])
        customCmap = 'jet'
    
    # Display image:
    cax = ax.imshow(input_image, cmap=customCmap, extent=(0, input_image_driver.RasterXSize*GRD_resol, 0, input_image_driver.RasterYSize*GRD_resol))
    
    # Set figure Layout:
    ax.set_xlabel('Longitude (m)')
    ax.set_ylabel('Latitude (m)')
    cbar = fig.colorbar(cax)
    if Type == 'biomass':
        cbar.set_label('Biomass (ton/ha)')
    if Type == 'height':
        cbar.set_label('Height (m)')
    ax.set_title(os.path.basename(quickLookBaseFilename) + '.tiff\n')
    
    # Save figure:
    canvas.print_figure(quickLookBaseFilename + '_' + Type + '_QL.' + localParameters.quickLookExtension, dpi=150, bbox_inches='tight')
    
    # Close image data set:
    input_image_driver = None
    
    
##########################################################################################
if (__name__ == '__main__'):
    imageFilename = r'C:\Users\Clement Albinet\Desktop\2 Biomass Algo\Test Bed Orchestrator\output_data\test_biosar1_109_biomass.tiff'
    shapeFolderPrefix = r'C:\IN\biosar1\biosar1_roi_'
    rois = ['insitu1', 'insitu5', 'insitu10', 'insitu14', 'insitu15', 'insitu17', 'insitu18', 'lidar1', 'lidar2', 'lidar3', 'lidar4', 'lidar5', 'lidar6', 'lidar7', 'lidar8', 'lidar9', 'lidar10', 'lidar11', 'lidar12', 'lidar13', 'lidar14', 'lidar15', 'lidar16', 'lidar17', 'lidar18', 'lidar19', 'lidar20', 'lidar21', 'lidar22', 'lidar23', 'lidar24', 'lidar25', 'lidar26', 'lidar27', 'lidar28', 'lidar29', 'lidar30', 'lidar31', 'lidar32', 'lidar33', 'lidar34', 'lidar35', 'lidar36', 'lidar37', 'lidar38', 'lidar39', 'lidar40', 'lidar41', 'lidar42', 'lidar43', 'lidar44', 'lidar45', 'lidar46', 'lidar47', 'lidar48', 'lidar49', 'lidar50', 'lidar51', 'lidar52', 'lidar53', 'lidar54', 'lidar55', 'lidar56', 'lidar57', 'lidar58']
#    rois = ['1474', '1493', '1517', '1812', '1892', '2228', '2269', '2625', '2626', '2629', '3245', '3611', '3614', '3628', '3689', '3715', '4035', '4038', '4115', '4451', '15096', '17637', '18147', '18278', '21577', '22838', '30097', '31818', '32398', '36169', '36979']
    
#    imageFilename = r'E:\P-Band Airborne Campaign Data\2010_BIOSAR3\LiDAR_Data\UTM33N\BioSAR_2010_Remningstorp_UTM33N_LiDARperc95.tif'
##    imageFilename = r'E:\P-Band Airborne Campaigne Data\2010_BIOSAR3\LiDAR_Data\WGS84\BioSAR_2010_Remningstorp_WGS84_LiDARperc95.tif'
#    shapeFolderPrefix = r'E:\BL2ATB Backup\IN\biosar3\biosar3_roi_'
#    rois = ['insitu1', 'insitu5', 'insitu10', 'insitu14', 'insitu15', 'insitu17', 'insitu18', 'lidar1', 'lidar2', 'lidar3', 'lidar4', 'lidar5', 'lidar6', 'lidar7', 'lidar8', 'lidar9', 'lidar10', 'lidar11', 'lidar12', 'lidar13', 'lidar14', 'lidar15', 'lidar16', 'lidar17', 'lidar18', 'lidar19', 'lidar20', 'lidar21', 'lidar22', 'lidar23', 'lidar24', 'lidar25', 'lidar26', 'lidar27', 'lidar28', 'lidar29', 'lidar30', 'lidar31', 'lidar32', 'lidar33', 'lidar34', 'lidar35', 'lidar36', 'lidar37', 'lidar38', 'lidar39', 'lidar40', 'lidar41', 'lidar42', 'lidar43', 'lidar44', 'lidar45', 'lidar46', 'lidar47', 'lidar48', 'lidar49', 'lidar50', 'lidar51', 'lidar52', 'lidar53', 'lidar54', 'lidar55', 'lidar56', 'lidar57', 'lidar58']
#    
    stats = getRoiStats(imageFilename, shapeFolderPrefix, rois)
    print(stats['mean'][0])
    print(stats['min'][0])
    print(stats['max'][0])
    print(stats['std'][0])
    print(stats['count'][0])
    
#    import numpy as np
#    print(stats([np.NaN, 5],[2, np.NaN]))
    
#    for i, val in enumerate(stats['mean']):
#        print(rois[i] + ' - ' + str(round(val/10)/10))
    
#    measuredValues = [-11.081954013444239, -18.290151256775307, -11.435651320523421, -12.322133031457362, -19.238602930361086, -10.442486842395358, -12.820638334816692, -11.187729299903221, -16.431480132163646, -12.558853942971185, -10.774031736401904, -16.461657793256972, -15.667282374903925, -9.8992338754112552, -12.644257569123569, -10.530646777197738, -13.354559926361903, -16.443491235266638, -10.533193883542438, -10.796806649532284, -21.390598748102075, -17.498017927892693, -10.545639310498306, -15.866850415349989, -13.491103943518786, -11.852564989253798, -11.410154960191225, -10.925983972372928, -11.286729493470757, -11.764303520490326, -11.630362204622395, -12.837404926498145, -11.073798804838725, -12.051331938045454, -11.711657965707639, -13.92444081695621, -10.350941101247949, -12.373550066862128, -10.195832505067905, -11.997892461870574, -13.840925629063882, -12.310124112638995, -18.961440881404393, -22.368818838639303, -12.36925308690374, -12.287310974655854, -10.950999116970879, -10.662559909469566, -17.221619568970379, -19.149419821527019, -18.332007756134377, -12.643898098092331, -11.284275884873821, -18.554091899346293, -12.321528701812216, -13.365448838062667, -12.245813351029888, -11.859663517032555, -10.328429326968596, -8.7315732044665246, -12.008752623916696, -13.370254670617296, -11.32680095662425, -12.829647993652012, -10.574976835851148]
#    estimatedValues = [209.4, 114.5, 182.8, 92.7, 123.1, 182.9, 298.4, 98.4, 175.7, 185.5, 127.9, 146.5, 237.2, 98.2, 124.6, 106.3, 138.2, 161.6, 108.0, 180.7, 158.6, 118.2, 151.8, 111.5, 9.4, 147.7, 175.6, 166.2, 239.6, 142.2, 141.7, 123.7, 144.8, 27.7, 158.4, 236.4, 149.2, 25.6, 93.3, 117.7, 118.8, 253.2, 111.8, 158.8, 53.6, 144.5, 173.0, 71.8, 18.3, 137.8, 211.2, 43.5, 96.9, 122.7, 86.7, 11.2, 108.2, 111.3, 122.6, 79.6, 95.8, 9.2, 117.3, 266.3, 121.5]
#    print(statistics(measuredValues, estimatedValues))
    
#    measuredValues = [209.4, 114.5, 182.8, 92.7, 123.1, 182.9, 298.4, 98.4, 175.7, 185.5, 127.9, 146.5, 237.2, 98.2, 124.6, 106.3, 138.2, 161.6, 108.0, 180.7, 158.6, 118.2, 151.8, 111.5, 9.4, 147.7, 175.6, 166.2, 239.6, 142.2, 141.7, 123.7, 144.8, 27.7, 158.4, 236.4, 149.2, 25.6, 93.3, 117.7, 118.8, 253.2, 111.8, 158.8, 53.6, 144.5, 173.0, 71.8, 18.3, 137.8, 211.2, 43.5, 96.9, 122.7, 86.7, 11.2, 108.2, 111.3, 122.6, 79.6, 95.8, 9.2, 117.3, 266.3, 121.5]
#    estimatedValues = [-11.081954013444239, -18.290151256775307, -11.435651320523421, -12.322133031457362, -19.238602930361086, -10.442486842395358, -12.820638334816692, -11.187729299903221, -16.431480132163646, -12.558853942971185, -10.774031736401904, -16.461657793256972, -15.667282374903925, -9.8992338754112552, -12.644257569123569, -10.530646777197738, -13.354559926361903, -16.443491235266638, -10.533193883542438, -10.796806649532284, -21.390598748102075, -17.498017927892693, -10.545639310498306, -15.866850415349989, -13.491103943518786, -11.852564989253798, -11.410154960191225, -10.925983972372928, -11.286729493470757, -11.764303520490326, -11.630362204622395, -12.837404926498145, -11.073798804838725, -12.051331938045454, -11.711657965707639, -13.92444081695621, -10.350941101247949, -12.373550066862128, -10.195832505067905, -11.997892461870574, -13.840925629063882, -12.310124112638995, -18.961440881404393, -22.368818838639303, -12.36925308690374, -12.287310974655854, -10.950999116970879, -10.662559909469566, -17.221619568970379, -19.149419821527019, -18.332007756134377, -12.643898098092331, -11.284275884873821, -18.554091899346293, -12.321528701812216, -13.365448838062667, -12.245813351029888, -11.859663517032555, -10.328429326968596, -8.7315732044665246, -12.008752623916696, -13.370254670617296, -11.32680095662425, -12.829647993652012, -10.574976835851148]
#    figureFilename = r'C:\Users\Clement Albinet\Desktop\2 Biomass Algo\Test Bed Orchestrator\test'
#    title = 'test title'
#    [slope, intercept, r_value, p_value, std_err, bias, variance, rmsd] = stats(measuredValues, estimatedValues)
#    title += ' (' + '$r^2$=' + str(round(r_value**2, 2)) + ' | $RMSD$=' + str(round(rmsd, 1)) + ')'
#    Type = 'biomass'
#    plotFig(measuredValues, estimatedValues, figureFilename, title, Type, slope, intercept, location='upper left')
    
#    import userTools
#    tools = userTools.tools()
#    figureFilename = 'test.png'
#    print(tools.biomasses)
    
#    traceRoiStats(imageFilename, shapeFolderPrefix, rois, tools.biomasses, figureFilename)
    
#    quickL('orch-example_tropisar_509.tiff', 'test')
    
    print(' - Fin -')

