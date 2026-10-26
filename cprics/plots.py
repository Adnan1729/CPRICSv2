"""cprics/plots.py — accessible Plotly figures for the results.

Each returns a plotly Figure; the reports notebook writes them to standalone
HTML so colleagues open them in a browser with no Python.
"""
import plotly.graph_objects as go
from .location import to_mileage
import pandas as pd

CATEGORY_LINES = {"D": 18, "C": 20, "B": 23, "A": 26, "I": 30}


def before_after_figure(isl, site_id):
    """Incumbent (hard, steps) vs C-PRICS (continuous) for one tracked site."""
    g = isl[isl.site_id == site_id].sort_values("date")
    loc = (f"{g.ELR.iloc[0]} track {int(g.TrackID.iloc[0])}, "
           f"{to_mileage(g.start_location.iloc[-1])}-{to_mileage(g.end_location.iloc[-1])}")
    hard = g.groupby("date")["hard_amplitude"].max()
    cont = g.groupby("date")["amplitude"].max()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hard.index, y=hard.values, mode="lines+markers",
                             name="Module 11(current)", line=dict(width=2.5)))
    fig.add_trace(go.Scatter(x=cont.index, y=cont.values, mode="lines+markers",
                             name="C-PRICS (continuous)",
                             line=dict(width=2.5, dash="dash")))
    for cat, y in CATEGORY_LINES.items():
        fig.add_hline(y=y, line=dict(color="grey", width=0.5, dash="dot"),
                      annotation_text=f" {cat}", annotation_position="right")
    fig.update_layout(
        title=f"Cyclic top over time — {loc}",
        xaxis_title="Inspection date", yaxis_title="Cyclic-top amplitude (mm)",
        template="plotly_white", hovermode="x unified",
        width=950, height=520,
        legend=dict(orientation="h", y=1.03, x=0))
    return fig


def early_warning_table(isl, concern=18, critical=30):
    """Per critical site: months of advance warning each method gives."""
    rows = []
    for sid, g in isl.groupby("site_id"):
        g = g.sort_values("date")
        if g.hard_amplitude.max() < critical:
            continue
        crit = g.loc[g.hard_amplitude >= critical, "date"].iloc[0]
        def lead(dates):                      # months before critical that concern was first flagged
            d = dates[dates < crit]
            return (crit - d.iloc[0]).days / 30.44 if len(d) else 0.0
        rows.append({"site_id": sid,
                     "module11": lead(g.loc[g.hard_amplitude >= concern, "date"]),
                     "cprics":   lead(g.loc[g.amplitude      >= concern, "date"])})
    return pd.DataFrame(rows)


def early_warning_figure(isl):
    """Dumbbell: each row a critical site; how far ahead each method warned."""
    import plotly.graph_objects as go
    t = early_warning_table(isl).sort_values("cprics").reset_index(drop=True)
    fig = go.Figure()
    for i, r in t.iterrows():
        fig.add_trace(go.Scatter(x=[r.module11, r.cprics], y=[i, i], mode="lines",
                                 line=dict(color="lightgrey", width=2), showlegend=False))
    fig.add_trace(go.Scatter(x=t.module11, y=t.index, mode="markers",
                             name="Module 11 (current)", marker=dict(color="#6a7fdb", size=9)))
    fig.add_trace(go.Scatter(x=t.cprics, y=t.index, mode="markers",
                             name="C-PRICS", marker=dict(color="#e2504f", size=9)))
    fig.update_layout(
        title="Advance warning before a site becomes critical (category I)<br>"
              "<sub>each row is one critical site — further right is earlier warning</sub>",
        xaxis_title="Months of advance warning", template="plotly_white",
        height=700, width=850, legend=dict(orientation="h", y=1.03, x=0),
        yaxis=dict(showticklabels=False, title="critical sites"))
    return fig, t
