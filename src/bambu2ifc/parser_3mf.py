from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

from .errors import InputFormatError, ParseError
from .models import (
    BuildMetadata,
    IDENTITY_3X4,
    Matrix3x4,
    Mesh,
    NormalizedBuild,
    Part,
)


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _first_child(parent: ET.Element, name: str) -> ET.Element | None:
    for child in parent:
        if _local_name(child.tag) == name:
            return child
    return None


def _attr_local(attrib: dict[str, str], name: str) -> str | None:
    for key, value in attrib.items():
        if _local_name(key) == name:
            return value
    return None


def _parse_transform(raw: str | None) -> Matrix3x4:
    if not raw:
        return IDENTITY_3X4
    values = [float(v) for v in raw.split()]
    if len(values) != 12:
        raise ParseError(f"Invalid 3MF transform: expected 12 values, got {len(values)}")
    return tuple(values)  # type: ignore[return-value]


def _compose_transforms(a: Matrix3x4, b: Matrix3x4) -> Matrix3x4:
    """Return composed transform A(B(v)) for 3x4 affine matrices."""
    a11, a12, a13, a14, a21, a22, a23, a24, a31, a32, a33, a34 = a
    b11, b12, b13, b14, b21, b22, b23, b24, b31, b32, b33, b34 = b
    return (
        a11 * b11 + a12 * b21 + a13 * b31,
        a11 * b12 + a12 * b22 + a13 * b32,
        a11 * b13 + a12 * b23 + a13 * b33,
        a11 * b14 + a12 * b24 + a13 * b34 + a14,
        a21 * b11 + a22 * b21 + a23 * b31,
        a21 * b12 + a22 * b22 + a23 * b32,
        a21 * b13 + a22 * b23 + a23 * b33,
        a21 * b14 + a22 * b24 + a23 * b34 + a24,
        a31 * b11 + a32 * b21 + a33 * b31,
        a31 * b12 + a32 * b22 + a33 * b32,
        a31 * b13 + a32 * b23 + a33 * b33,
        a31 * b14 + a32 * b24 + a33 * b34 + a34,
    )


def _parse_mesh(mesh_el: ET.Element) -> Mesh:
    vertices_el = _first_child(mesh_el, "vertices")
    triangles_el = _first_child(mesh_el, "triangles")
    if vertices_el is None or triangles_el is None:
        raise ParseError("Mesh is missing vertices or triangles")

    vertices = []
    for vertex in vertices_el:
        if _local_name(vertex.tag) != "vertex":
            continue
        vertices.append(
            (
                float(vertex.attrib["x"]),
                float(vertex.attrib["y"]),
                float(vertex.attrib["z"]),
            )
        )

    triangles = []
    for triangle in triangles_el:
        if _local_name(triangle.tag) != "triangle":
            continue
        triangles.append(
            (
                int(triangle.attrib["v1"]),
                int(triangle.attrib["v2"]),
                int(triangle.attrib["v3"]),
            )
        )

    if not vertices or not triangles:
        raise ParseError("Mesh has no geometry")
    return Mesh(vertices=vertices, triangles=triangles)


@dataclass(slots=True)
class ComponentRef:
    path: str | None
    object_id: str
    transform: Matrix3x4


@dataclass(slots=True)
class ObjectDef:
    object_id: str
    name: str | None
    mesh: Mesh | None
    components: list[ComponentRef]


def _normalize_model_path(path: str) -> str:
    return path.lstrip("/")


def _parse_model_file(model_xml: bytes) -> tuple[dict[str, ObjectDef], str]:
    root = ET.fromstring(model_xml)
    unit = root.attrib.get("unit", "millimeter")
    resources = _first_child(root, "resources")
    if resources is None:
        return {}, unit

    objects: dict[str, ObjectDef] = {}
    for obj in resources:
        if _local_name(obj.tag) != "object":
            continue
        object_id = _attr_local(obj.attrib, "id")
        if not object_id:
            continue
        name = _attr_local(obj.attrib, "name")
        mesh_el = _first_child(obj, "mesh")
        if mesh_el is not None:
            objects[object_id] = ObjectDef(
                object_id=object_id,
                name=name,
                mesh=_parse_mesh(mesh_el),
                components=[],
            )
            continue

        components_el = _first_child(obj, "components")
        components: list[ComponentRef] = []
        if components_el is not None:
            for comp in components_el:
                if _local_name(comp.tag) != "component":
                    continue
                child_object_id = _attr_local(comp.attrib, "objectid")
                if not child_object_id:
                    continue
                path = _attr_local(comp.attrib, "path")
                transform = _parse_transform(_attr_local(comp.attrib, "transform"))
                components.append(
                    ComponentRef(path=_normalize_model_path(path) if path else None, object_id=child_object_id, transform=transform)
                )
        objects[object_id] = ObjectDef(
            object_id=object_id,
            name=name,
            mesh=None,
            components=components,
        )
    return objects, unit


def parse_bambu_3mf(input_path: str | Path) -> NormalizedBuild:
    path = Path(input_path)
    if not path.name.lower().endswith(".3mf"):
        raise InputFormatError(f"Unsupported input extension for {path.name}. Expected .3mf")

    try:
        with zipfile.ZipFile(path, mode="r") as zf:
            all_models = [name for name in zf.namelist() if name.lower().endswith(".model")]
            root_model_path = "3D/3dmodel.model" if "3D/3dmodel.model" in all_models else next(iter(all_models), None)
            if root_model_path is None:
                raise ParseError("No .model XML found inside .3mf package")

            model_registry: dict[str, dict[str, ObjectDef]] = {}
            root_xml = zf.read(root_model_path)
            root = ET.fromstring(root_xml)
            metadata_raw: dict[str, str] = {}
            for child in root:
                if _local_name(child.tag) == "metadata":
                    key = _attr_local(child.attrib, "name") or "metadata"
                    metadata_raw[key] = (child.text or "").strip()

            root_objects, unit = _parse_model_file(root_xml)
            model_registry[root_model_path] = root_objects

            for model_path in all_models:
                if model_path == root_model_path:
                    continue
                try:
                    objects, _ = _parse_model_file(zf.read(model_path))
                    model_registry[model_path] = objects
                except ET.ParseError as exc:
                    raise ParseError(f"Unable to parse model file {model_path}: {exc}") from exc
    except zipfile.BadZipFile as exc:
        raise InputFormatError(f"Input is not a valid 3MF archive: {path}") from exc
    except ET.ParseError as exc:
        raise ParseError(f"Unable to parse 3MF model XML: {exc}") from exc

    def resolve_object(
        model_path: str,
        object_id: str,
        transform: Matrix3x4,
        seen: set[tuple[str, str]],
    ) -> list[Part]:
        key = (model_path, object_id)
        if key in seen:
            return []
        seen = set(seen)
        seen.add(key)

        model_objects = model_registry.get(model_path)
        if not model_objects:
            return []
        obj = model_objects.get(object_id)
        if obj is None:
            return []

        if obj.mesh is not None:
            return [
                Part(
                    object_id=f"{model_path}:{object_id}",
                    name=obj.name,
                    mesh=obj.mesh,
                    transform=transform,
                )
            ]

        resolved: list[Part] = []
        for comp in obj.components:
            child_model = comp.path or model_path
            child_transform = _compose_transforms(transform, comp.transform)
            resolved.extend(resolve_object(child_model, comp.object_id, child_transform, seen))
        return resolved

    parts: list[Part] = []
    build_el = _first_child(root, "build")
    if build_el is not None:
        for idx, item in enumerate(build_el):
            if _local_name(item.tag) != "item":
                continue
            object_id = _attr_local(item.attrib, "objectid")
            if not object_id:
                continue
            item_transform = _parse_transform(_attr_local(item.attrib, "transform"))
            resolved = resolve_object(root_model_path, object_id, item_transform, set())
            for part in resolved:
                part.object_id = f"{part.object_id}:{idx}"
                parts.append(part)

    if not parts:
        root_objects = model_registry.get(root_model_path, {})
        for object_id in root_objects:
            parts.extend(resolve_object(root_model_path, object_id, IDENTITY_3X4, set()))

    if not parts:
        raise ParseError("No mesh objects found in 3MF resources")

    return NormalizedBuild(parts=parts, metadata=BuildMetadata(source_file=str(path), unit=unit, extras=metadata_raw))
