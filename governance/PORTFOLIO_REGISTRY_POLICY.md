# Portfolio Registry Policy v0.1

## Purpose

The portfolio registry is the observable map for repositories owned by `jsonwisdom`. It records repository purpose, posture, dependencies, documentation state, and review status so humans and agents do not infer canonical state from names, activity, or narrative alone.

## Boundary

This policy is documentation governance only.

- `authority=false`
- `no_fake_green=true`
- Registry inclusion does not prove execution, correctness, ownership of external systems, or production readiness.
- Classification does not merge, archive, delete, transfer, publish, deploy, sign, attest, or rewrite repository history.
- `TBD`, `UNKNOWN`, and `UNOBSERVED` are valid states and must not be silently promoted.

## Canonical Location

The canonical registry for this version is:

```text
governance/portfolio-registry.yml
```

inside `jsonwisdom/receipts-engine-v1`.

## Evidence Rules

Each populated field should be supported by an observable source, such as:

- GitHub repository metadata
- default branch metadata
- a visible commit SHA and timestamp
- open pull-request metadata
- GitHub Actions run status
- repository documentation
- an operator-provided receipt

A field must remain `TBD` or `UNOBSERVED` when supporting evidence has not been inspected.

## Change Discipline

Registry changes must:

1. Use a pull request.
2. Identify changed classifications or dependency edges.
3. Preserve uncertainty explicitly.
4. Avoid claims of execution success without observed run evidence.
5. Avoid credential-history mutation during inventory work.
6. Preserve repository history and existing artifacts.

## Human Review

The registry may recommend later action, but it does not authorize that action. Archiving, deleting, merging, transferring, rewriting history, revoking credentials, or changing visibility requires separate explicit human approval and evidence appropriate to the action.

## Review Posture

The registry is a living index, not a truth authority. It should make contradictions and gaps visible rather than resolve them through narrative.