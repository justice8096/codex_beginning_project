# CWE Mapping & Framework Crosswalk (Re-audit)
## Project: bambu2ifc

**Date**: 2026-03-31

## Mapped Findings

| Finding | CWE | Severity | Status |
|---|---|---|---|
| Archive/model resource consumption (bounded) | CWE-400 | Medium | Mitigated, residual |
| Output resource throttling | CWE-770 | Resolved | Closed via writer budgets |
| Unresolved component handling | CWE-754 | Resolved | Closed via strict default errors |
| Dependency policy drift | CWE-1104 | Medium | Open (supply-chain backlog) |

## Framework Mapping Matrix

| CWE | OWASP Top 10 2021 | OWASP LLM Top 10 2025 | NIST SP 800-53 | EU AI Act Art. 25 | ISO 27001 | SOC 2 | MITRE ATT&CK | MITRE ATLAS |
|---|---|---|---|---|---|---|---|---|
| CWE-400 | A04 / A06 | LLM04 | SC-5, SI-10 | Risk controls | A.8.16 | CC7.1 | T1499 | AML.TA0040 |
| CWE-1104 | A06 | LLM05 | SR-3, SA-12 | Lifecycle obligations | A.5.21 | CC6.6 | T1195 | AML.TA0001 |

## Before/After

| Metric | Before | After |
|---|---:|---:|
| High CWEs | 1 | 0 |
| Medium CWEs | 3 | 2 |

## Aggregate Status

- Total active mapped CWEs: **2**
- Critical CWEs: **0**
- High CWEs: **0**
- Medium CWEs: **2**

**Result**: **CONDITIONAL PASS (supply-chain + residual resource controls)**
