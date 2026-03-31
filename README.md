# bambu2ifc

Python component and CLI to convert Bambu build files (`.3mf`) into BIM IFC files (`.ifc` / `.ifcZIP`) using IfcOpenShell.

## Usage

```bash
bambu2ifc input.3mf -o output.ifc
bambu2ifc input.3mf -o output.ifczip --schema IFC2X3
```

## Notes

- Default output schema is `IFC4`.
- v0.1 targets mesh-based geometry with metadata preservation.
