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
"""

import unittest
from datetime import datetime
from dateutil import parser as dt
from .. import selector

LATITUDE = 39.74 # degrees north
LONGITUDE = 254.82 # degrees east


class TestSelector(unittest.TestCase):

    def assertDetected(self, irr_data, expected):
        select = selector.Selector(LATITUDE, LONGITUDE)
        out = select.select(irr_data)
        self.assertEqual(irr_data, out)

    def testTwoClear(self):
        irr_data = [
            [dt.parse('01/01/2012 11:00 -0700'), 500],
            [dt.parse('01/01/2012 11:05 -0700'), 502],
        ]
        expected = [
            [dt.parse('01/01/2012 11:00 -0700'), 500, True],
            [dt.parse('01/01/2012 11:05 -0700'), 502, True],
        ]
        self.assertDetected(irr_data, expected)

    def testTwoCloudy(self):
        irr_data = [
            [dt.parse('01/01/2012 11:00 -0700'), 500],
            [dt.parse('01/01/2012 11:05 -0700'), 550],
        ]
        expected = [
            [dt.parse('01/01/2012 11:00 -0700'), 500, False],
            [dt.parse('01/01/2012 11:05 -0700'), 550, False],
        ]
        self.assertDetected(irr_data, expected)

    def testFirstClear(self):
        irr_data = [
            [dt.parse('01/01/2012 11:00 -0700'), 500],
            [dt.parse('01/01/2012 11:05 -0700'), 501],
            [dt.parse('01/01/2012 11:10 -0700'), 550],
        ]
        expected = [
            [dt.parse('01/01/2012 11:00 -0700'), 500, True],
            [dt.parse('01/01/2012 11:05 -0700'), 501, False],
            [dt.parse('01/01/2012 11:10 -0700'), 550, False],
        ]
        self.assertDetected(irr_data, expected)

    def testLastClear(self):
        irr_data = [
            [dt.parse('01/01/2012 11:00 -0700'), 500],
            [dt.parse('01/01/2012 11:05 -0700'), 550],
            [dt.parse('01/01/2012 11:10 -0700'), 551],
        ]
        expected = [
            [dt.parse('01/01/2012 11:00 -0700'), 500, False],
            [dt.parse('01/01/2012 11:05 -0700'), 550, False],
            [dt.parse('01/01/2012 11:10 -0700'), 551, True],
        ]
        self.assertDetected(irr_data, expected)

    def testSpike(self):
        irr_data = [
            [dt.parse('01/01/2012 11:00 -0700'), 500],
            [dt.parse('01/01/2012 11:05 -0700'), 550],
            [dt.parse('01/01/2012 11:10 -0700'), 501],
        ]
        expected = [
            [dt.parse('01/01/2012 11:00 -0700'), 500, False],
            [dt.parse('01/01/2012 11:05 -0700'), 550, False],
            [dt.parse('01/01/2012 11:10 -0700'), 501, False],
        ]
        self.assertDetected(irr_data, expected)

    def testThreeClear(self):
        irr_data = [
            [dt.parse('01/01/2012 11:00 -0700'), 500],
            [dt.parse('01/01/2012 11:05 -0700'), 501],
            [dt.parse('01/01/2012 11:10 -0700'), 502],
        ]
        expected = [
            [dt.parse('01/01/2012 11:00 -0700'), 500, True],
            [dt.parse('01/01/2012 11:05 -0700'), 501, True],
            [dt.parse('01/01/2012 11:10 -0700'), 502, True],
        ]
        self.assertDetected(irr_data, expected)

    # test night, etc


if __name__ == '__main__':
    unittest.main()
