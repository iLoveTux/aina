=====
aina
=====


.. image:: https://img.shields.io/travis/iLoveTux/aina.svg
        :target: https://travis-ci.org/iLoveTux/aina

.. image:: https://readthedocs.org/projects/aina/badge/?version=latest
        :target: https://aina.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

Aina is a general-purpose stream processing framework. It includes
a simple but powerful templating system which powers a versitle command
line utility.

NOTE: This is new code. Master is in flux and docs are lacking,
but it is in a point where it could be useful to someone. If
it is useful to you, help us get to 1.0.0. You can start by reading
the contributing guide at https://github.com/ilovetux/aina/CONTRIBUTING.rst.

* Free software: GNU General Public License v3
* Documentation: https://aina.readthedocs.io.


Features
--------

* Simple, Powerful templating system
* Command line utilities
* All the power of Python
* No hacks or magic
* Approachable source code
* Tested
* TODO: Web UI
* TODO: Many default use cases covered
* TODO: --no-overwrite option
* TODO: Improve test coverage

Installing
----------
You can install the latest stable version with the following command::

  $ pip install aina

Alternately, to clone the latest development version::

  $ git clone https://github.com/ilovetux/aina
  $ cd aina
  # Optional
  $ python setup.py test
  $ pip install .

Concepts
--------

The built-in templating engine is very simple, it consists
of a namespace and a template. The template is rendered within
the context of the namespace.

Rendering involves two stages:

  1. scanning the template for strings matching the pattern `{%<Source>%}`
     where `<Source>` is Python source code which is executed (`exec`)
     within the context of the namespace. During execution, stdout is
     captured. After execution, `{%<Source>%}` is replaced with a string
     containing the output.
  2. scanning the remaining output for strings matching the pattern
     `{{<Expression>}}` where `<Expression>` is a Python expression which
     is replaced with the value to which it evaluates (`eval`)

As an example, let's look at the following template::

  {%
  me = "iLoveTux"
  name = "Bill"
  age = 35
  %}
  hello {{name}}:

  I heard that you just turned {{str(age)}}. Congratulations!

  Sincerely:

  {% print(me) %}

If this were rendered, the output would be as follows::

  Hello Bill,

  I heard that you just turned 35. Congratulations!

  Sincerely:

  iLoveTux

This concept is applied to a variety of use cases and embodied in the form of
command line utilities which cover a number of common use cases.

Usage
-----

Aina can be used directly from within Python, like so::

  from aina import render

  namespace = {"foo": "bar"}
  template = "The value of foo is {{foo}}"

  result = render(template, namespace)

This usage has first-class support, but a much handier solution is to use
the provided CLI.

The command line utility, aina, can be run in two modes:

  1. Streaming mode: Data is streamed through and used to populate templates
  2. Document mode: Render files src and write the results to dst

Streaming mode
==============

Streaming mode runs in the following manner:

  1. Accept a list of `filenames` (wildcards are accepted), which defaults to stdin
  2. At this point any expressions passed to `--begins` are executed
  3. The files specified are processed in order
    1. Any expressions passed to `--begin-files` are executed
    2. The data from the current file is read line-by-line
      1. Any statements passed to `--tests` are evaluated
      2. Iff all tests pass, the following process is performed.
        1. Any expressions passed to `--begin-lines` are executed
        2. Any templates are rendered through the python logging system
      3. Any expressions passed to `--end-lines` are executed
    3. Any expressions passed to `--end-files` are executed
  4. Any expressions passed to `--ends` are executed

Below are a few examples. See the documentation for more details::

  # Like grep
  $ aina stream --test "'error' in line.lower()" --template "{{line}}" *.log

  # Like wc -l
  $ aina stream --end-files "print(fnr, filename)" *.log

  # Like wc -wl
  $ aina stream --begins "words=0" --begin-lines "words += nf" --end-files "print(words, fnr, filename)"

  # Find all numbers "\d+" for each line
  $ aina stream --begins "import re" --begin-lines "print(re.findall(r'\d+', line))" *.log

  # Run an XPath
  $ aina stream --begins "from lxml import etree" --begin-lines "tree = etree.fromstring(line)" --templates "{{"\n".join(tree.xpath("./*"))}}"

Please see the documentation for more as well as trying::

  $ aina stream --help

Important Note:

If anything passed to any of the hooks is determined to exist by `os.path.exists`
then it will be read and executed as if that text was passed in on the CLI. This
is useful for quickly solving character escaping issues.

Document mode
-------------

Document mode renders one or more files and/or directories `src` to
another location `dst`. It is used like this::

  $ aina doc <src> <dst>

There are options to control behavior, but the gist of it is:

  1. if src is a file
    1. if dst is a filename, src is rendered and written to dst
    2. if dst is a directory, src is rendered and written to a file in dst with the same basename as src
  2. if src is a directory
    1. dst must be a directory and every file in src is rendered into a file in dst with the same basename as the file from src
    2. If `--recursive` is specified, the subdirectories will be reproduced in dst

Some important notes:

* File and directory names can be templated
* If `--interval` is passed an integer value, the program will sleep for that many seconds and check for changes to your templates (based on the file's mtime) in which case they will be re-rendered

Use Cases
---------

Streaming mode is great for processing incoming log files with `tail --follow=name`
or for ad-hoc analysis of text files.

Document mode is incredibly useful for a powerful configuration templating
system. The `--interval` option is incredibly useful as it will only re-render
on a file change, so is great for developing your templates as you can view
the results in near-real-time.

Document mode is also useful for near-real-time rendering of static
web resources such as charts, tables, dashboards and more.

If you find any more use cases, please open an issue or pull request to add it
here and in the wiki

Credits
-------

Author: iLoveTux
This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
