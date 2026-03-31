# Supply Chain Security Audit (Re-audit)
## Project: bambu2ifc

**Date**: 2026-03-31  
**Branch**: `master`

## Findings

1. **No lockfile or reproducible environment manifest committed**
- **Risk**: Medium
- **Status**: Open

2. **Generated artifacts remain tracked in repository history**
- **Risk**: Medium
- **Status**: Open

3. **Large binary sample IFC tracked in repo**
- **Risk**: Low
- **Status**: Open

## Improvements Since Initial Audit

- Parser and writer resource controls are now implemented (reducing operational supply-chain risk from malformed inputs).
- Test execution is now stable without temp-path permission dependency.

## SLSA / SBOM Posture

- **SLSA Level (estimated)**: **L1**
- **SBOM**: Not present
- **CI provenance attestation**: Not present

## Overall

**Result**: **CONDITIONAL PASS**  
Remaining work: lockfile/SBOM + repository artifact hygiene.
