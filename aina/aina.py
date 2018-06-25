"""A command line utility designed to assist with modern
computing tasks.

There are two modes of operation, stream mode and doc mode.

When in stream mode, a set of templates are evaluated in a namespace
which is continually updated with new data from the stream. The templates
are rendered to stdout once per line in the stream, but can be redirectred
to a number of destinations based on the logging configuration. A number
of hooks are allowed, specifically `begins`, `begin_lines`, `end_lines`
and `end`. This is useful for and intended to help parse line-delimited
text files such as logs.

When in doc mode, a set of templates in the form of text files
are rendered from `src` to `dst`. This is useful for rendering
configuration, static web assets and more. An optional recursive
flag allows you to render entire directory structure (with
templated file and directory names).
"""
import os
import sys
import runpy
import click
import logging
from pathlib import Path
from aina.render import render
from glob import glob
from time import time, sleep
cli = click.Group()

def _exec_list(exprs, namespace):
    for expr in exprs:
        _expr = render(expr, namespace)
        if os.path.isfile(_expr):
            namespace.update(runpy.run_path(_expr, init_globals=namespace))
        else:
            exec(_expr, namespace)

def make_namespace(namespaces, add_env):
    namespace = {}
    if add_env:
        namespace.update(os.environ)
    if namespaces is not None:
        for _namespace in namespaces:
            with open(_namespace, "r") as fin:
                namespace.update(eval(fin.read()))
    return namespace

def render_directory(src, dst, namespace):
    src = Path(render(src, namespace))
    dst = Path(render(dst, namespace))
    for filename in src.iterdir():
        filename = filename.resolve()
        if filename.is_dir():
            if recursive:
                new_dir = Path(render(str(dst / item.name), namespace))
                new_dir.mkdir(parents=True, exists_ok=True)
                render_directory(filename, new_dir, recursive, namespace)
            else:
                pass
        elif item.is_file():
            render_file(item, dst / item.name, namespace)
        else:
            pass

def render_file(src, dst, namespace):
    dst = Path(dst)
    template = Path(src)
    try:
        dst.write_text(render(template.read_text(), namespace))
    except ValueError:
        print("Error rendering template")

@cli.command("doc")
@click.argument("src")
@click.argument("dst")
@click.option("--interval", "-i", default=0, type=int)
@click.option("--recursive", "-R", is_flag=True, default=False)
@click.option("--namespaces", "-N", default=None, type=str, multiple=True)
@click.option("--add-env", "-E", default=False, is_flag=True)
def doc(src, dst, interval, recursive, namespaces, add_env):
    """Render a set of template documents `src` to detination `dst`
    with a persistent namespace"""
    namespace = make_namespace(namespaces, add_env)
    src = render(src, namespace)
    dst = render(dst, namespace)
    src, dst = map(Path, (src, dst))
    src = src.resolve()
    if src.is_dir():
        if not dst.is_dir():
            raise ValueError("If src is a directory, dst must also be a directory")
        render_directory(src, dst, recursive, namespace)
    elif src.is_file():
        if dst.exists() and dst.is_dir():
            dst = dst / src.name
        elif not dst.parent.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
        render_file(src, dst, namespace)
    else:
        raise ValueError("src must be either a file or directory.")

@cli.command("stream")
@click.argument("filenames", nargs=-1)
@click.option("--add-paths", "-p", multiple=True)
@click.option("--templates", "-t", multiple=True)
@click.option("--begins", "-b", multiple=True)
@click.option("--begin-lines", "-B", multiple=True)
@click.option("--begin-files", multiple=True)
@click.option("--end-files", multiple=True)
@click.option("--tests", "-t", multiple=True)
@click.option("--end-lines", "-E", multiple=True)
@click.option("--ends", "-e", multiple=True)
@click.option("--field-sep", "-F", default=None)
@click.option("--namespaces", "-n", multiple=True)
@click.option("--recursive", "-R", default=False, is_flag=True)
@click.option("--with-filenames", "-f", default=False, is_flag=True)
@click.option("--logging-config", "-L")
@click.option("--logging-level", default=20)
@click.option("--logging-format", default="%(message)s")
@click.option("--suppress-tracebacks", is_flag=True, default=False)
@click.option("--add-env", "-E", default=False, is_flag=True)
def stream(
        filenames,
        add_paths,
        templates,
        begins,
        begin_lines,
        begin_files,
        end_files,
        tests,
        end_lines,
        ends,
        field_sep,
        namespaces,
        recursive,
        with_filenames,
        logging_config,
        logging_level,
        logging_format,
        suppress_tracebacks,
        add_env,
    ):
    """Pass streams of data through a processing/templating pipeline"""
    if logging_config:
        with open(logging_config, "r") as fp:
            logging.config.dictConfig(eval(fp.read()))
    else:
        logging.basicConfig(
            stream=sys.stdout,
            level=logging_level,
            format=logging_format,
        )

    if add_paths is None:
        add_paths = []
    for path in add_paths:
        if os.path.exists(path):
            sys.path.insert(0, path)
        else:
            print("{} not found, invalid path".format(path))
            sys.exit(-2)
    namespace = make_namespace(namespaces, add_env)
    if not filenames:
        filenames = ["-"]
    _filenames = []
    for filename in filenames:
        if filename == "-":
            _filenames.append("-")
        else:
            _filenames.extend(glob(filename, recursive=recursive))
    filenames = list(filter(lambda x: not os.path.isdir(x), _filenames))
    last_filename = None
    nr = 0
    if tests is None:
        tests = ["True"]
    if begins is None:
        begins = []
    if begin_lines is None:
        begin_lines = []
    if begin_files is None:
        begin_files = []
    if end_files is None:
        end_files = []
    if end_lines is None:
        end_lines = []
    if ends is None:
        ends = []
    _exec_list(begins, namespace)
    for filename in filenames:
        try:
            with click.open_file(filename, "rb") as fin:
                for line in fin:
                    if filename != last_filename:
                        if with_filenames:
                            print("===> {} <===".format(os.path.abspath(filename)))
                        namespace.update({"filename": os.path.abspath(filename)})
                        fnr = 0
                        _exec_list(begin_files, namespace)
                        last_filename = filename
                    fnr, nr = fnr + 1, nr + 1
                    fields = line.split(field_sep)
                    namespace.update({
                        "line": line,
                        "filename": os.path.abspath(filename),
                        "fields": fields,
                        "nf": len(fields),
                        "nr": nr,
                        "fnr": fnr,
                    })
                    if all(eval(render(test, namespace), namespace) for test in tests):
                        _exec_list(begin_lines, namespace)
                        for template in templates:
                            try:
                                results = render(template, namespace).strip()
                            except:
                                if not suppress_tracebacks:
                                    logging.getLogger("ERROR").exception("An unhandled exception occurred")
                                continue
                            if results:
                                logging.getLogger(
                                    "{}.{}.{}".format(
                                        __name__,
                                        filename,
                                        templates.index(template),
                                    )
                                ).info(
                                    results
                                )
                    _exec_list(end_lines, namespace)
            _exec_list(end_files, namespace)
        except:
            if not suppress_tracebacks:
                logging.getLogger(__name__).exception("An unhandled exception occurred")
            continue
    _exec_list(ends, namespace)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
