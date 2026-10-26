"""cprics/cyc.py — read the CYC exceedance reports into one tidy table.
These are the incumbent's official output: our baseline and our labels.
"""
import re
from pathlib import Path
import pandas as pd

MILEAGE_RE = re.compile(r"(\d+)m(\d+)y")
DATE_RE    = re.compile(r"Date:\s*(\d{2}/\d{2}/\d{4})")


def mileage_to_yards(text):
    """'164m0854y' -> 164*1760 + 854 (one number of yards)."""
    m = MILEAGE_RE.search(str(text))
    return int(m.group(1)) * 1760 + int(m.group(2)) if m else None


def parse_cyc_file(path):
    """Parse one .cyc report into a list of row dicts."""
    lines = Path(path).read_text(errors="replace").splitlines()
    file_date = next((DATE_RE.search(ln).group(1)
                      for ln in lines[:5] if DATE_RE.search(ln)), None)
    rows = []
    for ln in lines:
        parts = ln.split("\t")
        if len(parts) < 14 or not parts[1].strip().isdigit():
            continue
        try:
            cat_action = parts[10].strip()
            rows.append({
                "ELR": parts[0].strip(),
                "TrackID": int(parts[1]),
                "start_mileage": parts[2].strip(),
                "amplitude": float(parts[7]),
                "rail": parts[8].strip(),
                "wavelength": parts[9].strip(),
                "category": cat_action.split()[0] if cat_action else None,
                "action": cat_action,
                "threshold": float(parts[11]),
                "file_date": file_date,
                "source_file": Path(path).name,
            })
        except (ValueError, IndexError):
            continue
    return rows


def load_all_cyc(cyc_dir):
    """Read every report in a folder into one tidy, sorted DataFrame."""
    rows = []
    for p in sorted(Path(cyc_dir).iterdir()):
        if p.is_file():
            rows.extend(parse_cyc_file(p))
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["file_date"], format="%d/%m/%Y", errors="coerce")
    df["start_yards"] = df["start_mileage"].map(mileage_to_yards)
    df = df.dropna(subset=["start_yards"]).copy()
    df["pos_bucket"] = (df["start_yards"] // 20 * 20).astype(int)
    df["site_id"] = (df["ELR"] + "_" + df["TrackID"].astype(str) + "_"
                     + df["rail"] + "_" + df["wavelength"] + "_"
                     + df["pos_bucket"].astype(str))
    return df.sort_values(["site_id", "date"]).reset_index(drop=True)
