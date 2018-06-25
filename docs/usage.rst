=====
Usage
=====
In streaming mode, your templates and hooks are `eval`uated or `exec`uted
within an single, shared namespace. This namespace is injected with the
following variables at various times throughout processing:

  * `filename`: The filename currently being processed
  * `line`: The text of the current line
  * `fields`: The result of calling `line.split(field_sep)`
  * `nr`: The number of the current record being processed
  * `fnr`: The number of the current record within the current file
  * `nf`: The result of `len(line.split(field_sep))`


to run in streaming mode, use the stream subcommand. Here is an example
of a command which is similar to grep::

  $ aina stream --test "'error' in line.lower()" --template {{line}} *.log

Here is a command which outputs the number of lines in each file::

  $ aina stream --end-files "print(fnr, filename)" *.log

Here is an updated example which also prints out the word count::

  $ aina stream --begins "words=0" --begin-lines "words += nf" --end-files "print(words, fnr, filename)"

Everything that looks advanced is literally just Python, so it's easy
to pick up and batteries are included. Imports work just fine and there is
no magic. Here is an example which uses the `re` module find the count of
numbers::

  $ aina stream --begins "import re" --begin-lines "print(re.findall(r'\d+', line))" *.log

A list of the hooks you can tie into are, If more than any are provided, they
are processed in the order given. If a filename is given and is said to exist by
`os.path.exists`, then that file is read in and executed by ``runpy.run_path``:

If Python source code is provided, then that is `exec`uted.

  * --begins: Executed once at startup.
  * --begin-files: Executed once for each file processed.
  * --begin-lines: Executed once for each line processed. These hooks are only
                   executed if all tests specified by `--tests` evaluate to
                   Truthy values.
  * --end-lines: Executed once after any processing of line is complete.
                 end-lines are rendered regardless of the results of `--tests`.
  * --end-files:  Executed once after processing is complete for each file.
  * --ends: Executed once after all lines are complete. This means that
            either all files are exhausted or `Ctrl + C` has been pressed.

Other parameters:

  * --tests: Each of these are `eval`uated when a new line is received.
             if and only if all tests provided evaluate to Truthy values
             processing of the line will continue otherwise processing is
             continued with the next line.
  * --templates: Templates are treated differently. Templates are rendered
                 once per line according to the rules defined above in
                 "Concepts". The result of each rendering is put out to a
                 logger unique to that template. This allows the Python
                 `logging.config` package to provide a very fine grain of
                 control. The main use case for this is to extract information
                 according to a variety of KPI and output to multiple
                 destinations, while also maintaining a record of authority.

Document mode
=============

In document mode, your templates reside in files and are read from `src`
and written to `dst`.The behavior differs depending on the values provided
for `src` and `dst`.

If `src` is a directory or multiple values are provided for `src`
then `dst` must be a directory in which case all files in `src` will
be rendered into `dst`. If `--recursive` is specified then files will
be rendered recursively from subdirectories within `src`.

If `src` is a file then `dst` can be either a directory or a filename. If a
filename is provided then `src` will be rendered into that file, otherwise
if a directory is provided for `dst` then a file with the same name as `src`
will be created.

If `--interval` is specified, then after all files are rendered the process
will sleep for the specified interval. When the process awakens again all files
in `src` will be examined and if any have changed then that file is re-rendered
into `dst`. Said process will continue indefinately until the process is killed,
ie by pressing `Ctrl + C`.

To use aina in a project::

    from aina.render import render
