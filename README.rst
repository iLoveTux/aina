=====
flume
=====


.. image:: https://img.shields.io/pypi/v/flume.svg
        :target: https://pypi.python.org/pypi/flume

.. image:: https://img.shields.io/travis/ilovetux/flume.svg
        :target: https://travis-ci.org/ilovetux/flume

.. image:: https://readthedocs.org/projects/flume/badge/?version=latest
        :target: https://flume.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Let the logs flow

Flume is a general-purpose stream processing framework. It includes
a simple but powerful templating system and all the utilities
to shape your data streams.

* Free software: GNU General Public License v3
* Documentation: https://flume.readthedocs.io.


Features
--------

* Simple, Powerful templating system
* Extensible input and output system
  * TODO: Many default use cases covered
* Command line utilities
* Web GUI

Installing
----------

Simply, issue the following command::

  $ pip install flume

Concepts
--------

The built-in templating engine is very simple, it consists
of a namespace and a template. The template is rendered within
the context of the namespace.

Rendering involves two stages:

  1. scanning the template for strings matching the pattern `{%<Expression>%}`
     where `<Expression>` is Python source code which is executed (`exec`)
     within the context of the namespace and removed from the output.
  2. scanning the remaining output for strings matching the pattern
     `{{<Statement>}}` where `<Statement>` is a Python statement which
     is replaced (along with `{{` and `}}`) with the value to which
     it evaluates (`eval`)

This concept is applied to a variety of use cases and embodied in the form of
command line utilities which cover a number of common use cases.

Usage
-----

In order to use flume, you must be familiar with the
following concepts a template is an instance Template
(or subclass) with the following attributes:

  * begin: a list of callables which are called at the
           when a template is created

Credits
-------

Author: iLoveTux
This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
