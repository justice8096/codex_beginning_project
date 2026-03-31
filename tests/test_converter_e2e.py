from __future__ import annotations

from pathlib import Path
import zipfile

import pytest

ifcopenshell = pytest.importorskip("ifcopenshell")

from bambu2ifc.converter import convert_bambu_to_ifc


def _write_minimal_3mf(path: Path) -> None:
    model_xml = """<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
  <resources>
    <object id="1" name="TriPart">
      <mesh>
        <vertices>
          <vertex x="0" y="0" z="0"/>
          <vertex x="5" y="0" z="0"/>
          <vertex x="0" y="5" z="0"/>
        </vertices>
        <triangles>
          <triangle v1="0" v2="1" v3="2"/>
        </triangles>
      </mesh>
    </object>
  </resources>
  <build>
    <item objectid="1"/>
  </build>
</model>
"""
    with zipfile.ZipFile(path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("3D/3dmodel.model", model_xml)
        zf.writestr("[Content_Types].xml", "")
        zf.writestr("_rels/.rels", "")


def test_e2e_convert_minimal_file(tmp_path: Path):
    input_path = tmp_path / "in.3mf"
    output_path = tmp_path / "out.ifc"
    _write_minimal_3mf(input_path)

    result = convert_bambu_to_ifc(input_path, output_path, schema="IFC4")
    assert result.part_count == 1
    assert Path(result.output_path).exists()

    model = ifcopenshell.open(result.output_path)
    assert len(model.by_type("IfcBuildingElementProxy")) == 1
