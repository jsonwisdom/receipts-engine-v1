# Portfolio Classification Rules v0.1

## Classification Set

### `CANONICAL`

Use for the repository that holds the governing map or canonical public protocol surface for the portfolio.

Requirements:

- Explicitly named as canonical by policy.
- Maintained through reviewable pull requests.
- Does not gain truth or execution authority from the label.

### `ACTIVE_DEPENDENCY`

Use for a repository that currently supplies implementation, governance, data, replay, agent, or documentation capabilities to a canonical system.

Signals may include recent commits, open PRs, active workflows, or explicit dependency references. Activity alone is insufficient without a stated purpose.

### `EXPERIMENTAL`

Use for prototypes, research surfaces, unintegrated tools, or candidate components whose canonical role has not been decided.

Experimental repositories must not be represented as production dependencies without a separate observed promotion decision.

### `LEGACY`

Use for repositories that preserve earlier approaches, superseded versions, or historical material that may still have reference value.

Legacy status does not authorize deletion or archival.

### `ARCHIVE`

Use only after observable evidence shows the repository is intentionally retained as read-only historical material and a human has approved archival posture.

The registry may recommend `ARCHIVE`; it must not perform or falsely claim the GitHub archive action.

### `PRIVATE_REVIEW_REQUIRED`

Use when repository names, branches, files, visibility, or history indicate a possible privacy, credential, personal-data, or sensitive-content concern requiring non-destructive review.

This classification is a precaution. It is not proof that a secret, violation, or compromise exists.

## Deterministic Precedence

When multiple classifications appear applicable, use this precedence until human review resolves the conflict:

```text
PRIVATE_REVIEW_REQUIRED
CANONICAL
ACTIVE_DEPENDENCY
EXPERIMENTAL
LEGACY
ARCHIVE
```

`PRIVATE_REVIEW_REQUIRED` may also be recorded as a separate security-review state while preserving the repository's functional classification.

## Field Rules

- `open_pr_count`: Populate only from observed GitHub PR metadata.
- `last_observed_commit`: Record a full commit SHA and timestamp when inspected.
- `execution_status`: Use `UNOBSERVED` unless workflow or runtime evidence was inspected.
- `documentation_status`: Describe visible documentation posture; do not infer implementation quality.
- `security_review`: Record review posture, not a verdict.
- `active_dependencies`: Add only observable, directional dependencies.
- `canonical_parent`: Must identify the governing repository or remain `null`.
- `authority`: Must remain `false` for every entry.

## Prohibited Promotions

The following transitions require separate evidence and human review:

- `EXPERIMENTAL` to `ACTIVE_DEPENDENCY`
- `ACTIVE_DEPENDENCY` to `CANONICAL`
- any classification to `ARCHIVE`
- `PRIVATE_REVIEW_REQUIRED` to a cleared security state
- `UNOBSERVED` to any passing execution state

## No-Fake-Green Rule

Recent commits, merged PRs, generated files, badges, documentation claims, or repository activity must not be translated into successful execution without observed run status and supporting artifacts.