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

"""Generate cmdt.py, with all available Type IDs"""
import os
import sys

from maya.api import OpenMaya as om
from maya import standalone, cmds


def main(fname=None):
    standalone.initialize()

    blacklist = (
        # Causes crash (Maya 2018)
        "caddyManipBase",

        # Causes TypeError
        "applyAbsOverride",
        "applyOverride",
        "applyRelOverride",
        "childNode",
        "lightItemBase",
        "listItem",
        "override",
        "selector",
        "valueOverride",
    )

    cmdt = [
        "from maya.api import OpenMaya as om",
        ""
    ]

    dg = om.MFnDependencyNode()
    for name in cmds.allNodeTypes():
        if name in blacklist:
            continue

        try:
            mobj = dg.create(name)
            print(mobj.apiType())
            fn = om.MFnDependencyNode
            try:
                # If `name` is a shape, then the transform
                # is returned. We need the shape.
                mobj = om.MFnDagNode(mobj).child(0)
            except RuntimeError:
                pass

        except TypeError:
            # This shouldn't happen, but might depending
            # on the Maya version, and if there are any
            # custom plug-ins registereing new (bad) nodes.
            #
            # If so:
            #   Add to `blacklist`
            #
            sys.stderr.write("%s threw a TypeError\n" % name)
            continue

        typeId = fn(mobj).typeId
        cmdt += ["{type} = om.MTypeId({id})".format(
            type=name[0].upper() + name[1:],
            id=str(typeId))
        ]

    text = os.linesep.join(cmdt)

    dirname = os.path.dirname(__file__)
    fname = fname or os.path.join(dirname, "cmdt.py")
    with open(fname, "w") as f:
        f.write(text)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--fname", default="")
    opt = parser.parse_args()
    main(opt.fname)
