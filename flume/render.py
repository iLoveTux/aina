from textwrap import dedent
from hashlib import sha256
import click
import re

statements = re.compile(r"(\{\{(.*?)\}\})", re.DOTALL)
expressions = re.compile(r"(\{%(.*?)%\})", re.DOTALL)

def render(template, namespace=None):
    global cache
    if namespace is None:
        namespace = {}

    out = template
    for expression in expressions.findall(out):
        exec(dedent(expression[1]).strip(), namespace)
        out = out.replace(expression[0], "")
    for statement in statements.findall(out):
        out = out.replace(
            statement[0],
            eval(dedent(statement[1]).strip(), namespace)
        )
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
