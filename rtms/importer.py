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
import yaml
from numpy import genfromtxt, nan, datetime64
from numpy.lib._iotools import ConverterError
from dateutil import parser as dtparser
from rtm import settings as rtmsettings


class DateTimeParseError(ConverterError): pass


class HeaderError(KeyError): pass


VALID_PROPERTIES = set(rtmsettings.defaults.keys() + ['irradiance'])


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


def info(info_file):

    parsed = yaml.load(info_file)

    # make sure we got a dict out
    if not isinstance(parsed, dict):
        raise TypeError("Settings did not parse to a dictionary: %s" % parsed)

    # make sure latitude and longitude are there
    basic_properties = set(['latitude', 'longitude'])
    if any(prop not in parsed for prop in basic_properties):
        missing = (prop for prop in basic_properties if prop not in parsed)
        raise KeyError("Missing properties: " + ", ".join(missing))

    # verify keys
    if any(k not in VALID_PROPERTIES for k in parsed):
        bad_ones = (k for k in parsed if k not in VALID_PROPERTIES)
        raise KeyError("Invalid properties: " + ", ".join(bad_ones))

    return parsed
