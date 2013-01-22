from collections import Counter
from rtm import SMARTS
import rtms

CONFIG_FILE = open('config.yaml')
DATA_FILE = open('time-series.csv')


print "importing configuration...",
site_info, csv_map, run_config = rtms.importer.config(CONFIG_FILE)
print "done."

print "importing data...",
timeseries_in = rtms.importer.data(DATA_FILE, csv_map)
print "imported {} rows.".format(len(timeseries_in))


print "selecting clear days...",
selector = rtms.Selector(site_info['latitude'], site_info['longitude'])
time_irrad_clear = selector.select(timeseries_in[['time', 'irradiance']])
print "selected {} ({:.1%}) clear points.".format(
    *((lambda c: [c, float(c)/len(timeseries_in)])
        (Counter(time_irrad_clear['clear'])[True])))


print "preparing clear days for aerosol optical depth optimization...",
# make a list of dictionaries of settings and targets
names = time_irrad_clear.dtype.names
config_dicts = [dict(zip(names, record)) for record in time_irrad_clear]
optimizeable = []
for config_dict, clear in zip(config_dicts, time_irrad_clear['clear']):
    if clear:
        config = dict(config_dict)
        target = config.pop('irradiance')
        optimizeable.append({
            'config': config,
            'target': target,
        })
print "done"

"""
print "submitting to smarts...",
optimizer = rtms.Optimizer(parameter="aerosol_optical_depth",
    bounds=(0,1), tolerance=0.01)
optimizer.optimze
"""
