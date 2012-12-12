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

    --

    This is a tool to pick out the clear-sky points from the cloudy-sky
    points in time-series irradiance data.

    The tool compares the rate of change of irradiance to what would be
    expected of extra-terrestrial irradiance to decide if it's clear or
    not.

    First, set up the met station parameters:

        * latitude
        * longitude

    Then, feed it a time-series array of the format:
    [
        {'time': datetime, 'irradiance': w/m2},
        {'time': datetime, 'irradiance': w/m2},
        ...
    ]

    The program will return an array of the form:

    [
        {'time': datetime, 'irradiance': w/m2, 'clear': bool},
        {'time': datetime, 'irradiance': w/m2, 'clear': bool},
        ...
    ]

"""

from copy import deepcopy
from itertools import chain
from numpy import nan
from rtm.tools import solar

SKIP_NIGHT = True
NIGHT_CONST = 12 # W/m^2; less than this is night
#SOLAR_CONST = 1367 # W/m^2
CHANGE_CONST = 6 # W/m^2 min
#TIME_CONST = 60 # minutes; spans greater than this are meaningless
Kt_MIN = 0.5


class Selector(object):
    """docstring for Selector"""
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        self.ext_irrad_calc = solar.extraterrestrial_radiation
    
    def select(self, irr_data):
        data = deepcopy(irr_data)

        prev_row, this_row, next_row = None, None, None
        prev_G, this_G, next_G = None, None, None
        prev_dt, next_dt = None, None
        prev_dirrad, next_dirrad = None, None
        prev_dextra, next_dextra = None, None

        for next_row in chain(data, [None]):

            if next_row:
                next_G = self.ext_irrad_calc(next_row[0],
                    self.latitude, self.longitude)

            if this_row and next_row:
                next_dt = (next_row[0] - this_row[0]).total_seconds() / 60.0
                next_dirrad = (next_row[1] - this_row[1]) / next_dt
                next_dextra = (next_G - this_G) / next_dt

            if this_row:
                change = 0
                if prev_row:
                    change = abs(prev_dextra - prev_dirrad)
                if next_row:
                    change = max(change, abs(next_dextra - next_dirrad))

                this_row.append(change < CHANGE_CONST)

            # shuffle down
            prev_row, this_row = this_row, next_row
            prev_G, this_G = this_G, next_G
            prev_dt = next_dt
            prev_dirrad = next_dirrad
            prev_dextra = next_dextra


        return data


