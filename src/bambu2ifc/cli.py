from __future__ import annotations

import argparse
import sys

from .converter import convert_bambu_to_ifc
from .errors import Bambu2IfcError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bambu2ifc",
        description="Convert a Bambu .3mf build file into IFC BIM format.",
    )
    parser.add_argument("input", help="Input Bambu build file (.3mf)")
    parser.add_argument("-o", "--output", required=True, help="Output IFC path (.ifc or .ifczip)")
    parser.add_argument(
        "--schema",
        default="IFC4",
        choices=["IFC4", "IFC2X3"],
        help="IFC schema version (default: IFC4)",
    )
    parser.add_argument(
        "--zip",
        action="store_true",
        help="Force compressed IFC output (.ifczip).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = convert_bambu_to_ifc(
            args.input,
            args.output,
            schema=args.schema,
            zip_output=args.zip,
        )
    except Bambu2IfcError as exc:
        print(f"Conversion failed: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover
        print(f"Unexpected failure: {exc}", file=sys.stderr)
        return 3

    print(
        f"Converted {result.input_path} -> {result.output_path} "
        f"({result.schema}, parts={result.part_count})"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
