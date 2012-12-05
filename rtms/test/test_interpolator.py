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
from numpy import nan, array
from .. import interpolator


class TestInterpolator(unittest.TestCase):

    def assertInterpolated(self, data_in, expected):
        out = interpolator.interpolate(data_in)
        self.assertEqual(out, expected)

    def assertNumpyInterpolated(self, data_in, expected):
        out = interpolator.interpolate(data_in)
        self.assertTrue((out == expected).all())

    def testEmpty(self):
        self.assertInterpolated([[]], [[]])

    def testSingleDat(self):
        self.assertInterpolated(
            [[datetime(2012, 1, 1, 0, 0), 1.0]],
            [[datetime(2012, 1, 1, 0, 0), 1.0]])

    def testSingleNaN(self):
        with self.assertRaises(interpolator.NoValidDataError):
            interpolator.interpolate([[datetime(2012, 1, 1, 0, 0), nan]])

    def testLeadingNaN(self):
        self.assertInterpolated(
            [[datetime(2012, 1, 1, 0, 0), nan],
             [datetime(2012, 1, 1, 0, 1), 1.0]],
            [[datetime(2012, 1, 1, 0, 0), 1.0],
             [datetime(2012, 1, 1, 0, 1), 1.0]])

    def testTrailingNaN(self):
        self.assertInterpolated(
            [[datetime(2012, 1, 1, 0, 0), 1.0],
             [datetime(2012, 1, 1, 0, 1), nan]],
            [[datetime(2012, 1, 1, 0, 0), 1.0],
             [datetime(2012, 1, 1, 0, 1), 1.0]])

    def testNaNSandwich(self):
        self.assertInterpolated(
            [[datetime(2012, 1, 1, 0, 0), nan],
             [datetime(2012, 1, 1, 0, 1), 1.0],
             [datetime(2012, 1, 1, 0, 2), nan]],
            [[datetime(2012, 1, 1, 0, 0), 1.0],
             [datetime(2012, 1, 1, 0, 1), 1.0],
             [datetime(2012, 1, 1, 0, 2), 1.0]])

    def testMidNaN(self):
        self.assertInterpolated(
            [[datetime(2012, 1, 1, 0, 0), 0.0],
             [datetime(2012, 1, 1, 0, 1), nan],
             [datetime(2012, 1, 1, 0, 2), 1.0]],
            [[datetime(2012, 1, 1, 0, 0), 0.0],
             [datetime(2012, 1, 1, 0, 1), 0.5],
             [datetime(2012, 1, 1, 0, 2), 1.0]])

    def testTwoNaNs(self):
        self.assertInterpolated(
            [[datetime(2012, 1, 1, 0, 0), 1.0],
             [datetime(2012, 1, 1, 0, 1), nan],
             [datetime(2012, 1, 1, 0, 2), nan],
             [datetime(2012, 1, 1, 0, 3), 4.0]],
            [[datetime(2012, 1, 1, 0, 0), 1.0],
             [datetime(2012, 1, 1, 0, 1), 2.0],
             [datetime(2012, 1, 1, 0, 2), 3.0],
             [datetime(2012, 1, 1, 0, 3), 4.0]])

    def testTwoNaNGaps(self):
        self.assertInterpolated(
            [[datetime(2012, 1, 1, 0, 0), 1.0],
             [datetime(2012, 1, 1, 0, 1), nan],
             [datetime(2012, 1, 1, 0, 2), 3.0],
             [datetime(2012, 1, 1, 0, 3), nan],
             [datetime(2012, 1, 1, 0, 4), 5.0]],
            [[datetime(2012, 1, 1, 0, 0), 1.0],
             [datetime(2012, 1, 1, 0, 1), 2.0],
             [datetime(2012, 1, 1, 0, 2), 3.0],
             [datetime(2012, 1, 1, 0, 3), 4.0],
             [datetime(2012, 1, 1, 0, 4), 5.0]])

    def testLongDateRange(self):
        # whitebox: datetime.seconds is INVALID, we need to make sure it uses
        # datetime.total_seconds().
        self.assertInterpolated(
            [[datetime(2012, 1, 1, 0, 0), 0.0],
             [datetime(2012, 1, 3, 1, 0), nan],
             [datetime(2012, 1, 5, 2, 0), 1.0]],
            [[datetime(2012, 1, 1, 0, 0), 0.0],
             [datetime(2012, 1, 3, 1, 0), 0.5],
             [datetime(2012, 1, 5, 2, 0), 1.0]])

    def testNumpyArray(self):
        self.assertNumpyInterpolated(
            array([[datetime(2012, 1, 1, 0, 0), 0.0],
                   [datetime(2012, 1, 1, 1, 0), nan],
                   [datetime(2012, 1, 1, 2, 0), 1.0]]),
            array([[datetime(2012, 1, 1, 0, 0), 0.0],
                   [datetime(2012, 1, 1, 1, 0), 0.5],
                   [datetime(2012, 1, 1, 2, 0), 1.0]]))



if __name__ == '__main__':
    unittest.main()