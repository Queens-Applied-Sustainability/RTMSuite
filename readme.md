RTMSuite
========

Time-series atmospheric data in -> optimized AOD and cloud thickness and spectrum out.


Setting Up
----------


You'll want to have RTM set up to make use of any of this
https://github.com/Queens-Applied-Sustainability/PyRTM

Create a directory some where.

You'll need to reate an `info.yaml` file there containing global settings. At a bare minimum it should look like this:

```yaml
latitude: 39.74
longitude: -105.18
```

Valid settings are any of those found in rtm.settings (https://github.com/Queens-Applied-Sustainability/PyRTM/blob/master/rtm/settings.py).

Settings in `info.yaml` will be applied globally to the rtm models. Global settings take a low precedence and will be overridden by anything also defined in the time-series CSV.



Testing
-------

Use nose, and for a quick check run `nosetests -a '!slow'`.

`nosetests` alone will run all tests including ones using `sbdart`, which
takes ages.
