# config.py — the one place for paths and parameters.
from pathlib import Path

DATA_ROOT = Path(__file__).parent / "data"      # data folders live under here

PEAK_AMP_DIR = DATA_ROOT / "Data_Out_Peak_Amp"  # sub-threshold input (used next)
CYC_DIR      = DATA_ROOT / "CYC"                 # incumbent reports (used first)
OUTPUTS_DIR  = Path(__file__).parent / "outputs"

MODELS_DIR = Path(__file__).parent / "models"

# parameters
FOCUS_WAVELENGTH    = "9"      # most common exceedance band in our data
RESET_DROP_FRACTION = 0.30     # fall >30% of current level = likely tamp
CATEGORY_THRESHOLDS = {"D": 18, "C": 20, "B": 23, "A": 26, "I": 30}  # mm


