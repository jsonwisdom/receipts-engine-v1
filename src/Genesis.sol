// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Genesis {
    event ProofEmitted(
        string agentId,
        string tradeId,
        bytes32 commitmentHash,
        string uri
    );

    function emitProof(
        string calldata agentId,
        string calldata tradeId,
        bytes32 commitmentHash,
        string calldata uri
    ) external {
        emit ProofEmitted(agentId, tradeId, commitmentHash, uri);
    }
}
