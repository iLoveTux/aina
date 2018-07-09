from textwrap import dedent
from hashlib import sha256
import logging
import click
import sys
import re
from io import StringIO
import contextlib

@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

expressions = re.compile(r"(\{\{(.*?)\}\})", re.DOTALL)
statements = re.compile(r"(\{%(.*?)%\})", re.DOTALL)

def render(template, namespace=None):
    global cache
    if namespace is None:
        logging.info("No namespace given, creating empty namespace")
        namespace = {}

    out = str(template)
    for expression in statements.findall(out):
        logging.info("Found expression {}".format(expression[1]))
        with stdoutIO() as output:
            exec(dedent(expression[1]).strip(), namespace)
            out = out.replace(expression[0], output.getvalue())
            logging.info("output so far: {}".format(out))
    for statement in expressions.findall(out):
        logging.debug("Found statement {}".format(statement[1]))
        out = out.replace(
            statement[0],
            str(eval(dedent(statement[1]).strip(), namespace))
        )
        logging.debug("output so far: {}".format(out))
    return out

if __name__ == "__main__":
    pass
