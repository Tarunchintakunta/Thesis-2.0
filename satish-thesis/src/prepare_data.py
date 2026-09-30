"""Build the hourly Building 59 modelling table from the raw LBNL CSV files.

Output: data/processed/bldg59_hourly.csv, results/data_dictionary.csv, results/data_profile.json.
Every row is one hour h. Sensor columns are means over [h, h+1). The target of the
forecast made at the end of hour h is hvac_kwh at h+1 (see experiment.py).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "data" / "raw", ROOT / "data" / "processed"
START, END = "2018-06-01", "2020-12-31 23:00"
F_TO_C = lambda f: (f - 32.0) * 5.0 / 9.0


def hourly(name, cols=None):
    d = pd.read_csv(RAW / f"{name}.csv")
    d = d.loc[:, ~d.columns.str.startswith("Unnamed")]
    d.index = pd.to_datetime(d.pop("date"), format="mixed")
    d = d.apply(pd.to_numeric, errors="coerce")
    if cols:
        d = d[cols]
    return d.resample("1h").mean()


def build():
    ele = hourly("ele")
    wx = hourly("site_weather")
    tin = hourly("zone_temp_interior")
    sat = hourly("rtu_sa_t")
    rat = hourly("rtu_ra_t")
    fan = hourly("rtu_fan_spd").filter(like="_sf_")

    # Physically impossible supply-air readings (0 degF) are treated as missing.
    sat = sat.where(sat > 32)
    rat = rat.where(rat > 32)
    fan = fan.where((fan >= 0) & (fan <= 100))

    df = pd.DataFrame({
        "hvac_kwh": ele["hvac_N"] + ele["hvac_S"],          # kW averaged over 1 h == kWh
        "t_in": tin.median(axis=1),                          # 16 loggers, median is robust to one bad logger
        "t_out": wx["air_temp_set_1"],
        "rh_out": wx["relative_humidity_set_1"],
        "solar": wx["solar_radiation_set_1"],
        # Plug loads + lighting: electricity that ends up as internal heat gain. Used instead of the
        # Wi-Fi/camera occupancy counts, which are missing for most of 2018-2020 in the release.
        "q_int": ele["mels_N"] + ele["mels_S"] + ele["lig_S"],
        "t_sa": F_TO_C(sat.mean(axis=1)),
        "t_ra": F_TO_C(rat.mean(axis=1)),
        "fan": fan.mean(axis=1),
    }).loc[START:END]
    df = df.reindex(pd.date_range(START, END, freq="1h"))
    df.index.name = "time"  # raw timestamps are UTC (solar noon falls at 20:00)
    natural_gap = df.isna()
    # Short natural gaps (<= 3 h) are filled by time interpolation inside the curated table;
    # longer ones are left NaN and flagged so they are never used as a target.
    df = df.interpolate(method="time", limit=3, limit_area="inside")
    df["natural_gap"] = natural_gap.any(axis=1).astype(int)
    df["valid"] = df.notna().all(axis=1).astype(int)
    local = df.index.tz_localize("UTC").tz_convert("America/Los_Angeles")
    df["local_hour"], df["local_dow"], df["local_month"] = local.hour, local.dayofweek, local.month
    return df, natural_gap


DICTIONARY = [
    ("hvac_kwh", "kWh", "ele.csv hvac_N + hvac_S", "HVAC electricity in the hour (forecast target, also lagged input)"),
    ("t_in", "degC", "zone_temp_interior.csv", "Median of 16 indoor air-temperature loggers"),
    ("t_out", "degC", "site_weather.csv air_temp_set_1", "Outdoor air temperature, LBNL weather station"),
    ("rh_out", "%", "site_weather.csv relative_humidity_set_1", "Outdoor relative humidity"),
    ("solar", "W/m2", "site_weather.csv solar_radiation_set_1", "Global solar radiation"),
    ("q_int", "kW", "ele.csv mels_N + mels_S + lig_S", "Plug-load and lighting power, internal heat-gain proxy"),
    ("t_sa", "degC", "rtu_sa_t.csv mean of 4 RTUs", "Supply-air temperature"),
    ("t_ra", "degC", "rtu_ra_t.csv mean of 4 RTUs", "Return-air temperature"),
    ("fan", "%", "rtu_fan_spd.csv supply-fan VFD mean", "Supply-fan speed feedback"),
    ("natural_gap", "0/1", "derived", "1 if any column was missing in the raw data for this hour"),
    ("valid", "0/1", "derived", "1 if all columns are present after short-gap filling"),
    ("local_hour", "h", "derived", "Hour of day, America/Los_Angeles"),
    ("local_dow", "0-6", "derived", "Day of week (Monday = 0), local time"),
    ("local_month", "1-12", "derived", "Month, local time"),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (ROOT / "results").mkdir(exist_ok=True)
    df, gap = build()
    df.round(4).to_csv(OUT / "bldg59_hourly.csv")
    pd.DataFrame(DICTIONARY, columns=["column", "unit", "source", "description"]).to_csv(
        ROOT / "results" / "data_dictionary.csv", index=False)
    num = df.drop(columns=["natural_gap", "valid", "local_hour", "local_dow", "local_month"])
    profile = {
        "rows": len(df), "start": str(df.index[0]), "end": str(df.index[-1]),
        "raw_missing_pct": (gap.mean() * 100).round(3).to_dict(),
        "missing_after_fill_pct": (num.isna().mean() * 100).round(3).to_dict(),
        "valid_rows_pct": round(df["valid"].mean() * 100, 3),
        "summary": num.describe().round(3).to_dict(),
        "corr_with_hvac": num.corr()["hvac_kwh"].round(3).to_dict(),
    }
    (ROOT / "results" / "data_profile.json").write_text(json.dumps(profile, indent=2))
    print(json.dumps({k: profile[k] for k in ("rows", "start", "end", "raw_missing_pct", "valid_rows_pct", "corr_with_hvac")}, indent=1))


if __name__ == "__main__":
    main()
