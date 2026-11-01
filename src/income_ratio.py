"""Kremer (1998): how much of a new drug's social value can a patent holder capture?

Kremer reports (NBER WP 6304, p. 8) that if willingness to pay for a drug is proportional to income, the US
income distribution implies that the social value of a new drug is 2.6 times the profit of a monopolist who
cannot price discriminate, and that the deadweight loss from monopoly pricing is one quarter of profits plus
consumer surplus. This script redoes that calculation on Census household incomes for 1997 (the income year
closest to the paper) and 2025 (the latest), with bootstrap intervals, alternative income units, and a
positive marginal cost.

The monopolist picks one price p. A household with income y values the drug at k*y, so it buys if
k*y >= p. Because k scales every dollar figure equally, it drops out of every ratio reported here.

Run from the repository root:
    python src/income_ratio.py
Inputs are the two household extracts in data/raw/ (committed). If they are missing, the script downloads
the Census CPS ASEC files (18 MB and 139 MB) into data/raw/cps/ and rebuilds them.
"""

import io
import urllib.request
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "results"

ASEC = {  # income year: (Census URL, file inside the zip)
    1997: ("https://www2.census.gov/programs-surveys/cps/datasets/1998/march/mar98supp.zip", "mar98pub.cps"),
    2025: ("https://www2.census.gov/programs-surveys/cps/datasets/2026/march/asecpub26csv.zip", "hhpub26.csv"),
}
# March 1998 household record positions (1-based, inclusive), from the NBER dictionary cpsmar98.dct:
# h_numper 21-22, htotval 248-255, hsup_wgt 287-294 (two implied decimals). Record type '1' = household.
POS_1998 = {"persons": (21, 22), "income": (248, 255), "weight": (287, 294)}

PAPER_RATIO = 2.6         # social value / monopoly profit, Kremer WP 6304 p. 8
PAPER_DWL_SHARE = 0.25    # deadweight loss / (profit + consumer surplus), same page
MC_SHARES = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]   # marginal cost as a share of the monopoly price (sensitivity)
N_BOOT = 500              # household bootstrap draws for the main specification
SEED = 1998
WORKED_K = 0.01          # worked example: each household values the drug at 1% of its income
TAIL = 0.05               # flag optima where fewer than 5% of buyers are served (the top-coded income tail)


# ----------------------------------------------------------------------------- data
def build_extract(year):
    url, member = ASEC[year]
    cps = RAW / "cps"
    cps.mkdir(parents=True, exist_ok=True)
    zpath = cps / url.rsplit("/", 1)[1]
    if not zpath.exists():
        print(f"Downloading {url}")
        tmp = zpath.with_suffix(".part")
        tmp.write_bytes(urllib.request.urlopen(url, timeout=600).read())
        tmp.rename(zpath)
    with zipfile.ZipFile(zpath) as z:
        if year == 1997:
            rows = []
            for line in z.open(member):
                if line[:1] == b"1":
                    rows.append([int(line[a - 1:b]) for a, b in POS_1998.values()])
            h = pd.DataFrame(rows, columns=list(POS_1998))
            h["weight"] = h.weight / 100
        else:
            h = pd.read_csv(io.BytesIO(z.read(member)), usecols=["H_NUMPER", "HTOTVAL", "HSUP_WGT"])
            h = h.rename(columns={"H_NUMPER": "persons", "HTOTVAL": "income", "HSUP_WGT": "weight"})
            h["weight"] = h.weight / 100     # ASEC CSV weights carry two implied decimals
    h[["persons", "income", "weight"]].to_csv(RAW / f"asec_households_{year}.csv", index=False)


def load(year):
    f = RAW / f"asec_households_{year}.csv"
    if not f.exists():
        build_extract(year)
    h = pd.read_csv(f)
    n0 = len(h)
    h = h[(h.persons > 0) & (h.weight > 0)].copy()
    neg = int((h.income < 0).sum())
    h["income"] = h.income.clip(lower=0)
    print(f"{year}: {n0:,} household records; kept {len(h):,} occupied households with positive weight "
          f"(dropped {n0 - len(h):,} vacant or non-interview records); {neg} negative incomes set to zero; "
          f"{h.weight.sum() / 1e6:.1f} million households, weighted mean income ${np.average(h.income, weights=h.weight):,.0f}")
    return h


def units(h):
    """The three ways of turning household income into one buyer's willingness to pay."""
    n = h.persons.to_numpy(float)
    y = h.income.to_numpy(float)
    w = h.weight.to_numpy(float)
    return {"household": (y, w), "person_per_capita": (y / n, w * n), "person_equivalized": (y / np.sqrt(n), w * n)}


# ----------------------------------------------------------------------------- the calculation
def monopoly(y, w, c=0.0):
    """One-price monopolist facing values y (weights w) and marginal cost c.
    Returns profit, consumer surplus, deadweight loss and total social value, all per buyer."""
    o = np.argsort(-y, kind="stable")
    y, w = y[o], w[o]
    W = w.sum()
    share = np.cumsum(w) / W                    # share of buyers whose value is at least y_i
    profit = (y - c) * share
    i = int(np.argmax(profit))
    p = y[i]
    buys = y >= p
    gains = np.clip(y - c, 0, None)
    out = dict(price=p, share_buying=share[i], profit=profit[i],
               cs=float(((y - p) * w * buys).sum() / W),
               dwl=float((gains * w * ~buys).sum() / W),
               social_value=float((gains * w).sum() / W), mean_value=float((y * w).sum() / W))
    out["price_over_mean"] = p / out["mean_value"]
    out["ratio_sv_profit"] = out["social_value"] / out["profit"]
    out["dwl_share"] = out["dwl"] / (out["profit"] + out["cs"])
    out["dwl_per_profit"] = out["dwl"] / out["profit"]
    out["profit_share_sv"] = out["profit"] / out["social_value"]
    return out


def cost_for_share(y, w, m):
    """Marginal cost c such that c equals a share m of the monopoly price it induces (bisection)."""
    if m == 0:
        return 0.0
    lo, hi = 0.0, float(np.quantile(y, 0.999))
    for _ in range(60):
        c = (lo + hi) / 2
        if c / monopoly(y, w, c)["price"] < m:
            lo = c
        else:
            hi = c
    return (lo + hi) / 2


def bootstrap(y, w, rng):
    n = len(y)
    draws = []
    for _ in range(N_BOOT):
        idx = rng.integers(0, n, n)
        r = monopoly(y[idx], w[idx])
        draws.append((r["ratio_sv_profit"], r["dwl_share"]))
    return np.array(draws)


def profit_curve(y, w, grid):
    """Profit at each price (as a share of total social value), price expressed relative to mean value."""
    o = np.argsort(y)
    ys, ws = y[o], w[o]
    tail = ws[::-1].cumsum()[::-1] / ws.sum()       # share with value >= ys[i]
    mean = np.average(y, weights=w)
    prices = grid * mean
    idx = np.searchsorted(ys, prices, side="left")
    share = np.where(idx < len(ys), tail[np.minimum(idx, len(ys) - 1)], 0.0)
    return prices * share / mean


# ----------------------------------------------------------------------------- main
def main():
    OUT.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)
    rows, curves, load_weight_total = [], {}, {}
    grid = np.linspace(0, 4, 401)
    for year in ASEC:
        h = load(year)
        load_weight_total[year] = h.weight.sum()
        for unit, (y, w) in units(h).items():
            for m in MC_SHARES:
                c = cost_for_share(y, w, m)
                r = monopoly(y, w, c)
                r.update(year=year, unit=unit, mc_share_of_price=m, marginal_cost=c, n_records=len(y),
                         mc_share_achieved=c / r["price"], tail_solution=r["share_buying"] < TAIL)
                if unit == "household" and m == 0:
                    b = bootstrap(y, w, rng)
                    r["ratio_ci_low"], r["ratio_ci_high"] = np.percentile(b[:, 0], [2.5, 97.5])
                    r["dwl_share_ci_low"], r["dwl_share_ci_high"] = np.percentile(b[:, 1], [2.5, 97.5])
                    r["ratio_se"], r["dwl_share_se"] = b[:, 0].std(ddof=1), b[:, 1].std(ddof=1)
                rows.append(r)
        curves[year] = profit_curve(*units(h)["household"], grid)

    res = pd.DataFrame(rows)
    res["paper_ratio"], res["paper_dwl_share"] = PAPER_RATIO, PAPER_DWL_SHARE
    # Kremer's chain on p. 10: social/private at monopoly output (2) x 4/3 (duplication) x (1 + DWL share).
    res["kremer_chain"] = 2 * 4 / 3 * (1 + res.dwl_share)
    cols = ["year", "unit", "mc_share_of_price", "n_records", "mean_value", "price", "price_over_mean",
            "share_buying", "profit", "cs", "dwl", "social_value", "ratio_sv_profit", "ratio_ci_low", "ratio_ci_high", "ratio_se",
            "dwl_share", "dwl_share_ci_low", "dwl_share_ci_high", "dwl_share_se", "dwl_per_profit",
            "profit_share_sv", "kremer_chain", "marginal_cost", "mc_share_achieved", "tail_solution",
            "paper_ratio", "paper_dwl_share"]
    res[cols].to_csv(OUT / "income_ratio.csv", index=False)

    main_rows = res[(res.unit == "household") & (res.mc_share_of_price == 0)]
    # Worked example in dollars: a household values the drug at WORKED_K of its annual income.
    we = main_rows[["year", "mean_value", "price", "share_buying", "profit", "cs", "dwl", "social_value"]].copy()
    for c in ["mean_value", "price", "profit", "cs", "dwl", "social_value"]:
        we[c] = we[c] * WORKED_K
    we["households_millions"] = [load_weight_total[y] / 1e6 for y in we.year]
    we["k"] = WORKED_K
    we.to_csv(OUT / "worked_example.csv", index=False)
    print("\nKremer's calculation, households, zero marginal cost (paper: ratio 2.6, DWL share 0.25)")
    for _, r in main_rows.iterrows():
        print(f"  {r.year}: monopoly price = {r.price / r.mean_value:.2f} x mean income, {r.share_buying:.1%} buy; "
              f"social value / profit = {r.ratio_sv_profit:.2f} [{r.ratio_ci_low:.2f}, {r.ratio_ci_high:.2f}]; "
              f"DWL / (profit + CS) = {r.dwl_share:.3f} [{r.dwl_share_ci_low:.3f}, {r.dwl_share_ci_high:.3f}]")
    print("\nAll units and marginal costs:")
    print(res[["year", "unit", "mc_share_of_price", "mc_share_achieved", "ratio_sv_profit", "dwl_share",
               "share_buying"]].round(3).to_string(index=False))

    pc = pd.DataFrame({"price_over_mean_income": grid, **{f"profit_share_sv_{y}": v for y, v in curves.items()}})
    pc.to_csv(OUT / "profit_curve.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for (year, v), col in zip(curves.items(), ["#8c8c8c", "#1f5f8b"]):
        r = main_rows[main_rows.year == year].iloc[0]
        ax.plot(grid, v, color=col, lw=2, label=f"{year} incomes")
        ax.scatter([r.price / r.mean_value], [r.profit_share_sv], color=col, zorder=3)
        ax.annotate(f"best price: {r.share_buying:.0%} buy,\nprofit = 1/{r.ratio_sv_profit:.2f} of value",
                    (r.price / r.mean_value, r.profit_share_sv), xytext=(30, 22) if year == 1997 else (15, -100),
                    textcoords="offset points", fontsize=8.5, color=col,
                    arrowprops=dict(arrowstyle="-", color=col, lw=0.8))
    ax.set_xlabel("Price, as a multiple of the average household's willingness to pay")
    ax.set_ylabel("Monopoly profit as a share of\nthe drug's total social value")
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 0.45)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False)
    ax.set_title("Willingness to pay proportional to household income (Kremer's assumption)", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "profit_curve.png", dpi=150)
    print("\nWrote results/income_ratio.csv, results/worked_example.csv, results/profit_curve.csv, "
          "results/profit_curve.png")


if __name__ == "__main__":
    main()
