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






