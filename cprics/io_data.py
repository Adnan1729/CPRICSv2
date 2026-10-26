"""cprics/io_data.py — read Andy's peak-amplitude output over all dates.

Robust reader (pyarrow dataset, not pd.read_parquet) over the partitioned
Data_Out_Peak_Amp tree. Keeps only rows where the chosen channel has a peak,
which is all we need for cyclic-top analysis and keeps the table small.
"""
import pyarrow.dataset as ds
import pandas as pd


def load_peak_amplitudes(peak_amp_dir, channel):
    """Load peaks for one channel across every ELR / TrackID / date.

    Returns a tidy DataFrame: ELR, TrackID, Location_m, date, amplitude.
    """
    dataset = ds.dataset(str(peak_amp_dir), format="parquet", partitioning="hive")
    cols = ["ELR", "TrackID", "Location_m", "Date", channel]
    table = dataset.to_table(columns=cols, filter=ds.field(channel).is_valid())
    df = table.to_pandas().rename(columns={channel: "amplitude"})
    df["date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df.dropna(subset=["amplitude"]).reset_index(drop=True)
