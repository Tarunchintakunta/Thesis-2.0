# Design checks (arithmetic predictions, not measurements)

Zipf s = 1.070916 over 1,000,000 orders: hottest 10% of keys get 90.0% of operations; the single hottest order gets 10.65%, the hottest customer 10.65%.

## Provisioned capacity plan (C2)

| key_design | read_need_rcu_s | write_need_wcu_s | read_min | read_max | write_min | write_max |
|---|---|---|---|---|---|---|
| K1 | 95 | 140 | 140 | 700 | 200 | 1000 |
| K2 | 95 | 140 | 140 | 700 | 200 | 1000 |
| K3 | 950 | 140 | 1360 | 6800 | 200 | 1000 |

## Hot partition-key load at the profile's peak rate

2 of 36 design x workload x item-size cases would pass the documented per-partition limit (3000 RCU/s, 1000 WCU/s):

| key_design | workload | item_kb | hot_key_rcu_s | hot_key_wcu_s |
|---|---|---|---|---|
| K1 | W4 | 32 | 212.996 | 1703.969 |
| K2 | W4 | 32 | 213.034 | 1704.27 |
