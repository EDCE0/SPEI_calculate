import numpy as np
from netCDF4 import Dataset
from osgeo import gdal, gdalconst
import climate_indices.indices as indices
import climate_indices.compute as compute
import os
from datetime import datetime, timedelta
import gc

class SPEICalculator:
    def __init__(self, start_year, end_year, spei_scale):
        self.start_year = start_year
        self.end_year = end_year
        self.spei_scale = spei_scale
        self.output_dir = f"SPEI{spei_scale}_output"
        os.makedirs(self.output_dir, exist_ok=True)

    def read_netcdf(self, file_path, var_name):
        """读取NetCDF文件数据"""
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

    def calculate_pet(self, temperature, latitude, start_year):
        """计算潜在蒸散发"""
        try:
            return indices.pet(
                temperature_celsius=temperature,
                latitude_degrees=latitude,
                data_start_year=start_year
            )
        except Exception as e:
            print(f"Error calculating PET: {str(e)}")
            return np.full_like(temperature, np.nan)

    def calculate_spei(self, precip, pet):
        """计算SPEI指数"""
        try:
            return indices.spei(
                precips_mm=precip,
                pet_mm=pet,
                scale=self.spei_scale,
                distribution=indices.Distribution.gamma,
                periodicity=compute.Periodicity.daily,
                data_start_year=self.start_year,
                calibration_year_initial=self.start_year,
                calibration_year_final=self.end_year
            )
        except Exception as e:
            print(f"Error calculating SPEI: {str(e)}")
            return np.full_like(precip, np.nan)

    def save_geotiff(self, data, filename, geotransform, projection):
        """保存为GeoTIFF格式"""
        try:
            driver = gdal.GetDriverByName("GTiff")
            filepath = os.path.join(self.output_dir, filename)
            dataset = driver.Create(filepath, data.shape[1], data.shape[0], 
                                  1, gdal.GDT_Float32)
            
            dataset.SetGeoTransform(geotransform)
            dataset.SetProjection(projection)
            
            band = dataset.GetRasterBand(1)
            band.WriteArray(data)
            band.SetNoDataValue(-9999)
            
            dataset.FlushCache()
        except Exception as e:
            print(f"Error saving {filename}: {str(e)}")
        finally:
            dataset = None

    def process(self):
        print(f"Starting SPEI-{self.spei_scale} calculation...")
        start_time = datetime.now()

        # 读取数据
        prcp, undef, lons, lats = self.read_netcdf(
            r'H:\precipitation\PreDaily\pre_1990_2021.nc', 'pre')
        tmp = self.read_netcdf(r'H:\precipitation\PreDaily\tmp_1990_2021.nc', 'tmp')

        # 掩膜处理
        mask = (prcp == undef)
        prcp = np.ma.MaskedArray(prcp, mask=mask).astype(np.float32)
        tmp = np.ma.MaskedArray(tmp, mask=mask).astype(np.float32)

        nt, nlat, nlon = prcp.shape
        print(f"Data loaded. Shape: {prcp.shape}")

        # 读取地理信息
        geotransform, projection = self.read_geotiff_info(r'H:\precipitation\etp.tif')

        # 按批次处理数据
        batch_size = 100  # 每次处理100个纬度点
        for batch_start in range(0, nlat, batch_size):
            batch_end = min(batch_start + batch_size, nlat)
            print(f"Processing latitudes {batch_start} to {batch_end}")

            spei_batch = np.full((nt, batch_end - batch_start, nlon), np.nan)

            for i, ilat in enumerate(range(batch_start, batch_end)):
                lat = lats[ilat]
                for ilon in range(nlon):
                    if not mask[:, ilat, ilon].all():
                        # 计算PET
                        pet = self.calculate_pet(
                            tmp[:, ilat, ilon],
                            lat,
                            self.start_year
                        )
                        
                        # 计算SPEI
                        spei_batch[:, i, ilon] = self.calculate_spei(
                            prcp[:, ilat, ilon],
                            pet
                        )

            # 保存每天的结果
            for day in range(nt):
                year = self.start_year + day // 365
                day_of_year = (day % 365) + 1
                
                filename = f"spei{self.spei_scale}_{year}_{day_of_year:03d}.tif"
                self.save_geotiff(
                    spei_batch[day],
                    filename,
                    geotransform,
                    projection
                )

            # 清理内存
            gc.collect()

        end_time = datetime.now()
        print(f"Processing completed in {end_time - start_time}")

    def read_geotiff_info(self, filepath):
        """读取参考影像的地理信息"""
        try:
            dataset = gdal.Open(filepath, gdalconst.GA_ReadOnly)
            if dataset is None:
                raise ValueError(f"Unable to open {filepath}")
            
            geotransform = dataset.GetGeoTransform()
            projection = dataset.GetProjection()
            
            return geotransform, projection
        except Exception as e:
            print(f"Error reading geotiff info: {str(e)}")
            raise
        finally:
            dataset = None

if __name__ == "__main__":
    calculator = SPEICalculator(
        start_year=1990,
        end_year=2021,
        spei_scale=90
    )
    calculator.process()
