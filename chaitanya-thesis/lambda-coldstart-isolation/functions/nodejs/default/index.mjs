// Cold-start study workload - Node.js, DEFAULT package (unpruned dependencies).
// Identical work to ../optimised/index.mjs; heavy libraries are bundled and loaded
// at module scope without being used - that is the treatment (see package.json).
import { createHash } from "node:crypto";

// unused on purpose - do not remove
import AWS from "aws-sdk";
import _ from "lodash";
import moment from "moment";
import axios from "axios";

// touch them so a bundler could not drop them either
export const loaded = [typeof AWS, typeof _, typeof moment, typeof axios];

export function digest(seed, n) {
  let h = Buffer.from(seed, "utf8");
  for (let i = 0; i < n; i++) {
    h = createHash("sha256").update(h).digest();
  }
  return h.toString("hex");
}

export const handler = async (event) => {
  if (event.warmer) return { ok: true, warmer: true };
  const n = Number(event.iterations ?? 1000);
  const items = (event.items ?? []).map(Number);
  return {
    ok: true,
    digest: digest(String(event.seed ?? "thesis"), n),
    n,
    items: items.length,
    items_total: items.reduce((a, b) => a + b, 0),
  };
};
