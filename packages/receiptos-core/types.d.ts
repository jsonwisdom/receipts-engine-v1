/*
 * Generated from receipt-schema/v0.1/schema.json.
 * Regenerate with: npm run schema:types
 */

export interface GoblinCourtReceiptV0_1 {
  schema: "GoblinCourtReceiptV0_1";
  version: "0.1";
  /** Stable identifier for this receipt instance. */
  receipt_id: string;
  /** Hash of the previous receipt in the chain (or 0x00..00 for genesis). */
  prev_hash: string;
  /** Hash of the canonical event payload for this receipt. */
  event_hash: string;
  /** Hashing algorithm used for all digest fields. */
  algorithm: "sha256";
  /** Receipts are non-authoritative by design; authority=false is explicit. */
  authority: false;
  stages: Array<{
    /** Logical stage name (e.g., ingest, edit, render). */
    stage_id: string;
    before: {
      assets: Array<{
        asset_id: string;
        /** SHA-256 digest of the asset bytes. */
        hash: string;
        /** MIME-like descriptor (e.g., image/png, video/mp4). */
        media_type: string;
        /** Optional local or remote reference (file path, IPFS, etc.). */
        uri?: string;
      }>;
      tool_chain: Array<{
        /** Logical tool name (e.g., OpenMontage, Veo). */
        tool_id: string;
        /** Semantic or commit-based version identifier. */
        version: string;
        /** Opaque parameter bag; not interpreted by the schema. */
        parameters?: Record<string, unknown>;
      }>;
    };
    after: {
      assets: Array<{
        asset_id: string;
        hash: string;
        media_type: string;
        uri?: string;
      }>;
    };
  }>;
  /** Optional external anchors; not required for local replay. */
  anchors?: {
    ipfs_cid?: string;
    eas_uid?: string;
  };
  /** Non-hashed, non-authoritative metadata; excluded from event_hash. */
  metadata?: Record<string, unknown>;
}
