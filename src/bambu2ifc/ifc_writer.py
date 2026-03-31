from __future__ import annotations

from pathlib import Path
import time
import zipfile

import ifcopenshell
import ifcopenshell.guid

from .metadata import compact_metadata
from .models import Mesh, NormalizedBuild, apply_transform


SUPPORTED_SCHEMAS = {"IFC4", "IFC2X3"}


def _guid() -> str:
    return ifcopenshell.guid.new()


def _owner_history(model: ifcopenshell.file):
    person = model.create_entity("IfcPerson")
    org = model.create_entity("IfcOrganization", Name="bambu2ifc")
    person_org = model.create_entity(
        "IfcPersonAndOrganization",
        ThePerson=person,
        TheOrganization=org,
    )
    app = model.create_entity(
        "IfcApplication",
        ApplicationDeveloper=org,
        Version="0.1.0",
        ApplicationFullName="bambu2ifc",
        ApplicationIdentifier="bambu2ifc",
    )
    return model.create_entity(
        "IfcOwnerHistory",
        OwningUser=person_org,
        OwningApplication=app,
        ChangeAction="ADDED",
        CreationDate=int(time.time()),
    )


def _context_and_units(model: ifcopenshell.file):
    origin = model.create_entity("IfcCartesianPoint", (0.0, 0.0, 0.0))
    axis = model.create_entity("IfcAxis2Placement3D", origin)
    context = model.create_entity(
        "IfcGeometricRepresentationContext",
        "Model",
        "Model",
        3,
        1.0e-5,
        axis,
        None,
    )
    length_unit = model.create_entity("IfcSIUnit", None, "LENGTHUNIT", "MILLI", "METRE")
    units = model.create_entity("IfcUnitAssignment", [length_unit])
    return context, units, axis


def _create_face_model(model: ifcopenshell.file, mesh: Mesh):
    points = [model.create_entity("IfcCartesianPoint", v) for v in mesh.vertices]
    faces = []
    for v1, v2, v3 in mesh.triangles:
        loop = model.create_entity("IfcPolyLoop", [points[v1], points[v2], points[v3]])
        bound = model.create_entity("IfcFaceOuterBound", loop, True)
        faces.append(model.create_entity("IfcFace", [bound]))
    connected_face_set = model.create_entity("IfcConnectedFaceSet", faces)
    return model.create_entity("IfcFaceBasedSurfaceModel", [connected_face_set])


def _ifc_text(model: ifcopenshell.file, value: str):
    return model.create_entity("IfcText", value)


def _create_pset(model: ifcopenshell.file, owner_history, product, metadata: dict[str, str]):
    props = []
    for key, value in metadata.items():
        props.append(model.create_entity("IfcPropertySingleValue", key, None, _ifc_text(model, value), None))
    pset = model.create_entity(
        "IfcPropertySet",
        _guid(),
        owner_history,
        "Pset_BambuPrint",
        None,
        props,
    )
    model.create_entity(
        "IfcRelDefinesByProperties",
        _guid(),
        owner_history,
        "Bambu metadata",
        None,
        [product],
        pset,
    )


def write_ifc(
    build: NormalizedBuild,
    output_path: str | Path,
    *,
    schema: str = "IFC4",
    zip_output: bool = False,
) -> Path:
    schema = schema.upper()
    if schema not in SUPPORTED_SCHEMAS:
        raise ValueError(f"Unsupported schema: {schema}. Expected one of {sorted(SUPPORTED_SCHEMAS)}")

    out = Path(output_path)
    if zip_output and out.suffix.lower() != ".ifczip":
        out = out.with_suffix(".ifczip")

    model = ifcopenshell.file(schema=schema)
    owner_history = _owner_history(model)
    context, units, default_axis = _context_and_units(model)

    project = model.create_entity(
        "IfcProject",
        _guid(),
        owner_history,
        "Bambu Build Project",
        None,
        None,
        None,
        None,
        [context],
        units,
    )

    site = model.create_entity(
        "IfcSite",
        _guid(),
        owner_history,
        "Site",
        None,
        None,
        model.create_entity("IfcLocalPlacement", None, default_axis),
        None,
        None,
        "ELEMENT",
        None,
        None,
        None,
        None,
        None,
    )
    building = model.create_entity(
        "IfcBuilding",
        _guid(),
        owner_history,
        "Building",
        None,
        None,
        model.create_entity("IfcLocalPlacement", site.ObjectPlacement, default_axis),
        None,
        None,
        "ELEMENT",
        None,
        None,
        None,
    )
    storey = model.create_entity(
        "IfcBuildingStorey",
        _guid(),
        owner_history,
        "Storey",
        None,
        None,
        model.create_entity("IfcLocalPlacement", building.ObjectPlacement, default_axis),
        None,
        None,
        "ELEMENT",
        None,
    )

    model.create_entity("IfcRelAggregates", _guid(), owner_history, None, None, project, [site])
    model.create_entity("IfcRelAggregates", _guid(), owner_history, None, None, site, [building])
    model.create_entity("IfcRelAggregates", _guid(), owner_history, None, None, building, [storey])

    compact_meta = compact_metadata(build.metadata.extras)
    compact_meta["source_file"] = build.metadata.source_file
    compact_meta["unit"] = build.metadata.unit

    for idx, part in enumerate(build.parts):
        transformed = apply_transform(part.mesh.vertices, part.transform)
        face_model = _create_face_model(model, Mesh(vertices=transformed, triangles=part.mesh.triangles))
        body = model.create_entity(
            "IfcShapeRepresentation",
            context,
            "Body",
            "SurfaceModel",
            [face_model],
        )
        shape = model.create_entity("IfcProductDefinitionShape", None, None, [body])
        placement = model.create_entity("IfcLocalPlacement", storey.ObjectPlacement, default_axis)
        product = model.create_entity(
            "IfcBuildingElementProxy",
            _guid(),
            owner_history,
            part.name or f"BambuPart_{idx}",
            None,
            None,
            placement,
            shape,
            None,
            "NOTDEFINED",
        )
        model.create_entity(
            "IfcRelContainedInSpatialStructure",
            _guid(),
            owner_history,
            None,
            None,
            [product],
            storey,
        )
        _create_pset(model, owner_history, product, compact_meta)

    if out.suffix.lower() == ".ifczip":
        uncompressed = out.with_suffix(".ifc")
        model.write(str(uncompressed))
        with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(uncompressed, arcname=uncompressed.name)
        uncompressed.unlink(missing_ok=True)
    else:
        model.write(str(out))
    return out
