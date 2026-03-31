# SAST/DAST Scan Report (Re-audit)
## Project: bambu2ifc

**Date**: 2026-03-31  
**Branch**: `master`

## Remediation Verification

- Added archive/model size limits and model-file count limits in parser.
- Added strict unresolved-reference failures by default, plus explicit `--lenient` opt-in.
- Added geometry and output-size budgets in IFC writer.
- Re-ran tests: `5 passed`.

## Findings By Severity

### MEDIUM

1. **Archive parsing still uses whole-file reads within configured limits (CWE-400)**
- **Location**: `src/bambu2ifc/parser_3mf.py`
- **Status**: Mitigated (was HIGH, now MEDIUM residual)
- **Details**: Resource exhaustion risk is reduced via hard limits, but streaming XML parse is not yet implemented.

### LOW

1. **No formal DAST surface in current package**
- **Details**: CLI-only project; no HTTP endpoints to probe.
- **Action**: Re-run DAST if a service/API wrapper is added.

## Before/After

| Metric | Before | After |
|---|---:|---:|
| Critical | 0 | 0 |
| High | 1 | 0 |
| Medium | 2 | 1 |

## Summary

- **Critical**: 0  
- **High**: 0  
- **Medium**: 1  
- **Low/Info**: 1  
- **Overall**: **PASS with low residual risk**
