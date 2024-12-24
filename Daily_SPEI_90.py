import numpy as np
from netCDF4 import Dataset
from osgeo import gdal, gdalconst
import climate_indices.indices as indices
import climate_indices.compute as compute
import os
from datetime import datetime
import gc

def read_netcdf(file_path, var_name):
    """读取NetCDF文件并返回数据"""
    try:
        with Dataset(file_path, mode='r') as fh:
            fh.set_auto_mask(False)
            data = fh.variables[var_name][:]
            if var_name == 'pre':
                undef = fh.variables[var_name].missing_value
                lons = fh.variables['lon'][:]
                lats = fh.variables['lat'][:]
                return data, undef, lons, lats
            return data
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
        raise

def read_geotiff_info(img_path):
    """读取参考影像的地理信息"""
    try:
        dataset = gdal.Open(img_path, gdalconst.GA_ReadOnly)
        if dataset is None:
            raise ValueError(f"Unable to open {img_path}")
        
        geotransform = dataset.GetGeoTransform()
        projection = dataset.GetProjection()
        
        return geotransform, projection
    except Exception as e:
        print(f"Error reading geotiff info: {str(e)}")
        raise
    finally:
        dataset = None

def save_tiff(data, save_path, geotransform, projection):
    """保存为TIFF文件"""
    try:
        driver = gdal.GetDriverByName("GTiff")
        rows, cols = data.shape
        dataset = driver.Create(save_path, cols, rows, 1, gdal.GDT_Float32)
        
        dataset.SetGeoTransform(geotransform)
        dataset.SetProjection(projection)
        
        band = dataset.GetRasterBand(1)
        band.WriteArray(data)
        band.SetNoDataValue(-9999)
        
        dataset.FlushCache()
    except Exception as e:
        print(f"Error saving tiff {save_path}: {str(e)}")
        raise
    finally:
        dataset = None

def calculate_spei(precip, pet, nrun, start_year, end_year):
    """计算SPEI指数"""
    try:
        
        return indices.spei(
            precips_mm=precip,
            pet_mm=pet,
            scale=nrun,
            distribution=indices.Distribution.gamma,
            periodicity=compute.Periodicity.daily,  # 调整为daily尺度
            data_start_year=start_year,
            calibration_year_initial=start_year,
            calibration_year_final=end_year
        )
    except Exception as e:
        print(f"Error calculating SPEI: {str(e)}")
        return np.full_like(precip, np.nan)

def main():
    # 参数设置
    start_year = 1960
    end_year = 2025
    nrun = 90  # SPEI-90，表示3天的尺度
    output_dir = "spei_output"
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 读取数据
    print("Reading input data...")
    prcp, undef, lons, lats = read_netcdf(r'H:\precipitation\PreDaily\precipitation_1960_2025.nc', 'pre')  # 使用每日数据
    tmp = read_netcdf(r'H:\precipitation\PreDaily\tmp_1960_2025.nc', 'tmp')  # 使用每日数据

    # 创建掩膜
    mask = (prcp == undef)
    prcp = np.ma.MaskedArray(prcp, mask=mask).astype(np.float64)
    tmp = np.ma.MaskedArray(tmp, mask=mask).astype(np.float64)

    # 获取维度
    nt, nlat, nlon = prcp.shape
    print(f"Data shape: {prcp.shape}")

    # 读取地理信息
    geotransform, projection = read_geotiff_info(r'H:\precipitation\etp.tif')

    # 计算SPEI
    print("Calculating SPEI...")
    spei = np.zeros((nt, nlat, nlon), dtype=np.float32)
    spei.fill(np.nan)

    for ilat in range(nlat):
        if ilat % 10 == 0:
            print(f"Processing latitude {ilat}/{nlat}")
        for ilon in range(nlon):
            if not mask[:, ilat, ilon].all():  # 只处理非完全掩膜的像素
                spei[:, ilat, ilon] = calculate_spei(
                    prcp[:, ilat, ilon],
                    tmp[:, ilat, ilon],
                    nrun,
                    start_year,
                    end_year
                )

    # 清理内存
    del prcp, tmp
    gc.collect()

    # 保存结果
    print("Saving results...")
    for i in range(nt):
        date = datetime(start_year, 1, 1) + timedelta(days=i)
        year = date.year
        month = date.month
        day = date.day
        save_path = os.path.join(output_dir, f"spei{nrun}-{year}-{month:02d}-{day:02d}.tif")
        save_tiff(spei[i], save_path, geotransform, projection)

        if i % 365 == 0:
            print(f"Saved year {year}")

    print("Processing completed successfully!")

if __name__ == "__main__":
    start_time = datetime.now()
    try:
        main()
    except Exception as e:
        print(f"Error in main execution: {str(e)}")
    finally:
        end_time = datetime.now()
        print(f"Total processing time: {end_time - start_time}")
