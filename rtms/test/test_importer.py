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
from StringIO import StringIO
from numpy import nan, isnan
from numpy.testing import assert_warns
from .. import importer


class TestDataImporter(unittest.TestCase):

    def testValidCSV(self):
        f = StringIO("time,irradiance\n'2012-01-01 12:00:00-07:00',460")
        imported = importer.data(f)

    def testInvalidDT(self):
        with self.assertRaises(importer.DateTimeParseError):
            f = StringIO("time,irradiance\n'2012-01-50 12:00:00-07:00',460")
            imported = importer.data(f)

    def testInvalidHeader(self):
        with self.assertRaises(importer.HeaderError):
            f = StringIO("time,blah,irradiance\n'2012-01-01 12:00:00-07:00',0,460")
            imported = importer.data(f)

    def testNanData(self):
        f = StringIO("time,irradiance\n'2012-01-01 12:00:00-07:00',nan")
        imported = importer.data(f)
        if not isnan(imported['irradiance']):
            raise ValueError('nan should have been interpreted as nan!')

    def testNoData(self):
        f = StringIO("time,irradiance")
        imported = importer.data(f)

    def testEmpty(self):
        f = StringIO("")
        with self.assertRaises(ValueError):
            assert_warns(UserWarning, importer.data, f)


class TestInfoImporter(unittest.TestCase):

    def testValidInfo(self):
        y = "latitude: 39.74\nlongitude: -105.18"
        info = importer.info(y)
        expected = {'latitude': 39.74, 'longitude': -105.18}
        self.assertEqual(info, expected)

    def testExtraInfo(self):
        y = "latitude: 39.74\nlongitude: -105.18\nelevation: 1.829"
        info = importer.info(y)
        expected = {'latitude': 39.74, 'longitude': -105.18, 'elevation': 1.829}
        self.assertEqual(info, expected)

    def testMissingProperties(self):
        y = "latitude: 39.74"
        with self.assertRaises(KeyError):
            info = importer.info(y)

    def testNoProperties(self):
        y = ""
        with self.assertRaises(TypeError):
            info = importer.info(y)

    def testInvalidKeys(self):
        y = "latitude: 39.74\nlongitude: -105.18\nblah: 0"
        with self.assertRaises(KeyError):
            info = importer.info(y)


if __name__ == '__main__':
    unittest.main()
