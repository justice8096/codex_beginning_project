from __future__ import annotations

from pathlib import Path
import uuid

import pytest

ifcopenshell = pytest.importorskip("ifcopenshell")

from bambu2ifc.ifc_writer import write_ifc
from bambu2ifc.models import BuildMetadata, Mesh, NormalizedBuild, Part


def _artifact_dir() -> Path:
    path = Path(__file__).resolve().parents[1] / ".test_artifacts"
    path.mkdir(exist_ok=True)
    return path


def test_writer_creates_ifc_with_expected_entities():
    build = NormalizedBuild(
        parts=[
            Part(
                object_id="1",
                name="SamplePart",
                mesh=Mesh(
                    vertices=[(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (0.0, 10.0, 0.0)],
                    triangles=[(0, 1, 2)],
                ),
            )
        ],
        metadata=BuildMetadata(
            source_file="sample.3mf",
            unit="millimeter",
            extras={"printer": "Bambu X1C"},
        ),
    )
    out = write_ifc(build, _artifact_dir() / f"writer_{uuid.uuid4().hex}.ifc", schema="IFC4")
    model = ifcopenshell.open(str(out))

    assert len(model.by_type("IfcProject")) == 1
    assert len(model.by_type("IfcBuildingElementProxy")) == 1
    assert len(model.by_type("IfcPropertySet")) >= 1
