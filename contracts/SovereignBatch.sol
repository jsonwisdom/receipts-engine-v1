pragma solidity ^0.8.20;
contract SovereignBatch {
    event BatchAnchored(bytes32 indexed batchId,bytes32 indexed merkleRoot,bytes32 indexed receiptHash,uint256 leafCount,string receiptCid);
    mapping(bytes32 => bool) public isAnchored;
    function anchorBatch(bytes32 _batchId,bytes32 _merkleRoot,bytes32 _receiptHash,uint256 _leafCount,string calldata _receiptCid) external {
        require(!isAnchored[_batchId]);
        isAnchored[_batchId]=true;
        emit BatchAnchored(_batchId,_merkleRoot,_receiptHash,_leafCount,_receiptCid);
    }
}
