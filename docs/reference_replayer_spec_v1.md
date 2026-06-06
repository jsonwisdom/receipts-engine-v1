# Reference Replayer Specification V1 — FINAL

**Status:** LOCKED  
**Authority:** false

## Dependencies (Immutable Hashes)

- Constitution: `CONST_HASH`
- Equivalence Contract: `EQUIV_HASH`
- Semantic Contract V1: `SEMANTIC_HASH`
- Witness Certificate V1 schema
- Divergence Proof V1 schema
- Conformance Suite V1

---

## 1. Canonical Serialization (Mandatory)

All hashes MUST be computed over canonical UTF-8 JSON conforming to the following rules. Any deviation is a serialization error, not a constitutional divergence.