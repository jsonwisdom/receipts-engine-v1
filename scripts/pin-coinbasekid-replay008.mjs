/**
 * Upload ONLY the static, public REPLAY 008 handoff manifest to Pinata.
 * Never reveal the JWT, publish private proofs, sign, or move funds.
 */
import { readFileSync, appendFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
const file='sealed/COINBASEKID_REPLAY008_SEALED_MANIFEST.json';
const raw=readFileSync(file);
if(raw.length>65536)throw Error('MANIFEST_TOO_LARGE');
const m=JSON.parse(raw.toString('utf8'));
if(m.schema!=='jsonwisdom.sealed_public_batch_handoff.v1'||
  m.artifact_id!=='COINBASEKID_REPLAY008_SEALED_PUBLIC_HANDOFF'||
  m.chain?.eip155_chain_id!==8453||
  m.scope?.private_proof_bundle_included!==false||
  m.scope?.raw_wallet_signatures_included!==false||
  m.scope?.actual_accepted_batch_merkle_root!==null||
  m.authorization?.funds_movement_authorized!==false||
  m.authorization?.x402_settlement_authorized!==false||
  m.authorization?.chain_attestation_status!=='NOT_PERFORMED')
  throw Error('SEAL_SCOPE_GATE_FAILED');
const sha256='0x'+createHash('sha256').update(raw).digest('hex');
const jwt=process.env.PINATA_JWT;
if(!jwt){console.error('PINATA_JWT_NOT_CONFIGURED: no upload attempted');process.exit(2);}
const form=new FormData();
form.append('file',new Blob([raw],{type:'application/json'}),'COINBASEKID_REPLAY008_SEALED_MANIFEST.json');
form.append('pinataMetadata',JSON.stringify({name:'COINBASEKID_REPLAY008_SEALED_MANIFEST',keyvalues:{
  artifact_id:m.artifact_id,chain_id:'8453',scope:'public_audit_handoff_not_private_proof'
}}));
form.append('pinataOptions',JSON.stringify({cidVersion:1}));
const response=await fetch('https://api.pinata.cloud/pinning/pinFileToIPFS',{
  method:'POST',headers:{Authorization:'Bearer '+jwt},body:form,
  signal:AbortSignal.timeout(60000)
});
if(!response.ok){
  console.error('PINATA_UPLOAD_FAILED_HTTP_'+response.status+'; no CID claimed');
  process.exit(1);
}
const out=await response.json();
const cid=out.IpfsHash;
if(typeof cid!=='string'||!(/^(bafy[a-z2-7]{30,}|Qm[1-9A-HJ-NP-Za-km-z]{44})$/).test(cid))
  throw Error('PINATA_RETURNED_NO_VALID_CID');
console.log('PINATA_CID='+cid);
console.log('SEALED_MANIFEST_SHA256='+sha256);
console.log('PINATA_UPLOAD_CONFIRMED=true');
let verified=false;
for(let attempt=0;attempt<4;attempt++){
  try{
    const gateway=await fetch('https://gateway.pinata.cloud/ipfs/'+cid,{
      headers:{'Accept':'application/json'},signal:AbortSignal.timeout(12000)
    });
    if(!gateway.ok)continue;
    const downloaded=Buffer.from(await gateway.arrayBuffer());
    const digest='0x'+createHash('sha256').update(downloaded).digest('hex');
    if(digest!==sha256)throw Error('PUBLIC_GATEWAY_BYTES_MISMATCH');
    verified=true;
    break;
  }catch(e){
    if(String(e?.message).includes('PUBLIC_GATEWAY_BYTES_MISMATCH'))throw e;
  }
}
console.log('PINATA_GATEWAY_SHA256_MATCH='+String(verified));
console.log('ATTESTATION=NOT_PERFORMED');
console.log('ONCHAIN_TX=NONE');
if(process.env.GITHUB_STEP_SUMMARY){
  appendFileSync(process.env.GITHUB_STEP_SUMMARY,[
    '# CoinBaseKid REPLAY 008 — Public Pinata upload',
    '',
    '| Field | Value |',
    '|---|---|',
    '| Content ID | '+cid+' |',
    '| File SHA-256 | '+sha256+' |',
    '| Public gateway | https://gateway.pinata.cloud/ipfs/'+cid+' |',
    '| Gateway byte-match | '+(verified?'CONFIRMED':'NOT_YET_CONFIRMED')+' |',
    '| Evidence type | Public engineering handoff manifest; NOT a signed batch proof |',
    '| Onchain / settlement | NONE / HOLD |',
    ''
  ].join('\n'));
}
