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
    log = logging.getLogger(__name__)
    for expr in exprs:
        _expr = render(expr, namespace)
        if os.path.isfile(_expr):
            log.debug("{} is a file, executing...".format(_expr))
            namespace.update(runpy.run_path(_expr, init_globals=namespace))
        else:
            log.debug("Executing {}".format(_expr))
            exec(_expr, namespace)

def make_namespace(namespace, namespaces, add_env):
    if add_env:
        namespace.update(os.environ)
    if namespaces is not None:
        for _namespace in namespaces:
            with open(_namespace, "r") as fin:
                namespace.update(eval(fin.read(), namespace))
    return namespace

def render_directory(src, dst, recursive, namespace):
    log = logging.getLogger(__name__)
    src = Path(render(src, namespace))
    dst = Path(render(dst, namespace))
    for root, dirs, filenames in os.walk(str(src), topdown=True):
        log.debug("In directory: {}".format(root))
        for filename in filenames:
            filename = Path(os.path.join(root, filename))
            log.debug("Found file {}".format(filename))
            _dst = os.path.join(str(dst), os.path.relpath(str(filename), str(src)))
            render_file(filename, _dst, namespace)
        if recursive:
            for dirname in dirs:
                new_dir = Path(dst / dirname)
                log.debug("Recursive, rendering to {}".format(new_dir))
                new_dir.mkdir(parents=True, exist_ok=True)
        else:
            log.debug("Not recursive, exiting")
            dirs.clear()

mtimes = {}
def render_file(src, dst, namespace):
    log = logging.getLogger(__name__)
    dst = Path(dst)
    src = Path(src)
    if src not in mtimes or src.stat().st_mtime != mtimes[src]:
        log.warn("Rendering {} -> {}".format(src, dst))
        try:
            dst.write_text(render(src.read_text(), namespace))
        finally:
            mtimes[src] = src.stat().st_mtime
    else:
        log.debug("File {} has not changed, skipping".format(src))
        pass

@cli.command("doc")
@click.argument("src")
@click.argument("dst")
@click.option("--interval", "-i", default=0, type=int)
@click.option("--recursive", "-R", is_flag=True, default=False)
@click.option("--namespaces", "-N", default=None, type=str, multiple=True)
@click.option("--add-env", "-E", default=False, is_flag=True)
@click.option("--begins", "-b", multiple=True)
@click.option("--ends", "-e", multiple=True)
@click.option("--logging-config", "-L")
@click.option("--logging-level", default=30)
@click.option("--logging-format", default="%(message)s")
def doc(
        src,
        dst,
        interval,
        recursive,
        namespaces,
        add_env,
        begins,
        ends,
        logging_config,
        logging_level,
        logging_format,
    ):
    """Render a set of template documents `src` to detination `dst`
    with a persistent namespace"""
    if logging_config:
        with open(logging_config, "r") as fp:
            logging.config.dictConfig(eval(fp.read()))
    else:
        logging.basicConfig(
            stream=sys.stdout,
            level=logging_level,
            format=logging_format,
        )
    log = logging.getLogger(__name__)
    if begins is None:
        begins = []
    if ends is None:
        ends = []
    namespace = {}
    _exec_list(begins, namespace)
    namespace.update(make_namespace(namespace, namespaces, add_env))
    src, dst = map(Path, (src, dst))
    src = src.resolve()
    while True:
        if src.is_dir():
            log.debug("src is directory: {}".format(src))
            if not dst.is_dir():
                raise ValueError("If src is a directory, dst must also be a directory")
            render_directory(src, dst, recursive, namespace)
        elif src.is_file():
            log.debug("src is file: {}".format(src))
            if dst.exists() and dst.is_dir():
                dst = dst / src.name
                log.debug("dst is directory, rendering to: {}".format(dst))
            elif not dst.parent.exists():
                log.debug("{} does not exist, creating...")
                dst.parent.mkdir(parents=True, exist_ok=True)
            render_file(src, dst, namespace)
        else:
            raise ValueError("src must be either a file or directory.")
        if interval <= 0:
            break
        sleep(interval)
    _exec_list(ends, namespace)
    return 0


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

    log = logging.getLogger(__name__)
    if add_paths is None:
        add_paths = []
    for path in add_paths:
        if os.path.exists(path):
            sys.path.insert(0, path)
        else:
            log.critical("{} not found, invalid path".format(path))
            sys.exit(-2)
    namespace = make_namespace({}, namespaces, add_env)
    if not filenames:
        log.debug("No filenames specified, defaulting to stdin")
        filenames = ["-"]
    _filenames = []
    for filename in filenames:
        if filename == "-":
            _filenames.append("-")
        else:
            _filenames.extend(glob(filename, recursive=recursive))
    filenames = list(filter(lambda x: not os.path.isdir(x), _filenames))
    log.debug("Reading filenames {}".format(filenames))
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
                log.debug("Reading {}".format(filename))
                for line in fin:
                    log.debug("Got line: {}".format(line))
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
                        "line": line.decode(),
                        "filename": os.path.abspath(filename),
                        "fields": fields,
                        "nf": len(fields),
                        "nr": nr,
                        "fnr": fnr,
                    })
                    if all(eval(render(test, namespace), namespace) for test in tests):
                        _exec_list(begin_lines, namespace)
                        for template in templates:
                            log.debug("Rendering template: {}".format(template))
                            try:
                                results = render(template, namespace).strip()
                            except:
                                if not suppress_tracebacks:
                                    log.exception("An unhandled exception occurred")
                                continue
                            log.debug("Result: {}".format(results))
                            if results:
                                log.info(results)
                    _exec_list(end_lines, namespace)
            _exec_list(end_files, namespace)
        except:
            if not suppress_tracebacks:
                log.exception("An unhandled exception occurred")
            continue
    _exec_list(ends, namespace)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
