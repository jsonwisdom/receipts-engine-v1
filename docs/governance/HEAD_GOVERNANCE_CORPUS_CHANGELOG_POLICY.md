# HEAD Governance Corpus Changelog Policy

**VERSIONED • DOCS-ONLY • NON-AUTHORITATIVE • AUTHORITY_FALSE**

## Purpose

This document defines how changes to the HEAD governance corpus are recorded across versions.

The changelog policy ensures corpus evolution remains readable, reviewable, and governance-safe.

This policy applies to documentation changes only.

It does not create execution evidence, replay outputs, HEAD entries, commits, tags, releases, seals, public anchors, hashes, or authority.

---

## 1. Core Changelog Rule

A changelog records documentation changes.

It does not prove execution.

```text
CHANGELOG_ENTRY != EXECUTION_EVIDENCE
VERSION_NOTE != HEAD_PROMOTION
DOC_CHANGE != REPLAY_PASS
TAG_NOTE != AUTHORITY
PUBLICATION_NOTE != ANCHOR_PROOF
```

---

## 2. Changelog Scope

The corpus changelog may record:

- added documents
- revised documents
- removed documents
- renamed documents
- clarified terminology
- safe-language corrections
- dependency graph updates
- template updates
- replay specification updates
- contributor workflow updates
- operator workflow updates
- release-plan updates

The changelog must not claim that any HEAD entry, replay digest, seal, release, or anchor was validated unless external operator-produced evidence exists and is explicitly referenced outside the changelog.

---

## 3. Required Changelog Fields

Each changelog entry should include:

```text
VERSION: corpus-vX.Y
DATE: YYYY-MM-DD
CHANGE_TYPE: added / changed / fixed / removed / deprecated
DOCUMENTS_AFFECTED: path list
SUMMARY: narrow description
BOUNDARY: documentation-only
AUTHORITY: false
NO_FAKE_GREEN: true
```

Optional fields:

```text
DEPENDENCIES_UPDATED: yes/no
GLOSSARY_UPDATED: yes/no
TEMPLATES_UPDATED: yes/no
SAFE_LANGUAGE_REVIEWED: yes/no
```

---

## 4. Change Types

### Added

Use when a new corpus document is introduced.

Safe language:

> Added a documentation guide describing corpus review procedures.

Unsafe language:

> Added a guide that finalizes corpus authority.

### Changed

Use when existing documentation is revised.

Safe language:

> Updated replay terminology to preserve deterministic meaning.

Unsafe language:

> Updated replay docs to prove the system is valid.

### Fixed

Use when correcting typos, broken links, unsafe language, or ambiguity.

Safe language:

> Fixed wording to preserve the safe claim boundary.

Unsafe language:

> Fixed the protocol so it is now authoritative.

### Removed

Use when removing outdated, unsafe, or redundant documentation.

Safe language:

> Removed duplicated language that could cause contributor confusion.

Unsafe language:

> Removed obsolete language after finalizing truth.

### Deprecated

Use when a document or pattern remains visible but should no longer be used.

Safe language:

> Deprecated an older template in favor of clearer placeholder handling.

Unsafe language:

> Deprecated old rules because the new rules are final authority.

---

## 5. Safe Changelog Language

Use narrow verbs:

- added
- changed
- clarified
- corrected
- documented
- updated
- deprecated
- removed
- referenced

Avoid authority verbs:

- proved
- finalized
- certified
- guaranteed
- authorized
- canonized by declaration
- validated truth

---

## 6. Versioning Rules

Corpus versions identify documentation state only.

Allowed examples:

```text
corpus-v0.1
corpus-v0.2
corpus-v1.0
```

Avoid:

```text
final
official
true
authoritative
```

A corpus version does not validate HEAD entries.

---

## 7. Dependency Notes

When a change affects dependencies, the changelog should identify related documents.

Examples:

- Replay spec changed → replay log schema and digest specs reviewed.
- Template changed → quickstart and implementation guide reviewed.
- Glossary changed → contributor-facing documents reviewed.
- Release guide changed → anchoring guide reviewed.

Dependency notes improve reviewability.

They do not prove correctness.

---

## 8. Changelog Entry Template

```text
## corpus-vX.Y - YYYY-MM-DD

CHANGE_TYPE: added / changed / fixed / removed / deprecated
DOCUMENTS_AFFECTED:
- docs/governance/EXAMPLE.md

SUMMARY:
- Describe the documentation change narrowly.

DEPENDENCIES_UPDATED: yes/no
GLOSSARY_UPDATED: yes/no
TEMPLATES_UPDATED: yes/no
SAFE_LANGUAGE_REVIEWED: yes/no

BOUNDARY: documentation-only
AUTHORITY: false
NO_FAKE_GREEN: true
```

---

## 9. Refusal Conditions

A changelog entry must be held or refused when it introduces:

```text
truth_claim = REFUSE
authority_claim = REFUSE
synthetic_execution_value = REFUSE
head_promotion_by_changelog = REFUSE
replay_success_without_output = REFUSE
seal_completion_by_language = REFUSE
anchor_publication_without_evidence = REFUSE
release_finality_claim = REFUSE
ambiguous_dependency_note = HOLD
unsafe_language = HOLD
```

---

## 10. Safe Claim Boundary

This changelog policy may claim:

> These rules define how documentation changes are recorded across corpus versions.

This changelog policy may not claim:

> Any HEAD entry, replay digest, release, seal, or anchor is true, authoritative, legal, owned, final, complete, released, or anchored.

---

## Summary

The HEAD Governance Corpus Changelog Policy defines:

```text
CHANGE TYPES
→ REQUIRED FIELDS
→ SAFE LANGUAGE
→ VERSIONING RULES
→ DEPENDENCY NOTES
→ REFUSAL CONDITIONS
```

The changelog records documentation evolution.

It does not fabricate evidence.

The corpus remains:

```text
WITNESS_ONLY
EVIDENCE_FIRST
AUTHORITY_FALSE
NO_FAKE_GREEN
```
