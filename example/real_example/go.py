from collections import Counter
from numpy import nan
from rtm import SMARTS
import rtms

CONFIG_FILE = open('config.yaml')
DATA_FILE = open('time-series.csv')


print "Importing configuration...",
site_info, csv_map, run_config = rtms.importer.config(CONFIG_FILE)
print "done."

print "Importing data...",
timeseries_in = rtms.importer.data(DATA_FILE, csv_map)
print "imported {} rows.".format(len(timeseries_in))


print "Selecting clear days...",
selector = rtms.Selector(site_info['latitude'], site_info['longitude'])
time_irrad_clear = selector.select(timeseries_in[['time', 'irradiance']])
print "selected {} ({:.1%}) clear points.".format(
    *((lambda c: [c, float(c)/len(timeseries_in)])
        (Counter(time_irrad_clear['clear'])[True])))


print "Preparing clear days for aerosol optical depth optimization...",
# make a list of dictionaries of settings and targets
names = time_irrad_clear.dtype.names
config_dicts = [dict(zip(names, record)) for record in time_irrad_clear]
optimizeable = []
for config_dict, clear in zip(config_dicts, time_irrad_clear['clear']):
    if clear:
        config = dict(config_dict)
        config.pop('clear')
        target = config.pop('irradiance')
        optimizeable.append({
            'settings': config,
            'target': target,
        })
print "done."


print "Submitting to optimizer for SMARTS..."
aods = rtms.optimize(optimizeable, site_info, SMARTS, 'angstroms_coefficient')
print "optimzed {} points ({:.1%}) of {} selected clear points.".format(
    *((lambda l:((lambda s,t:[s,float(s)/t,t])(l - Counter(aods)[nan],l))
       )(len(aods))))


print "Interpolating AOD between successful optimizations...",
optimes = [o['settings']['time'] for o in optimizeable]
time_aod = [[t, aod] for t, aod in zip(optimes, aods)]
interp_aods = rtms.interpolate(time_aod)
print "done."