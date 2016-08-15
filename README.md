[![Build Status](https://travis-ci.org/joshvillbrandt/goprohero.svg?branch=master)](https://travis-ci.org/joshvillbrandt/goprohero) [![Documentation Status](https://readthedocs.org/projects/goprohero/badge/?version=latest)](http://goprohero.readthedocs.org/en/latest/)

# goprohero

A Python3 library for controlling GoPro Hero 3 and 3+ cameras over http.

## Description

This package includes a both a library and a command line interface that can interface with GoPro HERO3, and HERO3+ cameras over http. It is an update from [goprohero](https://github.com/joshvillbrandt/goprohero) since firmware 3.0 contains breaking changes to the HTTP API. If you think there are missing commands or would like to submit a pull request, have a look at [goprowifihack](https://github.com/KonradIT/goprowifihack/blob/master/HERO4.md) for a list of all the commands on API 3.

The library can be used to set any of the configurable options of the camera and can also interpret the camera's status details. OpenCV (if installed) is used to open the live stream and save a single frame.

The command line interface utilizes the [wireless](https://github.com/joshvillbrandt/wireless) library to control one or more cameras from a single command.

For more advanced management of multiple cameras, check out the [GoProController](https://github.com/joshvillbrandt/GoProController) and [GoProControllerUI](https://github.com/joshvillbrandt/GoProControllerUI) packages which allow for command queuing and status history as well as an interface to view the live stream image captures.

Requirements:

* Python 3.4 or higher
* GoPro HERO3 or GoPro HERO3+
* A computer with a wireless card
* (optional) OpenCV for live streaming

## Documentation

Documentation for the original goprohero project is available on [readthedocs.org](http://goprohero.readthedocs.org/en/latest/).
