"""
    Copyright (c) 2012 Philip Schliehauf (uniphil@gmail.com) and the
    Queen's University Applied Sustainability Centre
    
    This project is hosted on github; for up-to-date code and contacts:
    https://github.com/Queens-Applied-Sustainability/RTMSuite
    
    This file is part of RTMSuite.

    RTMSuite is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    RTMSuite is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with RTMSuite.  If not, see <http://www.gnu.org/licenses/>.

    ----


    data:

    This tool takes an input file and builds a numpy array in a useable format.

    All columns of the input file must correspond to properties from
    rtm.settings
    (https://github.com/Queens-Applied-Sustainability/PyRTM/blob/master/rtm/settings.py)

    Another script is provided with this package to easily convert time-series
    meteorological data to the correct format.

    The input must be a file-like object with csv contents.

    There must be a column for measured irradiance, called 'irradiance'.

    The time column must be present, and must be in ISO format:
    '2012-01-01 12:00:00-07:00'


    info:

    THIS DOC SECTION IS OUT OF DATE.
    check the example folder and actual code.

    parses and validates an info file

    such a file must, at minimum, define latitude and longitude.
    it may also define elevation, and any other properties that should be kept
    constant for every input to the rtm modelers.
    
    properties defined in the time-series csv will take precedence over those
    defined in info.

    valid properties are any of those in rtm.settings.


    This tool requires pyyaml.

"""

import logging
from copy import deepcopy
import yaml
from numpy import genfromtxt, nan
from numpy.lib._iotools import ConverterError
from dateutil import parser as dtparser
import defaults


class DateTimeParseError(ConverterError): pass


class HeaderError(KeyError): pass


VALID_PROPERTIES = set(defaults.rtm_settings.keys() + ['irradiance'])


def config(config_file):
    # returns info, map, run

    required = set(['info', 'csv_map'])
    required_info = set(['latitude', 'longitude'])
    required_map = set(['time', 'irradiance'])
    additional = set(['meta'])
    valid_run = set(['save_everything', 'multiprocessing',
                        'processes', 'verbosity'])

    parsed = yaml.load(config_file)

    # make sure we got a dict
    if not isinstance(parsed, dict):
        raise TypeError("Settings did not parse to a dictionary: %s" % parsed)

    # make sure we got the right dicts
    if not all(section in parsed for section in required):
        missing = set(key for key in required if key not in parsed)
        raise KeyError("Missing config sections: " + ", ".join(missing))

    # check if additional sectons are present
    extras = set(section for section in additional if section in parsed)

    # check if any other sections are there for some reason
    if any(section not in required+additional for section in parsed):
        misplaced = set(section for section in parsed if
            section not in reqired+additional)
        logging.warning('Found extraneous sections in the config: ' + \
            ', '.join(misplaced))

    # make sure our dicts contain dicts
    for subdict in required+extras:
        if not isinstance(subdict, dict):
            raise TypeError("config sections didn't import as dicts...")

    # check we have the necessary info
    info_dict = parsed['info']
    if any(prop not in info_dict for prop in required_info):
        missing = set(prop for prop in required_info if prop not in info_dict)
        raise ValueError('Missing info properties: ' + ', '.join(missing))

    # check we have the necessary mappings
    map_dict = parsed['csv_map']
    if any(prop not in map_dict for prop in map_dict):
        missing = set(prop for prop in required_map if prop not in map_dict)
        raise ValueError('Missing ')

    # check that all the mappings and info are legit
    rtm_keys = set(info_dict.keys() + map_dict.keys())
    if any(key not in VALID_PROPERTIES for key in rtm_keys):
        invalids = set(key for key in rtm_keys if key not in VALID_PROPERTIES)

        # pull out the invalids
        info_invalids = [info_dict.pop(p) for p in invalids if p in info_dict]
        if info_invalids:
            logging.warning('ignoring invalid info properties: ' + \
                            ', '.join(info_invalids))
        map_invalids = [map_dict.pop(p) for p in invalids if p in map_dict]
        if map_invalids:
            logging.warning('ignoring invalid mappings: ' + \
                            ', '.join(map_invalids))

    # warn if info settings will be overridden by the mapping
    if any(info_key in map_dict for info_key in info_dict):
        overridden = set(key for key in info_dict if key in map_dict)
        logging.warning('info settings {} will be overridden by the mapped '\
            'csv values for that setting'.format(', '.join(overridden)))

    # deal with no run settings
    run_dict = defaults.run
    try:
        run_dict.update(parsed['run'])
    except KeyError:
        logging.info('no run settings found in config, using defaults')
    # check that all run settings are legit
    if any(key not in defaults.run for key in run_dict):
        invalids = set(key for key in run_dict if key not in defaults.run)
        logging.warning('ignoring invalid run settings: ' + \
                        ', '.join(invalids))

    return info_dict, map_dict, run_dict


def data(data_file):
    gen_kwargs = {
        'delimiter': ',',
        'names': True,
        'converters': {'time': lambda s: dtparser.parse(s)},
        'dtype': None,
    }
    try:
        parsed = genfromtxt(data_file, **gen_kwargs)
    except ConverterError:
        raise DateTimeParseError("Could not convert the date.")
    except IndexError:
        raise ValueError("Encountered an IndexError -- empty file?")


    headers = parsed.dtype.fields.keys()

    # verify that at least time and irradiance are present
    basic_properties = set(['time', 'irradiance'])
    if any(prop not in headers for prop in basic_properties):
        missing = (prop for prop in basic_properties if prop not in headers)
        raise KeyError("Missing names: " + ", ".join(missing))

    # verify that all the columns are legit
    if any(k not in VALID_PROPERTIES for k in headers):
        bad_ones = (k for k in headers if k not in VALID_PROPERTIES)
        raise HeaderError("Invalid header names: " + ", ".join(bad_ones))

    return parsed
