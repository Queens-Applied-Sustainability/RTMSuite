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

    This is a tool to interpolate missing data points for time-series
    data. It takes a 2-d list, in the form:
    [
        [datetime, data],
        [datetime, data],
        ...
    ]
    where data may be either a floating-point value, or NaN. If it is
    NaN, the tool will perform a linear interpolation from the nearest
    data points on either side and replace the NaN the new value.

"""

from copy import deepcopy
from numpy import nan

class NoValidDataError(ValueError): pass


def interpolate(input_data):
    out = deepcopy(input_data)

    # catch empty
    if len(out) == 1 and not out[0]:
        return out
    
    # find first data point and fill in any starting gap
    first = 0
    empties = 0
    while out[first][1] is nan:
        empties += 1
        # make sure the whole thing's not just nans
        if empties == len(out):
            raise NoValidDataError('There must be at least one data point')
        first = empties
    for index in range(empties):
        out[index][1] = out[first][1]

    # find the last data point and fill in any trailing gap
    last = len(out) - 1
    empties = 0
    while out[last][1] is nan:
        empties += 1
        last = len(out) - empties - 1
    for index in range(len(out)-1, last, -1):
        out[index][1] = out[last][1]

    # interpolate all the gaps.
    index = last
    while index > first:
        index -= 1
        # have we entered a gap?
        if out[index][1] is nan:
            last_val_index = index + 1
            # find the next edge
            while out[index][1] is nan:
                index -= 1
            # what's the slope through the gap?
            delta_t = out[index][0] - out[last_val_index][0]
            delta_v = out[index][1] - out[last_val_index][1]
            slope = delta_v / delta_t.total_seconds()
            intercept = out[last_val_index][1]
            # fill in the gap
            for point_index in range(index, last_val_index):
                delta_t = out[point_index][0] - out[last_val_index][0]
                delta_v = slope * delta_t.total_seconds()
                out[point_index][1] = intercept + delta_v

    return out