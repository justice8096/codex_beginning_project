from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


Vec3 = tuple[float, float, float]
Tri = tuple[int, int, int]
Matrix3x4 = tuple[
    float, float, float, float,
    float, float, float, float,
    float, float, float, float,
]


IDENTITY_3X4: Matrix3x4 = (
    1.0, 0.0, 0.0, 0.0,
    0.0, 1.0, 0.0, 0.0,
    0.0, 0.0, 1.0, 0.0,
)


@dataclass(slots=True)
class Mesh:
    vertices: list[Vec3]
    triangles: list[Tri]


@dataclass(slots=True)
class Part:
    object_id: str
    name: str | None
    mesh: Mesh
    transform: Matrix3x4 = IDENTITY_3X4


@dataclass(slots=True)
class BuildMetadata:
    source_file: str
    unit: str = "millimeter"
    extras: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class NormalizedBuild:
    parts: list[Part]
    metadata: BuildMetadata


def apply_transform(vertices: Sequence[Vec3], matrix: Matrix3x4) -> list[Vec3]:
    """Apply a 3MF 3x4 matrix to vertices."""
    a, b, c, d, e, f, g, h, i, j, k, l = matrix
    out: list[Vec3] = []
    for x, y, z in vertices:
        out.append(
            (
                a * x + b * y + c * z + d,
                e * x + f * y + g * z + h,
                i * x + j * y + k * z + l,
            )
        )
    return out
