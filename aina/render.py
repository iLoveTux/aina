from textwrap import dedent
from hashlib import sha256
import logging
import click
import re

statements = re.compile(r"(\{\{(.*?)\}\})", re.DOTALL)
expressions = re.compile(r"(\{%(.*?)%\})", re.DOTALL)

def render(template, namespace=None):
    global cache
    if namespace is None:
        logging.info("No namespace given, creating empty namespace")
        namespace = {}

    out = template
    for expression in expressions.findall(out):
        logger.debug("Found expression {}, executing with namespace: {}".format(expression[1], namespace))
        exec(dedent(expression[1]).strip(), namespace)
        logger.debug("Namespace after executing: {}".format(namespace))
        out = out.replace(expression[0], "")
        logger.debug("output so far: {}".format(out))
    for statement in statements.findall(out):
        logger.debug("Found statement {}, evaluating with namespace: {}".format(statement[1], namespace))
        out = out.replace(
            statement[0],
            eval(dedent(statement[1]).strip(), namespace)
        )
        logger.debug("output so far: {}".format(out))
    return out

if __name__ == "__main__":
    print(render("pre: {% x = 2 %}: post"))
    try:
        # Won't work:
        print(render("{{str(x)}}"))
    except:
        print("Got exception")
    # Will work
    namespace = {}
    print(render("pre: {% x = 2 %}: post", namespace))
    print(render("{{str(x)}}", namespace))
