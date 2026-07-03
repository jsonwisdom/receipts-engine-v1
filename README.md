# Jay Wisdom Receipts Machine — v1

[![Replay Status](https://jsonwisdom.github.io/receipts-engine-v1/signal-core/badge.svg)](https://jsonwisdom.github.io/receipts-engine-v1/signal-core/replay)

> **Status: Production Rail v0_1 sealed — Replay Badge v0.2 active**
>
> This repository is a public verifier interface for the receipts-machine ecosystem.
> The canonical Anchor 001 state is recorded in `jsonwisdom/Welcome-to-JSONWISDOM`.
> See `docs/ANCHOR_001_COMPATIBILITY.md` for the current GitHub + EAS verification model.
>
> The ENS-first Looking Glass flow remains useful for artifacts that intentionally use ENS text records, but Anchor 001 does not depend on ENS.

**A sovereign verification layer for auditability, control-plane truth, and forensic record-keeping.**

This system explores how documents and records can become cryptographically verifiable proofs anchored on Base. It combines deterministic hashing, Merkle membership, ENS + IPFS anchoring, and an append-only temporal ledger so artifacts can be independently checked without trusting an intermediary.

**ENS:** `jaywisdom.base.eth`

## What It Does

- Turns receipts, documents, and records into tamper-evident artifacts
- Supports public anchoring patterns using Base, ENS, and IPFS where appropriate
- Maintains compatibility with rolling-root and historical-ledger designs
- Provides replayable verification surfaces so truth can be mathematically checked
- Supports watchdog-style monitoring patterns to detect drift or tampering

No accounts. No centralized trust. Verification should be pure replay.

## Key Capabilities

- **Deterministic Proofs** — Canonical hashing and Merkle-tree-compatible designs
- **On-Chain Anchoring** — ENS/IPFS Looking Glass flow plus Base verification surfaces
- **Temporal Ledger** — Append-only history patterns with deterministic epochs
- **Rolling Master Root** — Cryptographic commitment pattern for full timelines
- **Replay Verification** — Independent checks of state and history
- **Watchdog** — Integrity monitoring pattern with optional alerting hooks
- **Public Dashboard** — Browser-based timeline and verification UI
- **Adversarial Testing** — Challenge and integrity validation patterns

## Anchor 001 Compatibility

Anchor 001 is not verified through the ENS-first Looking Glass model.

Canonical Anchor 001 uses:

```text
GitHub commit → JCS canonical bytes → SHA-256 → Keccak-256 → EAS attestation on Base
```

See `docs/ANCHOR_001_COMPATIBILITY.md` for exact values and verification steps.

## Live Verification

The Looking Glass verifier route can be deployed for ENS-based artifacts:

**https://your-verifier.vercel.app/?ens=jaywisdom.base.eth**

Replace the URL above with your deployed verifier once live.

## Tech Stack

- **Frontend**: Next.js 14 + React 18 + viem
- **Anchoring**: ENS + IPFS on Base for Looking Glass artifacts
- **Verification**: Deterministic replay patterns, Merkle-compatible checks, rolling-ledger concepts
- **Monitoring**: Watchdog pattern with optional webhook alerts

## Quick Start

```bash
git clone https://github.com/jsonwisdom/receipts-engine-v1.git
cd receipts-engine-v1
npm install
npm run dev
```

For backend verification tools and ledger operations, see the project structure and environment configuration.

## Philosophy

> If it cannot be deterministically rebuilt, it didn’t happen.

This is infrastructure for control-plane truth in adversarial environments where auditability and verifiability matter most.

## Discipline Rules

- Never rewrite historical ledger entries
- Never anchor unverified state
- Keep signing keys outside public verifier logic
- Maintain IPFS pinning for availability when using IPFS-based artifacts
- Treat mathematical replay as final authority
- Do not claim ENS anchoring unless text records are visible and independently verifiable

## Live System

- **ENS:** `jaywisdom.base.eth`
- **Chain:** Base
- **Version:** v1 (`0.1.0`)
- **Canonical Anchor 001 Source:** `jsonwisdom/Welcome-to-JSONWISDOM`

## Status

**Prototype verifier surface — see docs for canonical Anchor 001 state**
