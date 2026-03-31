from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .errors import ValidationError
from .models import NormalizedBuild
from .parser_3mf import parse_bambu_3mf


@dataclass(slots=True)
class ConversionResult:
    input_path: str
    output_path: str
    schema: str
    part_count: int


def _validate(build: NormalizedBuild) -> None:
    if not build.parts:
        raise ValidationError("No parts were parsed from input.")
    for part in build.parts:
        if not part.mesh.vertices:
            raise ValidationError(f"Part {part.object_id} has no vertices.")
        if not part.mesh.triangles:
            raise ValidationError(f"Part {part.object_id} has no triangles.")


def convert_bambu_to_ifc(
    input_path: str | Path,
    output_path: str | Path,
    *,
    schema: str = "IFC4",
    zip_output: bool = False,
) -> ConversionResult:
    from .ifc_writer import write_ifc

    build = parse_bambu_3mf(input_path)
    _validate(build)
    out = write_ifc(build, output_path, schema=schema, zip_output=zip_output)
    return ConversionResult(
        input_path=str(input_path),
        output_path=str(out),
        schema=schema.upper(),
        part_count=len(build.parts),
    )
