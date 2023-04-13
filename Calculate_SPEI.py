import numpy as np
from netCDF4 import Dataset
from osgeo import gdal, gdalconst
import climate_indices.indices as indices
import climate_indices.compute as compute
# from climate_indices import indices
# from climate_indices import compute

pre_file = r'H:\precipitation\PreMonthy\pre_1990_2021.nc'
pre_fh = Dataset(pre_file, mode='r') # file handle, open in read only mode
pre_fh.set_auto_mask(False)
lons = pre_fh.variables['lon'][:]
lats = pre_fh.variables['lat'][:]
nctime = pre_fh.variables['time'][:]
t_unit = pre_fh.variables['time'].units
prcp = pre_fh.variables['pre'][:]
#  undef = 9.96921E36
undef = pre_fh.variables['pre'].missing_value

pre_fh.close() # close the file

mask = (prcp==undef)
prcp = np.ma.MaskedArray(prcp, mask=mask)
prcp = prcp.astype(np.float64)
print(prcp.shape)
nt,nlat,nlon = prcp.shape

pet_file = r'H:\precipitation\PreMonthy\pet_1990_2021.nc'
pet_fh = Dataset(pet_file, mode='r') # file handle, open in read only mode
pet_fh.set_auto_mask(False)
pet = pet_fh.variables['etp'][:]
pet_fh.close()

pet = np.ma.MaskedArray(pet, mask=mask)
pet = pet.astype(np.float64)
print(pet.shape)



spei = np.zeros(pet.shape)
spei[:,:,:] = np.nan
nrun = 12

for ilat in np.arange(nlat):
    lat = lats[ilat]
    for ilon in np.arange(nlon):
        one_pr = prcp[:, ilat, ilon]
        one_pet = pet[:, ilat, ilon]
        spei[:, ilat, ilon] = indices.spei(precips_mm=one_pr,
                                           pet_mm=one_pet,
                                           scale=nrun,
                                           distribution=indices.Distribution.gamma,
                                           periodicity=compute.Periodicity.monthly,
                                           data_start_year=1990,
                                           calibration_year_initial=1990,
                                           calibration_year_final=2021,
                                           )


#pet = np.ma.MaskedArray(pet, mask=mask)
spei = np.ma.MaskedArray(spei, mask=mask)
del pet,prcp

# print(spei.shape)
time_spei,latt,long= spei.shape

print(time_spei)
def read_img(img_path):
    dataset = gdal.Open(img_path, gdalconst.GA_ReadOnly)

    adf_GeoTransform = dataset.GetGeoTransform()
    im_Proj = dataset.GetProjection()


    del dataset
    return adf_GeoTransform, im_Proj

adf_GeoTransform,im_Proj=read_img(r'H:\precipitation\etp.tif')

for i in range(time_spei):
    # 保存为TIF格式
    driver = gdal.GetDriverByName("GTiff")
    year = 1990 + int(i/12)
    season = i%12
    r = season + 1
    save_path = "spei12-" + str(year)+"-"+str(r)+".tif"
    datasetnew = driver.Create(save_path, long, latt, 1, gdal.GDT_Float32)
    datasetnew.SetGeoTransform(adf_GeoTransform)
    datasetnew.SetProjection(im_Proj)
    band = datasetnew.GetRasterBand(1)
    band.WriteArray(spei[i,:,:])
    datasetnew.FlushCache()  # Write to disk.必须有清除缓存

# for i in range()
# spei.dump('spei')
# for i in range()
