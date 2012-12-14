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

    create an optimization object
      > static config stuff like lat/lng
      > reference to the desired rtm class
      > choose the parameter to optimize for
      > set up parallelization options

    give it a list of settings, plus a target for the optimizer

    [
        {
            'settings': {...},
            'target': 646.2,
        },
        {
            'settings': {...},
            'target': 647.7,
        },
        ...
    ]

    it gives back a list of values for the parameter

    [0.1, nan, ...]

    incalculable cases are returned nan.

"""

from copy import deepcopy
import logging
from numpy import nan
from fmm import zeroin, BadBoundsError, NoConvergeError
from rtm import RTMError


class Single_Optimizer(object):
    """
    Optimize a model for a target irradiance.

    Possible future extension: plug in a custom solver?
    """
    
    def __init__(self, parameter, bounds, tolerance,
        irradiance='global'):
        """
        parameter: a model config setting that the particular rtm supports.
        bounds: a two-elemnt tuple defining some x which bound the solution.
        a solution returned will be within +/- tolerance + epsilon of whatever
        target irradiance is passed to optimize.
        """
        self.parameter = parameter
        self.bounds = bounds
        self.tolerance = tolerance
        self.irradiance = irradiance

    def optimize(self, model, target_irradiance):
        self.meta = {
            'model': dict(model),
            'parameter': self.parameter,
            'target_irradiance': target_irradiance,
            'iterations': {},
            }

        def f(x):
            model.update({self.parameter: x})
            diff = model.irradiance[self.irradiance] - target_irradiance
            self.meta['iterations'].update({x: diff})
            return diff

        result = zeroin(self.bounds[0], self.bounds[1], f, self.tolerance)
        self.meta['model'].update({self.parameter: result})

        return result

    def clean_up(self):
        raise NotImplementedError


def _optimize(things_list):
    settings, target, model, optimizer, irradiance, output = things_list
    model.update(settings)
    try:
        answer = optimizer.optimize(model, target_irradiance=target)
    except (BadBoundsError, RTMError) as err:
        logging.error(err)
        return nan
    return answer


def optimize(settings_list, base_settings, rtm, parameter, map_func=map,
    tolerance=0.1, bounds=(0,1), irradiance='global', output='aod'):
    model = rtm(base_settings)
    optimizer = Single_Optimizer(parameter, bounds, tolerance)
    things_list = [
        [item['settings'], item['target'], model, optimizer,
        irradiance, output] for item in settings_list
    ]
    return map_func(_optimize, things_list)
