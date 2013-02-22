=====================================
pykarotz - Python interface to Karotz
=====================================

About
-----

A (work-in-progress) Python library which provides object-oriented access to
the REST-API for `Karotz`_::

                       _           _    ________________________________
                      / \         / \ /                                 \
                      \  \       /  / | https://github.com/esc/pykarotz |
                       \  \     /  /  \____  ___________________________/
                        \  \___/  /       /_/
                 _      /         \  _
     _ __  _   _| | ___|__ O __O___|| |_ ____
    | '_ \| | | | |/ / _` | '__/ _ \| __|_  /
    | |_) | |_| |   < (_| | | | (_) | |_ / /
    | .__/ \__, |_|\_\__,_|_|  \___/ \__/___|
    |_|    |___/       |           |
                        \_________/

.. _`Karotz`: http://www.karotz.com/home

Dependencies
------------

* `lxml <http://lxml.de/>`_

Installation
------------

Place the ``karotz.py`` file where you want to use it.
egg in progress

Getting Started
---------------

First, you must register an interactive application and install this on the
target Karotz. For now, you can find some great instructions on the `Ruby API
blog-post <http://blog.nofail.de/2011/12/karotz-ruby-love/>`_.

After doing this, you will have the access credentials ``INSTALL_ID``,
``API_KEY`` and a ``SECRET``. You have several ways to use these with
``pykarotz``. The easiest is to place the configuration in a configuration file
(standard INI format) in your home directory ``$HOME/.pykarotz``, for example::

    [karotz-app-settings]
    apikey = 23426660-beef-beee-baad-food0000babe
    secret = 23426660-beef-beee-baad-food0000babe
    installid = 23426660-beef-beee-baad-food0000babe

If you have done everything correctly, you can establish a connection and demo
the available colors from an interactive Python prompt using::

    >>> import karotz as kz
    >>> krtz = kz.Karotz()
    >>> krtz.led.demo()
    >>> krtz.stop()

In case you have placed the file somewhere else, for example if you are using
Windows and have placed the file at ``C:\pykarotz.txt``, you can initialise the
``Karotz`` class using::

    >>> import karotz as kz
    >>> settings = kz.parse_config(config_filename="C:\pykarotz.txt")
    >>> krtz = kz.Karotz(settings=settings)

If instead, you want to hardcode the settings in your Python source file, you
can do something like::

    >>> import karotz as kz
    >>> settings['apikey'] = "23426660-beef-beee-baad-food0000babe"
    >>> settings['installid'] = "23426660-beef-beee-baad-food0000babe"
    >>> settings['secret'] = "23426660-beef-beee-baad-food0000babe"
    >>> krtz = kz.Karotz(settings=settings)

If you have multiple units, you can save their settings in different sections::

    [karotz-one]
    apikey = 23426660-beef-beee-baad-food0000babe
    secret = 23426660-beef-beee-baad-food0000babe
    installid = 23426660-beef-beee-baad-food0000babe
    [karotz-two]
    apikey = 23426660-beef-beee-baad-food0000babe
    secret = 23426660-beef-beee-baad-food0000babe
    installid = 23426660-beef-beee-baad-food0000babe

And then use the keyword argument `section` to load them::

    >>> import karotz as kz
    >>> krtz1 = kz.Karotz(kz.parse_config(section='karotz-one'))
    >>> krtz2 = kz.Karotz(kz.parse_config(section='karotz-two'))

API
---

Currently the following REST API calls are supported:

* Ears
* Led
* TTS
* Config
* Mutimedia
* Video

You can access them in an object oriented fashion using ``kz.ears``, ``kz.led``
and ``kz.tts``::

    >>> import karotz as kz
    >>> krtz = kz.Karotz()
    >>> krtz.ears.sad()
    >>> krtz.led.light(kz.PURPLE)
    >>> krtz.tts.speak('Why is the world so evil?')
    >>> krtz.stop()

Examples
--------

See the directory ``examples`` for some example applications.:

* ``examples/kznotify``: Command line notification
  (`Direct link via GitHub <https://github.com/esc/pykarotz/blob/master/examples/kznotify>`_)

* ``examples/kzambient``: Ambient light source
  (`Direct link via GitHub <https://github.com/esc/pykarotz/blob/master/examples/kzambient>`_ )

Testing
-------

Install `nose <http://readthedocs.org/docs/nose/en/latest/>`_ and then do::

    $ nosetests

Similar Projects
----------------

* `Ruby <https://github.com/phoet/karotz>`_
* `Php <http://wizz.cc/blog/index.php?post/2011/04/12/Karotz-Php-Class>`_

Links
-----

* `Developer Pages (APIs etc..) <http://dev.karotz.com/>`_
* `Google group 'KarotzDev' <http://groups.google.com/group/karotzdev>`_
* `Karotz Wiki <http://wiki.karotz.com/index.php/Main_Page>`_


Author, Copyright and License
-----------------------------

| (C) 2012 Valentin 'esc' Haenel `<esc@zetatech.org>`, Franck Roudet

pykarotz is licensed under the terms of the MIT License.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
