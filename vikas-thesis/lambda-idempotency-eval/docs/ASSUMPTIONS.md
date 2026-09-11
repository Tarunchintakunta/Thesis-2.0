# Assumptions and implementation decisions

Things the code relies on, and why. Each one is a possible threat to validity,
so the report's limitations section should be checked against this list.

| # | decision | why / consequence |
|---|---|---|
| A1 | **Injected timeout**: after the path's writes return, the handler logs its record and sleeps past the function timeout (2 s); Lambda ends it with "Task timed out". | The state change is committed but the caller sees a failure - the duplicate-generating case of the master prompt. Locally (`INJECT_MODE=raise`) it raises `InjectedTimeout` instead. Real failures can be partial; this study measures post-commit duplicates only. |
| A2 | **Synchronous invokes only** (`RequestResponse`), driver SDK retries off, event-invoke config `maximum_retry_attempts = 0`. | Lambda does not retry synchronous invokes, so every delivery in the data is a scheduled one and the retry ground truth is known. |
| A3 | **No SDK retries inside the function** (`total_max_attempts = 1`). | A throttled or failed write shows up as an error instead of a hidden extra attempt. |
| A4 | **Mutations are counted from DynamoDB Streams** (`NEW_AND_OLD_IMAGES`). | Independent of what the function reports. DynamoDB writes no stream record for a write that changes nothing, so every business write carries its own `exec_id` and delivery number - a repeated write always changes the item and is always visible. |
| A5 | **Capacity** from `ReturnConsumedCapacity=TOTAL` on every call. A `ConditionalCheckFailedException` response carries no consumed capacity, so the documented rule (write units by item size) is added in a separate column `wcu_ccf_rule`. If a live error does carry capacity, that value is used and no rule units are added. | Failed conditions are billed and must be reported (master prompt 2.7). `scripts/collect_cloudwatch.py` checks the rule against CloudWatch's `ConsumedWriteCapacityUnits`. |
| A6 | **Item size**: the synthetic payload is padded so the business item is just under 1 KB. | Every write is 1 write unit, so capacity differences come from the number of calls, not from item size. |
| A7 | **P3 follows the Powertools idempotency pattern**, written out by hand: claim `IDEMP#<request_id>` as IN_PROGRESS (expires with the invocation's remaining time), business write, mark COMPLETED with the stored result (key TTL 1 h). | Every call's capacity is visible. It is a pattern reference, not the Powertools library and not a custom runtime. A redelivery gets the stored result (REPLAYED), is refused while a live claim exists (REJECTED_IN_PROGRESS), or runs again once the claim expired. |
| A8 | **P2 uses `attribute_not_exists(pk)`** only. | Each request writes a new item, so a version check has nothing to compare against; version-based updates of existing items are future work. |
| A9 | **A timeout resets the execution environment.** | The next invocation in that environment runs INIT again, so redeliveries after an injected timeout are often cold starts. Recorded per delivery (`cold_start`) and reported, not removed. |
| A10 | **Latency** is the driver's round trip for the final delivery. | Includes invoke overhead and the network path from the driver, so the driver should run close to eu-west-1 (CloudShell or an EC2 instance there) and stay on the same machine for the whole campaign. Cells are interleaved, so drift is shared. |
| A11 | **Deliveries of one request are sequential**; requests run on `--workers` threads. | Two deliveries of the same request never overlap - concurrent duplicates are out of scope. |
| A12 | **Single-item writes only**, no `TransactWriteItems`. | Master prompt 6; multi-item transactions are future work. |
| A13 | **Local / moto runs** use a `LocalContext` with remaining time -1, so a P3 claim from a "timed-out" local delivery has already expired when the redelivery arrives - as on Lambda, where the redelivery only starts after the timeout. | Without it a local run would refuse the redelivery where Lambda would not. |
| A14 | **moto is only a functional check.** | moto reports 0.5 units for every UpdateItem and does not model latency, throttling or cold starts. Nothing from `results/moto` is a result. |
| A15 | **One region, one account, one table, one function, on-demand capacity.** | External validity is limited to that setting (master prompt 5, threats). |

Vikas Reddy Amanagantti
