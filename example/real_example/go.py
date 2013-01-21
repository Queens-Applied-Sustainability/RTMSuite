import rtms

CONFIG_FILE = open('config.yaml')
DATA_FILE = open('time-series.csv')


print "importing configuration..."
site_info, csv_map, run_config = rtms.importer.config(CONFIG_FILE)


print "importing data..."
time_series_in = rtms.importer.data(DATA_FILE, csv_map)


print "selecting clear days..."
selector = rtms.Selector(site_info['latitude'], site_info['longitude'])
time_irrad_clear = selector.select(time_series_in[['time', 'irradiance']])


