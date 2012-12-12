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
        self.assertEqual(out, expected)

    def testEmpty(self):
        irr_data = []
        with self.assertRaises(selector.InsufficientDataError):
            select = selector.Selector(LATITUDE, LONGITUDE)
            select.select(irr_data)

    def testOne(self):
        irr_data = [
            [dt.parse('01/01/2012 12:00 -0700'), 500],
        ]
        with self.assertRaises(selector.InsufficientDataError):
            select = selector.Selector(LATITUDE, LONGITUDE)
            select.select(irr_data)

    def testTwoClear(self):
        irr_data = [
            [dt.parse('01/01/2012 12:00 -0700'), 500],
            [dt.parse('01/01/2012 12:01 -0700'), 501],
        ]
        expected = [
            [dt.parse('01/01/2012 12:00 -0700'), 500, True],
            [dt.parse('01/01/2012 12:01 -0700'), 501, True],
        ]
        self.assertDetected(irr_data, expected)

    def testTwoCloudy(self):
        irr_data = [
            [dt.parse('01/01/2012 12:00 -0700'), 500],
            [dt.parse('01/01/2012 12:01 -0700'), 510],
        ]
        expected = [
            [dt.parse('01/01/2012 12:00 -0700'), 500, False],
            [dt.parse('01/01/2012 12:01 -0700'), 510, False],
        ]
        self.assertDetected(irr_data, expected)

    def testFirstClear(self):
        irr_data = [
            [dt.parse('01/01/2012 12:00 -0700'), 640],
            [dt.parse('01/01/2012 12:01 -0700'), 641],
            [dt.parse('01/01/2012 12:02 -0700'), 649],
        ]
        expected = [
            [dt.parse('01/01/2012 12:00 -0700'), 640, True],
            [dt.parse('01/01/2012 12:01 -0700'), 641, False],
            [dt.parse('01/01/2012 12:02 -0700'), 649, False],
        ]
        self.assertDetected(irr_data, expected)

    def testLastClear(self):
        irr_data = [
            [dt.parse('01/01/2012 12:00 -0700'), 640],
            [dt.parse('01/01/2012 12:01 -0700'), 649],
            [dt.parse('01/01/2012 12:02 -0700'), 649],
        ]
        expected = [
            [dt.parse('01/01/2012 12:00 -0700'), 640, False],
            [dt.parse('01/01/2012 12:01 -0700'), 649, False],
            [dt.parse('01/01/2012 12:02 -0700'), 649, True],
        ]
        self.assertDetected(irr_data, expected)

    def testSpike(self):
        irr_data = [
            [dt.parse('01/01/2012 12:00 -0700'), 640],
            [dt.parse('01/01/2012 12:01 -0700'), 649],
            [dt.parse('01/01/2012 12:02 -0700'), 640],
        ]
        expected = [
            [dt.parse('01/01/2012 12:00 -0700'), 640, False],
            [dt.parse('01/01/2012 12:01 -0700'), 649, False],
            [dt.parse('01/01/2012 12:02 -0700'), 640, False],
        ]
        self.assertDetected(irr_data, expected)

    def testThreeClear(self):
        irr_data = [
            [dt.parse('01/01/2012 12:00 -0700'), 640],
            [dt.parse('01/01/2012 12:01 -0700'), 641],
            [dt.parse('01/01/2012 12:02 -0700'), 640],
        ]
        expected = [
            [dt.parse('01/01/2012 12:00 -0700'), 640, True],
            [dt.parse('01/01/2012 12:01 -0700'), 641, True],
            [dt.parse('01/01/2012 12:02 -0700'), 640, True],
        ]
        self.assertDetected(irr_data, expected)

    def testDark(self):
        irr_data = [
            [dt.parse('01/01/2012 00:00 -0700'), 0],
            [dt.parse('01/01/2012 00:01 -0700'), 0],
        ]
        expected = [
            [dt.parse('01/01/2012 00:00 -0700'), 0, None],
            [dt.parse('01/01/2012 00:01 -0700'), 0, None],
        ]
        self.assertDetected(irr_data, expected)

    def testSkipDark(self):
        irr_data = [
            [dt.parse('01/01/2012 12:00 -0700'), 640],
            [dt.parse('01/02/2012 00:00 -0700'), 0],
            [dt.parse('01/02/2012 12:01 -0700'), 640],
        ]
        expected = [
            [dt.parse('01/01/2012 12:00 -0700'), 640, True],
            [dt.parse('01/02/2012 00:00 -0700'), 0, None],
            [dt.parse('01/02/2012 12:01 -0700'), 640, True],
        ]
        self.assertDetected(irr_data, expected)


if __name__ == '__main__':
    unittest.main()
