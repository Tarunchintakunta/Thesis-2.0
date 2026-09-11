// One-shot init benchmark for a built Node.js package.
//   node scripts/bench/node_bench.mjs build/nodejs-default payloads/fixed_payload.json
// Prints one JSON line with epoch-microsecond timestamps (same format as python_bench.py).
import { readFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const nowUs = () => Math.round((performance.timeOrigin + performance.now()) * 1000);
const [pkg, payloadPath] = process.argv.slice(2);

const mod = await import(pathToFileURL(resolve(join(pkg, "index.mjs"))).href); // the "init phase"
const tInit = nowUs();
const event = JSON.parse(readFileSync(payloadPath, "utf8"));
const out = await mod.handler(event);
const tDone = nowUs();
console.log(JSON.stringify({ t_init_us: tInit, t_done_us: tDone, digest: out.digest, items_total: out.items_total }));
