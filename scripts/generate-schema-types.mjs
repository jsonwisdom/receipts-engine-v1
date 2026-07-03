#!/usr/bin/env node

import { compileFromFile } from "json-schema-to-typescript";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

const schemaPath = path.resolve("receipt-schema/v0.1/schema.json");
const outputPath = path.resolve("packages/receiptos-core/types.d.ts");

const bannerComment = `/*\n * Generated from receipt-schema/v0.1/schema.json.\n * Regenerate with: npm run schema:types\n */\n\n`;

const generated = await compileFromFile(schemaPath, {
  bannerComment,
  style: {
    semi: true,
    singleQuote: false
  }
});

await mkdir(path.dirname(outputPath), { recursive: true });
await writeFile(outputPath, generated);

console.log(`Wrote ${path.relative(process.cwd(), outputPath)}`);
