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
from nose.plugins.attrib import attr

from numpy import nan
from dateutil import parser as dtp
from rtm import SMARTS, RTMError
from .. import optimizer

base = {'latitude': 39.74, 'longitude': 254.82, 'description': 'test'}
sample = [
    {
        'settings': {'time': dtp.parse('2012-01-01 12:00 -0700')},
        'target': 420,
    },
    {
        'settings': {'time': dtp.parse('2012-01-01 12:01 -0700')},
        'target': 421,
    },
]
aod = 'angstroms_coefficient'


class TestOptimizer(unittest.TestCase):

    def assertOptimizedEqual(self, expected, result):
        self.assertEqual(len(expected), len(result))
        decimal_places = 1
        for exp, res in zip(expected, result):
            if exp is nan and res is nan:
                continue # nan == nan ...
            self.assertAlmostEqual(exp, res, decimal_places)

    def testFMMInstalled(self):
        from fmm import zeroin, BadBoundsError, NoConvergeError

    def testSingleSmarts(self):
        from rtm import SMARTS
        expected = [0.25]
        result = optimizer.optimize([sample[0]], base, SMARTS, aod)
        self.assertOptimizedEqual(expected, result)

    def testSingleSmartsMultiprocessing(self):
        from multiprocessing import Pool
        from rtm import SMARTS
        expected = [0.25]
        result = optimizer.optimize([sample[0]], base, SMARTS, aod, Pool().map)
        self.assertOptimizedEqual(expected, result)

    def testSmartsMultiprocessing(self):
        from multiprocessing import Pool
        from rtm import SMARTS
        expected = [0.25, 0.24]
        result = optimizer.optimize(sample, base, SMARTS, aod, Pool(2).map)
        self.assertOptimizedEqual(expected, result)

    @attr('slow')
    def testSBdartMultiprocessing(self):
        "this test takes a long time!"
        from multiprocessing import Pool
        from rtm import SBdart
        expected = [0.25]
        result = optimizer.optimize([sample[0]], base, SBdart, aod, Pool(2).map)
        self.assertOptimizedEqual(expected, result)

    def testBadBounds(self):
        from rtm import SMARTS
        expected = [nan]
        this_sample = [{
            'settings': {'time': dtp.parse('2012-01-01 12:00 -0700')},
            'target': 0 }]
        result = optimizer.optimize(this_sample, base, SMARTS, aod)
        self.assertOptimizedEqual(expected, result)

    def testSmartsSunDown(self):
        from rtm import SMARTS
        expected = [nan]
        this_sample = [{
            'settings': {'time': dtp.parse('2012-01-01 00:00 -0700')},
            'target': 0 }]
        result = optimizer.optimize(this_sample, base, SMARTS, aod)
        self.assertOptimizedEqual(expected, result)

    @classmethod
    def tearDownClass(cls):
        from shutil import rmtree
        test_dir_name = '-'.join([base['description'],
            str(base['longitude']), str(base['latitude'])])
        rmtree(test_dir_name)


if __name__ == '__main__':
    unittest.main()