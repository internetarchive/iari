#!/usr/bin/env python3
"""Build a Tapestry-importable .zip from a JSON spec.

Usage:
    build-tapestry-zip.py spec.json output.zip

The spec is almost exactly the shape of a Tapestry export's root.json (see
tapestry-zip-authoring's SKILL.md for the full field reference), except:

  - `version`, `id`, `createdAt`, `updatedAt` may be omitted; this script fills
    them in (version is always forced to 7, the current schema).
  - Anywhere the real root.json wants a string that is either an external URL
    or a `file:/...`-prefixed reference to a bundled asset, this spec instead
    accepts either a plain string (kept as-is, treated as an external URL) or
    an object `{"bundle": "<path to a local file, relative to the spec file>"}`.
    The script reads that local file, places it in the zip under the correct
    naming convention, and rewrites the field to the matching `file:/...`
    value. This is true for: top-level `thumbnail`, every media item's
    `source`, and every thumbnail rendition's `source` (in
    `item.thumbnail.renditions[].source`).

This script does load-bearing structural validation (required fields per item
type, valid discriminants) but is NOT a substitute for the real app's Zod
validation on import — it exists to make the mechanical parts (zip entry
naming, `file:/` prefixing, version/id defaults) impossible to get wrong by
hand. See tapestry-zip-authoring's SKILL.md for everything this validates and
everything it deliberately leaves for the real importer to catch.
"""

import argparse
import json
import sys
import zipfile
from pathlib import Path

from tapestry_zip import SpecError, build


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("spec", help="Path to the JSON spec file")
    parser.add_argument("output", help="Path to write the .zip to")
    args = parser.parse_args()

    spec_path = Path(args.spec).resolve()
    spec = json.loads(spec_path.read_text())

    with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED) as zf:
        try:
            root = build(spec, spec_path.parent, zf)
        except SpecError as e:
            print(f"error: {e}", file=sys.stderr)
            sys.exit(1)

    print(f"wrote {args.output}")
    print(f"  title: {root.get('title')!r}")
    print(f"  items: {len(root['items'])}")
    print(f"  groups: {len(root['groups'])}  rels: {len(root['rels'])}  presentation steps: {len(root['presentation'])}")


if __name__ == "__main__":
    main()
