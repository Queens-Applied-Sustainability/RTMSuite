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
    """returns info, map, run"""

    required = set(['info', 'csv_map'])
    required_info = set(['latitude', 'longitude'])
    required_map = set(['time', 'irradiance'])
    additional = set(['run'])
    valid_run = set(['save_everything', 'multiprocessing',
                        'processes', 'verbosity'])

    parsed = yaml.load(config_file)

    # make sure we got a dict
    if not isinstance(parsed, dict):
        raise TypeError("Settings did not parse to a dictionary: %s" % parsed)

    sections = set(parsed.keys())

    # make sure we got the right dicts
    if not sections >= required:
        raise KeyError("Missing config sections: " +
            ", ".join(required - sections))

    # check if optional sectons are present
    optionals = additional & sections

    # make sure our dicts contain dicts
    for subdict in (required | optionals):
        if not isinstance(parsed[subdict], dict):
            raise TypeError("config section didn't import as dict: %s" %
                subdict)

    # check if any other sections are there for some reason
    if not sections <= (required | additional):
        logging.warning('Ignoring extraneous sections in the config: ' +
            ', '.join(sections - (required | additional)))

    # check we have the necessary info
    info_set = set(parsed['info'])
    if not required_info <= info_set:
        raise ValueError('Missing info properties: ' +
            ', '.join(required_info - info_set))
    # make it all legit
    if not info_set <= VALID_PROPERTIES:
        logging.warning('ignoring invalid properties: ' +
            ', '.join(info_set - VALID_PROPERTIES))
        info_set &= VALID_PROPERTIES

    # check we have the necessary mappings
    map_set = set(parsed['csv_map'])
    if not required_map <= map_set:
        raise ValueError('Missing csv map properties: ' + 
            ', '.join(required_map - map_set))
    # make it all legit
    if not map_set <= VALID_PROPERTIES:
        logging.warning('ignoring invalid mappings: ' +
            ', '.join(map_set - VALID_PROPERTIES))
        map_set &= VALID_PROPERTIES


    if not info_set.isdisjoint(map_set):
        logging.warning('info settings {} will be overridden by the mapped '
            'csv values for that setting'.format(', '.join(info_set & map_set)))

    # deal with no run settings
    run_dict = deepcopy(defaults.run)
    try:
        run_dict.update(parsed['run'])
    except KeyError:
        logging.info('no run settings found in config, using defaults')

    # check that all run settings are legit
    if not set(run_dict) <= set(defaults.run):
        logging.warning('ignoring invalid run settings: ' +
            ', '.join(set(defaults.run) - set(run_dict)))

    info_dict = {k:v for k, v in parsed['info'].items() if k in info_set}
    map_dict = {k:v for k, v in parsed['csv_map'].items() if k in map_set}
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
