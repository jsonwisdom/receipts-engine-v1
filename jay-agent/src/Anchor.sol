// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MediaAnchor {
    event Anchored(
        bytes32 indexed contentHash,
        string contentCid,
        string receiptCid,
        string sourceUrl,
        string observedAt,
        address indexed observer
    );
    
    function anchor(
        bytes32 contentHash,
        string calldata contentCid,
        string calldata receiptCid,
        string calldata sourceUrl,
        string calldata observedAt
    ) external {
        emit Anchored(contentHash, contentCid, receiptCid, sourceUrl, observedAt, msg.sender);
    }
}
