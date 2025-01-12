import xarray as xr
import numpy as np
import pandas as pd

def detect_annual_events(data, threshold, duration_threshold):
    """   
    Parameters:
    - data: xarray DataArray
    - threshold:
    - duration_threshold: 
    - min_gap:     
    Returns:
    """
    data = data.assign_coords(time=pd.to_datetime(data.time.values))
    

    years = data.time.dt.year.values
    unique_years = np.unique(years)
    coords = {
        'year': unique_years,
        'latitude': data.latitude,
        'longitude': data.longitude
    }
    
    annual_stats = xr.Dataset({
        var: xr.DataArray(
            np.zeros((len(unique_years), len(data.latitude), len(data.longitude)), dtype=float),
            coords=coords, 
            dims=['year', 'latitude', 'longitude']
        ) for var in ['average_duration', 'average_severity', 'frequency', 'maximum_duration', 'total_severity','longest_event_start_day', 'longest_event_end_day']
    })
    
   
    for year_idx, year in enumerate(unique_years):

        year_data = data.sel(time=data.time.dt.year == year)
        
 
        for lat_idx in range(len(data.latitude)):
            for lon_idx in range(len(data.longitude)):
                grid_data = year_data[:, lat_idx, lon_idx].values
                

                events = []
                current_event = []
                
                for i, value in enumerate(grid_data):
                    if value > threshold:
                        current_event.append((i, value))
                    else:
                    
                        if len(current_event) > duration_threshold:
                            events.append(current_event)
                        current_event = []
                

                if current_event and len(current_event) > duration_threshold:
                    events.append(current_event)
                

                if events:

                    durations = [len(event) for event in events]
                    

                    severities = [sum(value - threshold for _, value in event) for event in events]
                    total_duration = sum(durations)
                    num_events = len(events)
                    longest_event_idx = np.argmax(durations)
                    longest_event = events[longest_event_idx]
                    

                    annual_stats['average_duration'][year_idx, lat_idx, lon_idx] = total_duration / num_events
                    annual_stats['average_severity'][year_idx, lat_idx, lon_idx] = np.mean([
                        sev/dur for sev, dur in zip(severities, durations)
                    ])
                    annual_stats['frequency'][year_idx, lat_idx, lon_idx] = num_events
                    annual_stats['maximum_duration'][year_idx, lat_idx, lon_idx] = max(durations)
                    annual_stats['total_severity'][year_idx, lat_idx, lon_idx] = max(severities)
                    annual_stats['longest_event_start_day'][year_idx, lat_idx, lon_idx] = longest_event[0][0]
                    annual_stats['longest_event_end_day'][year_idx, lat_idx, lon_idx] = longest_event[-1][0]
    
    return annual_stats

def detect_annual_compound_events(tmp_data, spei_data, 
                                  tmp_threshold, spei_threshold, 
                                  duration_threshold):
    """
    """

    tmp_data = tmp_data.assign_coords(time=pd.to_datetime(tmp_data.time.values))
    spei_data = spei_data.assign_coords(time=pd.to_datetime(spei_data.time.values))
    

    years = tmp_data.time.dt.year.values
    unique_years = np.unique(years)
    

    coords = {
        'year': unique_years,
        'latitude': tmp_data.latitude,
        'longitude': tmp_data.longitude
    }
    
    annual_stats = xr.Dataset({
        var: xr.DataArray(
            np.zeros((len(unique_years), len(tmp_data.latitude), len(tmp_data.longitude)), dtype=float),
            coords=coords, 
            dims=['year', 'latitude', 'longitude']
        ) for var in ['average_duration', 'average_severity', 'frequency', 'maximum_duration', 'total_severity','longest_event_start_day', 'longest_event_end_day']
    })
    

    for year_idx, year in enumerate(unique_years):

        tmp_year_data = tmp_data.sel(time=tmp_data.time.dt.year == year)
        spei_year_data = spei_data.sel(time=spei_data.time.dt.year == year)
        

        for lat_idx in range(len(tmp_data.latitude)):
            for lon_idx in range(len(tmp_data.longitude)):
                tmp_grid_data = tmp_year_data[:, lat_idx, lon_idx].values
                spei_grid_data = spei_year_data[:, lat_idx, lon_idx].values
                

                events = []
                current_event = []
                
                for i, (tmp_val, spei_val) in enumerate(zip(tmp_grid_data, spei_grid_data)):
                    if tmp_val > tmp_threshold and spei_val > spei_threshold:
                        current_event.append((i, tmp_val, spei_val))
                    else:


                        if len(current_event) > duration_threshold:
                            events.append(current_event)
                        current_event = []
                

                if current_event and len(current_event) > duration_threshold:
                    events.append(current_event)
                

                if events:

                    durations = [len(event) for event in events]
                    
                    severities = [
                        np.sum([np.sqrt((tmp_val - tmp_threshold)**2 + (np.abs(spei_val - spei_threshold))**2) for _, tmp_val, spei_val in event])
                        #np.sum(np.sqrt((tmp_val- tmp_threshold)**2 + (np.abs(spei_val-spei_threshold))**2) for _, tmp_val, spei_val in event) #Sum Euclidean distance over days in the event
                        for event in events
                    ]
                    total_duration = sum(durations)
                    num_events = len(events)
                    
                    longest_event_idx = np.argmax(durations)
                    longest_event = events[longest_event_idx]
                    
                    
                    annual_stats['average_duration'][year_idx, lat_idx, lon_idx] = total_duration / num_events
                    annual_stats['average_severity'][year_idx, lat_idx, lon_idx] = np.mean([
                        sev/dur for sev, dur in zip(severities, durations)
                    ])
                    annual_stats['frequency'][year_idx, lat_idx, lon_idx] = num_events
                    annual_stats['maximum_duration'][year_idx, lat_idx, lon_idx] = max(durations)
                    annual_stats['total_severity'][year_idx, lat_idx, lon_idx] = max(severities)
                    annual_stats['longest_event_start_day'][year_idx, lat_idx, lon_idx] = longest_event[0][0]
                    annual_stats['longest_event_end_day'][year_idx, lat_idx, lon_idx] = longest_event[-1][0]
    
    return annual_stats

def main():
    try:
        tmp_data = xr.open_dataset('/home/Colm2014/process/Daymax_1961.nc')['t2m']
        spei_data = xr.open_dataset('/home/Colm2014/process/SPEI90_1961.nc')['spei'] # SPEI*-1---> -SPEI
        spei_data = spei_data.rename({'lon': 'longitude'})
        spei_data = spei_data.rename({'lat': 'latitude'})
    except (FileNotFoundError, KeyError) as e:
        print(f"Error loading data: {e}")
        return

    tmp_data['time'] = pd.to_datetime(tmp_data.time.values)
    print(tmp_data['time'])
    spei_data['time'] = pd.to_datetime(spei_data.time.values)
    print(spei_data['time'])

    min_gap = 2
    start_year = tmp_data.time.dt.year.min().values
    end_year = tmp_data.time.dt.year.max().values

    heatwave_annual_stats = detect_annual_events(
        tmp_data, 
        threshold=32, 
        duration_threshold=3, 
        min_gap=min_gap
    )
    
    for year in heatwave_annual_stats.year.values:
        heatwave_year_stats = heatwave_annual_stats.sel(year=year)
        filename = f'heatwave2_annual_stats_{year}.nc'
        heatwave_year_stats.to_netcdf(filename)
    
    drought_annual_stats = detect_annual_events(
        spei_data, 
        threshold=1, 
        duration_threshold=3, 
        min_gap=min_gap
    )
    
    for year in drought_annual_stats.year.values:
        drought_year_stats = drought_annual_stats.sel(year=year)
        filename = f'drought2_annual_stats_{year}.nc'
        drought_year_stats.to_netcdf(filename)
    
    compound_annual_stats = detect_annual_compound_events(
        tmp_data, 
        spei_data, 
        tmp_threshold=32, 
        spei_threshold=1, 
        duration_threshold=3,
        min_gap=min_gap
    )

    for year in compound_annual_stats.year.values:
        compound_year_stats = compound_annual_stats.sel(year=year)
        filename = f'compound2_annual_stats_{year}.nc'
        compound_year_stats.to_netcdf(filename)

if __name__ == '__main__':
    main()