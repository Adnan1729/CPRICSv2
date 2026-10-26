"""cprics/location.py — turn metres-along-ELR into the NR mileage convention."""
METRES_TO_YARDS = 1.0936133


def to_mileage(location_m):
    """Metres along an ELR -> 'MMMmYYYYy' (miles + yards), as the CYC reports use."""
    yards = location_m * METRES_TO_YARDS
    miles = int(yards // 1760)
    rem = int(round(yards - miles * 1760))
    return f"{miles}m{rem:04d}y"


def add_mileage(islands):
    out = islands.copy()
    out["start_mileage"] = out["start_location"].map(to_mileage)
    out["end_mileage"] = out["end_location"].map(to_mileage)
    return out
