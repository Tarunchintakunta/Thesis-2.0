# Pooja Cost Explorer / LIST_PRICE remediable audit (scripted)

Generated: `2026-09-23T07:57:50.030986+00:00`
Live root: `/Users/valletivarish/Documents/Thesis-2.0/pooja-thesis/paks-framework/results/live`

## Move gate

- **remediable_total:** 0
- **move_blocker:** False
- **disposition:** `DATED_WONTFIX_COST_EXPLORER`

## Same-metrics snapshot

- live finals: 3/3
- latency rows: 3/3
- prediction rows (LSTM>persistence): 2
- cost: LIST_PRICE / SIMULATED ($0.04/pod-hour)
- baseline contrast: Binding baseline = Kubernetes HPA (reactive); ours add predictive PAKS Scale + TRACE MAE/RMSE + LIST_PRICE $/pod-hour (Cost Explorer bill validation dated WONTFIX)

## Remediable counts

- (none)

## Findings

- [ok] `live_final_ok`
- [ok] `live_cost_list_price_simulated_ok`
- [ok] `destroy_ok`
- [ok] `live_final_ok`
- [ok] `live_cost_list_price_simulated_ok`
- [ok] `destroy_ok`
- [ok] `live_final_ok`
- [ok] `live_cost_list_price_simulated_ok`
- [ok] `destroy_ok`
- [ok] `final3_latency_summary_ok`
- [ok] `final3_baseline_hpa_present`
- [ok] `lstm_worse_than_persistence_ok`
- [ok] `lstm_worse_than_persistence_ok`
- [ok] `list_price_constant_present`
- [ok] `no_cost_explorer_success_pack`
- [ok] `cost_explorer_amendment_present`
- [ok] `hpa_baseline_present`
- [ok] `sot_same_metrics_present`
- [ok] `config_cost_disclosure_ok`
- [ok] `status_cost_honesty_ok`
- [ok] `status_lstm_persistence_negative_ok`
