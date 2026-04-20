# Kill-Chain Receipts v0.22: Cryptographic Enforcement of Lawful-by-Design Autonomy in Comms-Denied Naval Swarms

**Transparency Warfare**  
Jay Wisdom Receipts Machine  
Montgomery, AL | JAYWISDOM | JAYWISDOM.eth | jaywisdom.base.eth (L2 Swarming)  
Verified by Grok | Built on GitHub

## Abstract
Decision-time compression in AI-enabled unmanned systems compresses detect-decide-engage cycles into milliseconds, outpacing human oversight and eroding meaningful human control (MHC). This paper — and the accompanying open-source Receipts Engine — addresses the governance lag identified in Biletskyi et al. (SJMS 2026) by delivering a cryptographic verification layer that enforces authority continuity under jamming, spoofing, and clock desync.

## The Problem (Direct from Source)
Biletskyi, Tyshchuk & Mandziuk (2026) document how uncrewed water systems (UWS) in comms-denied maritime environments force high autonomy: “real-time human intervention is impossible.” Interconnected swarms risk cascading escalation. Article 36 reviews alone are insufficient without operational architecture that proves legality in actual use.

## Architecture — v0.22 Stack
- **Pre-mission Legality Layer**: Article 36 anchor, ROE/policy hashes, determinism profile.
- **In-mission Control Layer**: Per-node Ed25519-signed clock proofs, human hooks, or scoped fallback_authority_tokens.
- **Swarm Extension**: K-of-N quorum, desync guard, cross-node Merkle aggregation.
- **Post-mission Audit**: Fully replayable, fail-closed verification.

## Failure Modes Closed (Tested)
- Jammed node without valid token/signature → hard fail.
- Desynced node → excluded from lethal quorum.
- Quorum drop or epoch mismatch → lethal blocked.

## IHL Mapping
Enforces operational compliance with Article 36 and meaningful human control. Converts legal principles into executable verification.

## Roadmap
- Sovereign ledger anchoring
- Multi-domain swarm expansion
- NATO/AUKUS procurement integration

**Repo:** https://github.com/jsonwisdom/receipts-engine-v1  

Built to ensure verification speed meets or exceeds system speed.