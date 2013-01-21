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

from copy import deepcopy
import unittest
import yaml
from nose.plugins.attrib import attr
from StringIO import StringIO
from numpy import nan, isnan
from numpy.testing import assert_warns
from .. import importer


class MockLogger(object):
    class Warning(Exception): pass
    class Info(Exception): pass
    def warning(self, message):
        raise self.Warning(message)
    def info(self, message):
        raise self.Info(message)


class TestConfigInfo(unittest.TestCase):
    basic = {
        'info': {
            'latitude': 39.74,
            'longitude': -105.18,
            'description': 'Testing...',
        },
        'csv_map': {
            'time': 'time',
            'irradiance': 'irradiance',
        },
        'run': {
            'save_everything': True,
            'multiprocessing': True,
            'processes': 2,
            'verbosity': 'warnings',
        }
    }

    def setUp(self):
        self._importer_logging = importer.logging
        importer.logging = MockLogger()

    def tearDown(self):
        importer.loggin = self._importer_logging

    def assertConfigEqual(self, yaml_in, expected):
        info_dict, map_dict, run_dict = importer.config(yaml_in)
        self.assertEqual(info_dict, expected['info'])
        self.assertEqual(map_dict, expected['csv_map'])
        self.assertEqual(run_dict, expected['run'])

    def testValid(self):
        y_in = yaml.dump(self.basic)
        self.assertConfigEqual(y_in, self.basic)

    def testExtraInfo(self):
        conf = deepcopy(self.basic)
        conf['info'].update({'surface_type': 'vegetation'})
        y_in = yaml.dump(conf)
        self.assertConfigEqual(y_in, conf)

    def testExtraMap(self):
        conf = deepcopy(self.basic)
        conf['csv_map'].update({'surface_type': 'vegetation'})
        y_in = yaml.dump(conf)
        self.assertConfigEqual(y_in, conf)

    def testNoRun(self):
        conf = deepcopy(self.basic)
        conf.pop('run')
        y_in = yaml.dump(conf)
        with self.assertRaises(MockLogger.Info):
            importer.config(y_in)

    def testInvalidInfo(self):
        conf = deepcopy(self.basic)
        conf['info'].update({'invalid': 'blah'})
        y_in = yaml.dump(conf)
        with self.assertRaises(MockLogger.Warning):
            self.assertConfigEqual(y_in, self.basic)

    def testInvalidMap(self):
        conf = deepcopy(self.basic)
        conf['csv_map'].update({'invalid': 'blah'})
        y_in = yaml.dump(conf)
        with self.assertRaises(MockLogger.Warning):
            self.assertConfigEqual(y_in, self.basic)

    def testInvalidRun(self):
        conf = deepcopy(self.basic)
        conf['run'].update({'invalid': 'blah'})
        y_in = yaml.dump(conf)
        with self.assertRaises(MockLogger.Warning):
            importer.config(y_in)

    def testMissingInfo(self):
        conf = deepcopy(self.basic)
        conf['info'].pop('latitude')
        y_in = yaml.dump(conf)
        with self.assertRaises(ValueError):
            self.assertConfigEqual(y_in, self.basic)

    def testMissingMap(self):
        conf = deepcopy(self.basic)
        conf['csv_map'].pop('time')
        y_in = yaml.dump(conf)
        with self.assertRaises(ValueError):
            self.assertConfigEqual(y_in, self.basic)

    def testNoInfo(self):
        conf = deepcopy(self.basic)
        conf.pop('info')
        y_in = yaml.dump(conf)
        with self.assertRaises(KeyError):
            self.assertConfigEqual(y_in, self.basic)

    def testNoMap(self):
        conf = deepcopy(self.basic)
        conf.pop('csv_map')
        y_in = yaml.dump(conf)
        with self.assertRaises(KeyError):
            self.assertConfigEqual(y_in, self.basic)

    def testNoRun(self):
        conf = deepcopy(self.basic)
        conf.pop('run')
        y_in = yaml.dump(conf)
        with self.assertRaises(MockLogger.Info):
            importer.config(y_in)

    def testEmptyConfig(self):
        with self.assertRaises(TypeError):
            self.assertConfigEqual("", self.basic)


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

    ### WITH column_map ###

    def testValidCSVMapped(self):
        f = StringIO("Time,irrad\n'2012-01-01 12:00:00-07:00',460")
        imported = importer.data(f, {
            'time': 'Time',
            'irradiance': 'irrad',
        })

    def testInvalidDTMapped(self):
        with self.assertRaises(importer.DateTimeParseError):
            f = StringIO("Time,irrad\n'2012-01-50 12:00:00-07:00',460")
            imported = importer.data(f, {
                'time': 'Time',
                'irradiance': 'irrad',
            })

    def testInvalidHeaderMapped(self):
        with self.assertRaises(importer.HeaderError):
            f = StringIO("time,blah,irradiance\n'2012-01-01 12:00:00-07:00',0,460")
            imported = importer.data(f, {
                'time': 'time',
                'invalid': 'blah',
                'irradiance': 'irradiance',
            })

    def testInvalidHeaderMappedOut(self):
        f = StringIO("time,blah,irradiance\n'2012-01-01 12:00:00-07:00',0,460")
        imported = importer.data(f, {
            'time': 'time',
            'irradiance': 'irradiance',
        })

    def testNoDataMapped(self):
        with self.assertRaises(KeyError):
            f = StringIO("time,irradiance")
            imported = importer.data(f, {
                'time': 'Time',
                'irradiance': 'irradiance',
            })

    def testEmptyMapped(self):
        f = StringIO("")
        with self.assertRaises(ValueError):
            assert_warns(UserWarning, importer.data, f, {})



if __name__ == '__main__':
    unittest.main()
