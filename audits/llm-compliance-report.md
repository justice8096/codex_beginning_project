# LLM Compliance & Transparency Report
## bambu2ifc

**Report Date**: 2026-03-31  
**Auditor**: LLM Governance & Compliance Team  
**Project**: bambu2ifc (Claude-assisted development)  
**Framework**: EU AI Act Art. 25, OWASP LLM Top 10 2025, NIST SP 800-218A  
**Audit Type**: POST-FIX Re-audit

## Executive Summary

- **Overall LLM Compliance Score**: **82/100**
- **Status**: **GOOD**
- High-severity security findings are closed.
- Remaining gaps are supply-chain governance and reproducibility controls.

| Dimension | Before | After | Delta | Status |
|---|---:|---:|---:|---|
| System Transparency | 70 | 72 | +2 | Improved |
| Training Data Disclosure | 62 | 64 | +2 | Improved |
| Risk Classification | 82 | 88 | +6 | Improved |
| Supply Chain Security | 55 | 58 | +3 | Partial |
| Consent & Authorization | 92 | 92 | 0 | Stable |
| Sensitive Data Handling | 80 | 84 | +4 | Improved |
| Incident Response | 76 | 88 | +12 | Improved |
| Bias Assessment | 67 | 70 | +3 | Improved |

## Recommendations

1. Add lockfile/SBOM generation and CI dependency governance checks.
2. Add streaming XML parsing to further reduce residual CWE-400 risk.
3. Add explicit AI transparency notes to project docs.
4. Add repo hygiene cleanup (`__pycache__`, temporary artifacts) and `.gitignore` policy.

## Regulatory Roadmap

- **EU AI Act Art. 25**: Continue lifecycle hardening with enforceable build controls.
- **NIST SP 800-218A**: Add provenance, SBOM, and continuous security gates.
- **ISO 27001/SOC 2**: Improve supplier/dependency governance evidence.
