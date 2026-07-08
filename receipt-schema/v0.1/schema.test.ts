import Ajv2020 from "ajv/dist/2020";
import schema from "./schema.json";

const ajv = new Ajv2020({ allErrors: true });
const validate = ajv.compile(schema);

test("valid minimal receipt passes schema", () => {
  const receipt = {
    schema: "GoblinCourtReceiptV0_1",
    version: "0.1",
    receipt_id: "REC-0001",
    prev_hash: "0x" + "0".repeat(64),
    event_hash: "0x" + "1".repeat(64),
    algorithm: "sha256",
    authority: false,
    stages: [
      {
        stage_id: "ingest",
        before: {
          assets: [
            {
              asset_id: "RAW-001",
              hash: "0x" + "2".repeat(64),
              media_type: "video/mp4",
              uri: "file://raw.mp4"
            }
          ],
          tool_chain: [
            {
              tool_id: "OpenMontage",
              version: "1.0.0",
              parameters: {}
            }
          ]
        },
        after: {
          assets: [
            {
              asset_id: "EDIT-001",
              hash: "0x" + "3".repeat(64),
              media_type: "video/mp4",
              uri: "file://edit.mp4"
            }
          ]
        }
      }
    ]
  };

  const valid = validate(receipt);
  if (!valid) {
    console.error(validate.errors);
  }

  expect(valid).toBe(true);
});
