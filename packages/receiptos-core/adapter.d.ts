import type { GoblinCourtReceiptV0_1 } from "./types";

/**
 * Hex-encoded SHA-256 digest used by ReceiptOS receipt records.
 */
export type ReceiptHash = `0x${string}`;

/**
 * Stable local or remote asset reference.
 * Examples: file://video.mp4, ipfs://..., https://...
 */
export type ReceiptUri = string;

/**
 * Minimal asset descriptor consumed by adapter events.
 * Raw bytes are never trusted directly; every asset must carry a digest.
 */
export interface ReceiptAssetRef {
  asset_id: string;
  hash: ReceiptHash;
  media_type: string;
  uri?: ReceiptUri;
}

/**
 * Tool invocation descriptor.
 * Parameters are opaque to the core protocol and should be canonicalized
 * by the adapter before hashing an event payload.
 */
export interface ReceiptToolRef {
  tool_id: string;
  version: string;
  parameters?: Record<string, unknown>;
}

/**
 * Canonical stage payload submitted by adapters to ReceiptOS core.
 *
 * Boundary rule:
 * - Adapters emit stage events.
 * - Core computes prev_hash, event_hash, and receipt_id.
 * - One event becomes one hash.
 */
export interface MediaProvenanceStageEvent {
  stage_id: string;
  before: {
    assets: ReceiptAssetRef[];
    tool_chain: ReceiptToolRef[];
  };
  after: {
    assets: ReceiptAssetRef[];
  };
  metadata?: Record<string, unknown>;
}

/**
 * Receipt emitted after the core accepts and hashes a stage event.
 */
export type MediaProvenanceReceipt = GoblinCourtReceiptV0_1;

/**
 * Minimal adapter trait for media-producing systems.
 *
 * The adapter MAY hash assets and collect tool/provider context.
 * The adapter MUST NOT compute prev_hash or event_hash.
 * Hash-chain authority belongs to ReceiptOS core only.
 */
export interface MediaProvenanceAdapter {
  readonly adapter_id: string;
  readonly adapter_version: string;

  /**
   * Capture input assets and tool-chain context before a media stage runs.
   */
  beforeStage(stage_id: string, input: {
    assets: ReceiptAssetRef[];
    tool_chain: ReceiptToolRef[];
    metadata?: Record<string, unknown>;
  }): Promise<void> | void;

  /**
   * Capture output assets after a media stage completes.
   * Implementations should submit exactly one canonical stage event to core.
   */
  afterStage(stage_id: string, output: {
    assets: ReceiptAssetRef[];
    metadata?: Record<string, unknown>;
  }): Promise<MediaProvenanceStageEvent> | MediaProvenanceStageEvent;

  /**
   * Finalize the packet after all stages complete.
   * Core returns the schema-compliant receipt object.
   */
  finalize(): Promise<MediaProvenanceReceipt> | MediaProvenanceReceipt;
}
