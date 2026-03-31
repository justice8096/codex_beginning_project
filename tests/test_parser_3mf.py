from __future__ import annotations

from pathlib import Path
import zipfile
import uuid

from bambu2ifc.parser_3mf import parse_bambu_3mf


def _write_minimal_3mf(path: Path) -> None:
    model_xml = """<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
  <metadata name="printer">Bambu X1C</metadata>
  <resources>
    <object id="1" name="Cube">
      <mesh>
        <vertices>
          <vertex x="0" y="0" z="0"/>
          <vertex x="10" y="0" z="0"/>
          <vertex x="0" y="10" z="0"/>
        </vertices>
        <triangles>
          <triangle v1="0" v2="1" v3="2"/>
        </triangles>
      </mesh>
    </object>
  </resources>
  <build>
    <item objectid="1" transform="1 0 0 5 0 1 0 6 0 0 1 7"/>
  </build>
</model>
"""
    with zipfile.ZipFile(path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("3D/3dmodel.model", model_xml)
        zf.writestr("[Content_Types].xml", "")
        zf.writestr("_rels/.rels", "")


def _artifact_dir() -> Path:
    path = Path(__file__).resolve().parents[1] / ".test_artifacts"
    path.mkdir(exist_ok=True)
    return path


def test_parse_3mf_extracts_geometry_and_metadata():
    path = _artifact_dir() / f"minimal_{uuid.uuid4().hex}.3mf"
    _write_minimal_3mf(path)
    build = parse_bambu_3mf(path)

    assert len(build.parts) == 1
    assert build.metadata.unit == "millimeter"
    assert build.metadata.extras["printer"] == "Bambu X1C"
    assert len(build.parts[0].mesh.vertices) == 3
    assert len(build.parts[0].mesh.triangles) == 1
    assert build.parts[0].transform[3] == 5.0
    assert build.parts[0].transform[7] == 6.0
    assert build.parts[0].transform[11] == 7.0
