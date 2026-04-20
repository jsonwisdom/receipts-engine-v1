# Jay Wisdom Receipts Machine — v1

**A sovereign verification layer for auditability, control-plane truth, and forensic record-keeping.**

This system transforms documents and records into cryptographically verifiable proofs anchored on Base. It combines deterministic hashing, Merkle membership, ENS + IPFS anchoring, and an append-only temporal ledger so anyone can independently verify both current state and historical integrity without trusting any intermediary.

**ENS:** `jaywisdom.base.eth`

## What It Does

- Turns receipts, documents, and records into tamper-evident artifacts
- Anchors them publicly on Base via ENS and IPFS
- Maintains a rolling master root that commits the full history
- Provides replayable verification so truth can be mathematically confirmed
- Supports continuous watchdog monitoring to detect drift or tampering

No accounts. No centralized trust. Verification is pure replay.

## Key Capabilities

- **Deterministic Proofs** — Canonical hashing and Merkle trees
- **On-Chain Anchoring** — ENS text records and IPFS on Base
- **Temporal Ledger** — Append-only history with deterministic epochs
- **Rolling Master Root** — One cryptographic commitment for the full timeline
- **Replay Verification** — Independent trustless checks of state and history
- **Watchdog** — Continuous integrity monitoring with alerting hooks
- **Public Dashboard** — Browser-based timeline and verification UI
- **Adversarial Testing** — Built-in challenge and integrity validation

## Live Verification

Check the current state and full history here:

**https://your-verifier.vercel.app/?ens=jaywisdom.base.eth**

Replace the URL above with your deployed verifier once live.

## Tech Stack

- **Frontend**: Next.js 14 + React 18 + viem
- **Anchoring**: ENS + IPFS on Base
- **Verification**: Deterministic replay, Merkle membership, rolling ledger root
- **Monitoring**: Watchdog with optional webhook alerts

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
- Keep ENS signing keys secure
- Maintain IPFS pinning for availability
- Keep the watchdog running for continuous protection
- Treat mathematical replay as final authority

## Live System

- **ENS:** `jaywisdom.base.eth`
- **Chain:** Base
- **Version:** v1 (`0.1.0`)

## Status

**Production-ready · Self-verifying · Publicly auditable**
