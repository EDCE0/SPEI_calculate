# ============================================================
# correct daily SPEI-90 calculation script
# Methodology:
# 1. Daily P and T -> PET (Thornthwaite, daily)
# 2. Water balance D = P - PET
# 3. 90-day rolling accumulation of D
# 4. For each grid & each DOY, fit Log-logistic distribution
# 5. Transform to standardized SPEI
# ============================================================

import numpy as np
from netCDF4 import Dataset
from osgeo import gdal, gdalconst
from scipy.stats import fisk  # log-logistic
from datetime import datetime, timedelta
import os
import gc

# -------------------------
# Helper functions
# -------------------------

def thornthwaite_pet(temp, lat, dates):
    """Daily Thornthwaite PET (mm/day)"""
    pet = np.full_like(temp, np.nan, dtype=np.float32)
    lat_rad = np.deg2rad(lat)

    # Monthly heat index I
    monthly_temp = {}
    for t, d in zip(temp, dates):
        if np.isnan(t):
            continue
        key = (d.year, d.month)
        monthly_temp.setdefault(key, []).append(t)

    Tm = {k: np.mean(v) for k, v in monthly_temp.items()}
    I = sum((np.maximum(0, T) / 5) ** 1.514 for T in Tm.values())
    a = (6.75e-7 * I ** 3) - (7.71e-5 * I ** 2) + (1.792e-2 * I) + 0.49239

    for i, d in enumerate(dates):
        T = temp[i]
        if np.isnan(T) or T <= 0:
            pet[i] = 0
            continue
        # day length factor
        delta = 0.409 * np.sin(2 * np.pi * d.timetuple().tm_yday / 365 - 1.39)
        ws = np.arccos(-np.tan(lat_rad) * np.tan(delta))
        daylen = 24 / np.pi * ws
        pet[i] = 16 * (daylen / 12) * (10 * T / I) ** a / d.replace(day=28).day
    return pet


def rolling_sum(x, window=90):
    out = np.full_like(x, np.nan, dtype=np.float32)
    for i in range(window - 1, len(x)):
        out[i] = np.nansum(x[i - window + 1:i + 1])
    return out


def spei_from_balance(balance, dates):
    """Compute daily SPEI using DOY-wise log-logistic fitting"""
    spei = np.full_like(balance, np.nan, dtype=np.float32)
    for doy in range(1, 367):
        idx = [i for i, d in enumerate(dates) if d.timetuple().tm_yday == doy]
        vals = balance[idx]
        vals = vals[~np.isnan(vals)]
        if len(vals) < 30:
            continue
        c, loc, scale = fisk.fit(vals)
        for i in idx:
            if not np.isnan(balance[i]):
                p = fisk.cdf(balance[i], c, loc, scale)
                spei[i] = np.clip(np.sqrt(2) * erfinv(2 * p - 1), -3, 3)
    return spei

# -------------------------
# Main workflow
# -------------------------

class DailySPEI90:
    def __init__(self, start_year, end_year):
        self.start_year = start_year
        self.end_year = end_year
        self.outdir = "SPEI90_daily_correct"
        os.makedirs(self.outdir, exist_ok=True)

    def run(self, pr_path, tmp_path, ref_tif):
        # read data
        with Dataset(pr_path) as ds:
            pr = ds.variables['pre'][:].astype(np.float32)
            lats = ds.variables['lat'][:]
            lons = ds.variables['lon'][:]
        with Dataset(tmp_path) as ds:
            tmp = ds.variables['tmp'][:].astype(np.float32)

        nt, nlat, nlon = pr.shape
        dates = [datetime(self.start_year, 1, 1) + timedelta(days=i) for i in range(nt)]

        spei_all = np.full((nt, nlat, nlon), np.nan, dtype=np.float32)

        for i in range(nlat):
            lat = lats[i]
            for j in range(nlon):
                p = pr[:, i, j]
                t = tmp[:, i, j]
                if np.all(np.isnan(p)):
                    continue
                pet = thornthwaite_pet(t, lat, dates)
                balance = rolling_sum(p - pet, 90)
                spei_all[:, i, j] = spei_from_balance(balance, dates)
            gc.collect()

        # output daily GeoTIFF
        ref = gdal.Open(ref_tif)
        gt = ref.GetGeoTransform()
        proj = ref.GetProjection()
        driver = gdal.GetDriverByName('GTiff')

        for i, d in enumerate(dates):
            fn = f"SPEI90_{d.year}_{d.timetuple().tm_yday:03d}.tif"
            ds = driver.Create(os.path.join(self.outdir, fn), nlon, nlat, 1, gdal.GDT_Float32)
            ds.SetGeoTransform(gt)
            ds.SetProjection(proj)
            arr = np.where(np.isnan(spei_all[i]), -9999, spei_all[i])
            band = ds.GetRasterBand(1)
            band.WriteArray(arr)
            band.SetNoDataValue(-9999)
            ds = None

# -------------------------
# Run
# -------------------------

if __name__ == '__main__':
    DailySPEI90(1990, 2021).run(
        pr_path=r'H:/precipitation/PreDaily/pre_1990_2021.nc',
        tmp_path=r'H:/precipitation/PreDaily/tmp_1990_2021.nc',
        ref_tif=r'H:/precipitation/etp.tif'
    )
