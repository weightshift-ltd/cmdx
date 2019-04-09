#!/usr/bin/env python

# Copyright 2019 WeightShift Ltd.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import io
import re


def parse(fname):
    """Return blocks of code as list of dicts

    Arguments:
        fname (str): Relative name of caveats file

    """

    blocks = list()
    with io.open(fname, "r", encoding="utf-8") as f:
        in_block = False
        current_block = None
        current_header = ""

        for number, line in enumerate(f):
            number += 1

            # Doctests are within a quadruple hashtag header.
            if line.startswith("### "):
                current_header = line.rstrip()

            # The actuat test is within a fenced block.
            if line.startswith("```"):
                in_block = False

            if in_block:
                current_block.append(line)

            if line.startswith("```python"):
                in_block = True
                current_block = list()
                current_block.append(current_header + " L%d" % number)
                blocks.append(current_block)

    tests = list()
    for block in blocks:
        header = (
            block[0].strip("# ")  # Remove Markdown
                    .rstrip()     # Remove newline
                    .lower()      # PEP08
        )

        # Remove unsupported characters
        header = re.sub(r"\W", "_", header)

        # Adding "untested" anywhere in the first line of
        # the doctest excludes it from the test.
        if "untested" in block[1].lower():
            continue

        tests.append({
            "header": header,
            "body": block[1:]
        })

    return tests


def format_(blocks):
    """Produce Python module from blocks of tests

    Arguments:
        blocks (list): Blocks of tests from func:`parse()`

    """

    tests = list()
    function_count = 0  # For each test to have a unique name

    for block in blocks:

        # Validate docstring format of body
        if not any(line[:3] == ">>>" for line in block["body"]):
            # A doctest requires at least one `>>>` directive.
            continue

        function_count += 1
        block["header"] = block["header"]
        block["count"] = str(function_count)
        block["body"] = "    ".join(block["body"])
        tests.append(u"""\

def test_{count}_{header}():
    '''Test {header}

    {body}
    '''

""".format(**block))

    return tests


if __name__ == '__main__':
    blocks = parse("README.md")
    tests = format_(blocks)

    # Write formatted tests
    # with open("test_docs.py", "w") as f:
    with io.open("test_docs.py", "w", encoding="utf-8") as f:
        f.write(u"""\
# -*- coding: utf-8 -*-
from nose.tools import assert_raises
from maya import standalone
standalone.initialize()

from maya import cmds
import cmdx

""")
        f.write("".join(tests))
