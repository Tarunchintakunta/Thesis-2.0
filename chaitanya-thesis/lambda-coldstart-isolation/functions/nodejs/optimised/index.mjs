// Cold-start study workload - Node.js, OPTIMISED package (no dependencies).
// Same work as the Python and Java versions: iterated SHA-256 + count/sum of items.
import { createHash } from "node:crypto";

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
