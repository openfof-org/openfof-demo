import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Sequence, Optional

def excel_to_csv_single(excel_path, csv_path: Optional[str|Path]=None) -> Path:
    excel_path = Path(excel_path)
    xls = pd.ExcelFile(excel_path)
    if len(xls.sheet_names) != 1:
        raise ValueError(f"{excel_path.name}: expected 1 sheet, found {len(xls.sheet_names)}: {xls.sheet_names}")

    df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
    out = Path(csv_path) if csv_path else excel_path.with_suffix(".csv")
    df.to_csv(out, index=False)
    return out

# --- replace your loader with this safer version ---
def load_prices_from_csvs(
    csv_files: Sequence[str|Path],
    date_col: str = "Date",
    price_col: str = "Close",
    resample: bool = True,
    ffill_limit: int = 3,   # forward-fill up to 3 days
) -> pd.DataFrame:
    series = []
    for fp in csv_files:
        fp = Path(fp)
        tkr = fp.stem
        df = pd.read_csv(fp, usecols=[date_col, price_col])
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=[date_col]).sort_values(date_col)
        s = df.set_index(date_col)[price_col].astype(float).rename(tkr)
        series.append(s)

    if not series:
        raise ValueError("No valid CSVs loaded.")

    # 1) Outer join (union of dates)
    prices = pd.concat(series, axis=1, join="outer").sort_index()

    # 2) Optional: resample to daily and forward-fill small gaps
    if resample:
        prices = prices.resample("B").last()         # business days
        prices = prices.ffill(limit=ffill_limit)

    return prices

def returns_corr(prices: pd.DataFrame, absolute: bool = False, min_periods: int = 5) -> pd.DataFrame:
    rets = prices.pct_change()
    corr = rets.corr(min_periods=min_periods)  # pairwise, ignores NaNs
    return corr.abs() if absolute else corr

def plot_lower_triangle_heatmap(
    corr: pd.DataFrame,
    title: str = "Correlation Heatmap (Lower Triangle)",
    vmin: float = 0.0,
    vmax: float = 1.0,
    cmap: str = "RdYlGn_r",  # green=neg, red=pos (reversed RdYlGn)
    annotate: bool = True,
    diag: bool = True  # keep diagonal values
):
    labels = corr.columns.to_list()
    n = len(labels)

    k = 1 if diag else 0
    mask = np.triu(np.ones((n, n), dtype=bool), k=k)
    data = corr.values.copy()
    data[mask] = np.nan

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(data, vmin=vmin, vmax=vmax, cmap=cmap)

    ax.set_xticks(range(n)); ax.set_yticks(range(n))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_yticklabels(labels)
    ax.set_title(title)

    if annotate:
        for i in range(n):
            for j in range(i + (0 if diag else 1)):  # j <= i (or < i) -> lower triangle
                val = data[i, j]
                if np.isnan(val):
                    continue
                # contrast-aware text color
                txt_color = "white" if (vmin < 0 and abs(val) > 0.6) or (vmin == 0 and val > 0.6*(vmax-vmin)+vmin) else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=9, color=txt_color)

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
    csv_files = sorted(Path("assets").glob("*.csv"))
    prices = load_prices_from_csvs(csv_files, date_col="Date", price_col="Close")
    corr = returns_corr(prices)    
    plot_lower_triangle_heatmap(corr)
