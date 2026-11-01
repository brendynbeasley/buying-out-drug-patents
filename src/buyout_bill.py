"""Extension: what Kremer's patent buyout would cost for the drugs Medicare spends the most on.

Kremer proposed that the government buy a patent at its private value times a markup of about two and put it
in the public domain. Generic entry is the closest thing to a buyout that happens every year: the patent ends,
other firms copy the drug, and the price falls toward cost. This script

  1. finds every pill-form molecule whose generics took over in Medicare Part D between 2014 and 2022, and
     measures how far its price per dose fell and how far its use rose two years later, net of the change
     for drugs still under patent over the same years;
  2. relates the price fall to the number of generic makers, Kremer's claim that drug markets would be
     competitive without patents;
  3. turns the average price fall into a private value (the rent a patent earns) for every brand-only pill in
     Part D in 2024, using each drug's remaining compound-patent and exclusivity term in the FDA Orange Book,
     and prices a buyout at Kremer's markup.

Run from the repository root:
    python src/buyout_bill.py
The first run downloads the CMS Part D historical file (55 MB) into data/raw/partd/. The FDA Orange Book
extract is committed in data/raw/. Outputs go to results/.
"""

import io
import re
import urllib.request
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PARTD = RAW / "partd"
OUT = ROOT / "results"
PARTD_URL = ("https://data.cms.gov/sites/default/files/2026-06/"
             "Medicare%20Part%20D%20Spending%20by%20Drug-Excel%20Reports%20including%20Historical%20Data%20RY26.zip")
ORANGE_BOOK = RAW / "orange_book_20261101.zip"     # FDA Orange Book data files, downloaded 2026-11-01
AS_OF = pd.Timestamp("2026-10-09")                 # date stamped on the Orange Book files

# Rules fixed before looking at results.
RELEASES = range(2016, 2025)   # CMS release Y covers calendar years Y-4..Y; entry year E = Y-2 uses all five
PRE_MAX_GSHARE = 0.05          # generics under 5% of the molecule's Part D doses in E-2 and E-1
POST_MIN_GSHARE = 0.50         # generics at least half of doses by E+1 and E+2
MIN_SPEND = 10e6               # gross Part D spending in E-1 (dollars); drops very small products
SOLID_SHARE = 0.5              # at least half of the molecule's Orange Book listings are oral tablets or capsules
MARKUP = 2.0                   # Kremer's markup (WP 6304 abstract and p. 17: "perhaps two", "at least twice")
RATES = [0.07, 0.03]           # real discount rates, OMB Circular A-4 (2003)
PROTECT_CODES = ("NCE", "ODE", "PED")   # Orange Book exclusivities that block generic copies of the molecule
TRIAL_FUND = 100e6             # Kremer's suggested two-year appropriation for trial buyouts (WP 6304 p. 47)
N_TOP = 15
N_BOOT = 2000
SEED = 1998


# ----------------------------------------------------------------------------- Part D
def fetch_partd():
    if PARTD.exists() and len(list(PARTD.glob("partd_release_*.xlsx"))) == len(RELEASES):
        return
    PARTD.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {PARTD_URL}")
    data = urllib.request.urlopen(PARTD_URL, timeout=600).read()
    with zipfile.ZipFile(io.BytesIO(data)) as outer:
        for name in outer.namelist():
            year = re.search(r"DYT(\d{4})", name).group(1)
            with zipfile.ZipFile(io.BytesIO(outer.read(name))) as inner:
                xl = [n for n in inner.namelist() if n.endswith(".xlsx")][0]
                (PARTD / f"partd_release_{year}.xlsx").write_bytes(inner.read(xl))


def first_word(s):
    w = re.findall(r"[a-z]+", str(s).lower())
    return w[0] if w else ""


def read_release(year):
    """The 'Spending & Utilization' sheet as product x calendar year rows."""
    df = pd.read_excel(PARTD / f"partd_release_{year}.xlsx", sheet_name=1, header=None, engine="openpyxl")
    hdr = df.index[df.iloc[:, 0].astype(str).str.strip() == "Brand Name"][0]
    labels = df.iloc[hdr].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    body = df.iloc[hdr + 1:]
    makers = pd.to_numeric(body.iloc[:, list(labels).index("Number of Manufacturers")], errors="coerce")
    starts = [(i, int(re.search(r"(\d{4})", v).group(1))) for i, v in enumerate(df.iloc[hdr - 1])
              if isinstance(v, str) and "Calendar Year" in v]
    out = []
    for j, (i, cal) in enumerate(starts):
        end = starts[j + 1][0] if j + 1 < len(starts) else len(labels)
        blk = body.iloc[:, i:end]
        blk.columns = labels[i:end]
        out.append(pd.DataFrame({
            "brand": body.iloc[:, 0].astype(str).str.strip(), "generic": body.iloc[:, 1].astype(str).str.strip(),
            "makers": makers, "year": cal, "spend": pd.to_numeric(blk["Total Spending"], errors="coerce"),
            "units": pd.to_numeric(blk["Total Dosage Units"], errors="coerce")}))
    p = pd.concat(out, ignore_index=True)
    n0 = len(p)
    p = p[p.units > 0].copy()
    p["mol"] = p.generic.str.lower().str.replace(r"\s+", " ", regex=True).str.strip()
    p["is_brand"] = [first_word(b) != first_word(g) for b, g in zip(p.brand, p.generic)]
    print(f"  release {year}: {n0:,} product-years, kept {len(p):,} with positive doses "
          f"(dropped {n0 - len(p):,} blank or suppressed); {p.mol.nunique():,} molecules")
    return p


def molecule_panel(p):
    g = p.groupby(["mol", "year", "is_brand"])[["spend", "units"]].sum().unstack("is_brand", fill_value=0)
    m = pd.DataFrame({"spend": g["spend"].sum(axis=1), "units": g["units"].sum(axis=1),
                      "gunits": g["units"].get(False, 0)})
    m["gshare"] = m.gunits / m.units
    m["lnp"] = np.log(m.spend / m.units)
    m["lnq"] = np.log(m.units)
    return {v: m[v].unstack("year") for v in ["spend", "units", "gshare", "lnp", "lnq"]}


# ----------------------------------------------------------------------------- Orange Book
def ingredient_key(parts):
    return frozenset(w[0][:6] for c in parts if (w := re.findall(r"[a-z]+", c.lower())))


def orange_book():
    with zipfile.ZipFile(ORANGE_BOOK) as z:
        prod = pd.read_csv(z.open("products.txt"), sep="~", dtype=str)
        pat = pd.read_csv(z.open("patent.txt"), sep="~", dtype=str)
        exc = pd.read_csv(z.open("exclusivity.txt"), sep="~", dtype=str)
    prod["key"] = [ingredient_key(s.split(";")) for s in prod.Ingredient]
    prod["solid"] = prod["DF;Route"].str.match(r"^(TABLET|CAPSULE)[^;]*;ORAL")
    pat["date"] = pd.to_datetime(pat.Patent_Expire_Date_Text, format="%b %d, %Y", errors="coerce")
    exc["date"] = pd.to_datetime(exc.Exclusivity_Date, format="%b %d, %Y", errors="coerce")
    print(f"Orange Book: {len(prod):,} products, {len(pat):,} patent listings, {len(exc):,} exclusivities")
    return prod, pat, exc


def protection_end(trade, prod, pat, exc):
    """Latest compound (drug-substance) patent, NCE, orphan or pediatric exclusivity on the brand's NDAs.
    Also returns which listing sets the end date ('compound patent' or the exclusivity code family)."""
    ndas = prod[(prod.Trade_Name == trade) & (prod.Appl_Type == "N")].Appl_No.unique()
    if len(ndas) == 0:
        return None, None, None, None
    ds = pat[pat.Appl_No.isin(ndas) & (pat.Drug_Substance_Flag == "Y")].date.max()
    e = exc[exc.Appl_No.isin(ndas) & exc.Exclusivity_Code.str.startswith(PROTECT_CODES)]
    ex = e.date.max()
    if pd.isna(ds):
        return None, ds, ex, None
    if pd.notna(ex) and ex > ds:
        return ex, ds, ex, e.loc[e.date == ex, "Exclusivity_Code"].iloc[0][:3]
    return ds, ds, ex, "compound patent"


# ----------------------------------------------------------------------------- generic entry
def find_events(W, Y, solid):
    E = Y - 2
    yrs = list(range(E - 2, E + 3))
    gs, U = W["gshare"].reindex(columns=yrs), W["units"].reindex(columns=yrs)
    full = U.notna().all(axis=1)
    hit = (full & (gs[E - 2] < PRE_MAX_GSHARE) & (gs[E - 1] < PRE_MAX_GSHARE)
           & (gs[E + 1] >= POST_MIN_GSHARE) & (gs[E + 2] >= POST_MIN_GSHARE)
           & (W["spend"][E - 1] >= MIN_SPEND))
    big = full & (W["spend"][E - 1] >= MIN_SPEND) & gs.index.isin(list(solid))
    ctrl = {"lnp": gs.index[big & (gs < PRE_MAX_GSHARE).all(axis=1)],       # prices: brand-only pills
            "lnq": gs.index[big & (gs >= POST_MIN_GSHARE).all(axis=1)]}     # doses: pills generic all along
    ev = pd.DataFrame({"mol": gs.index[hit], "E": E, "release": Y})
    n_hit = len(ev)
    ev = ev[ev.mol.isin(solid)]
    print(f"  entry year {E}: {n_hit} molecules meet the entry rules, {len(ev)} are mainly pills; controls: "
          f"{len(ctrl['lnp'])} brand-only pills (price), {len(ctrl['lnq'])} long-generic pills (doses)")
    rows = []
    for k in [-2, 0, 1, 2]:
        dc = {v: (W[v].loc[ctrl[v], E + k] - W[v].loc[ctrl[v], E - 1]).mean() for v in ["lnp", "lnq"]}
        for m in ev.mol:
            dt = {v: W[v].loc[m, E + k] - W[v].loc[m, E - 1] for v in ["lnp", "lnq"]}
            rows.append(dict(mol=m, E=E, k=k, dlnp=dt["lnp"], dlnq=dt["lnq"], ctrl_dlnp=dc["lnp"],
                             ctrl_dlnq=dc["lnq"], n_ctrl_price=len(ctrl["lnp"]), n_ctrl_doses=len(ctrl["lnq"])))
    path = pd.DataFrame(rows)
    path["did_lnp"], path["did_lnq"] = path.dlnp - path.ctrl_dlnp, path.dlnq - path.ctrl_dlnq
    ev["spend_pre"] = W["spend"].loc[ev.mol, E - 1].values
    ev["gshare_post"] = W["gshare"].loc[ev.mol, E + 2].values
    ev["price_pre"] = np.exp(W["lnp"].loc[ev.mol, E - 1].values)     # gross spending per dose, E-1
    ev["price_post"] = np.exp(W["lnp"].loc[ev.mol, E + 2].values)    # same, E+2 (brand and generics)
    return ev, path


def summarize(ev):
    w = ev.spend_pre.to_numpy()
    R, x, xt = ev.R.to_numpy(), ev.x.to_numpy(), ev.x_trend.to_numpy()
    rent = R * w
    return dict(R_mean=R.mean(), R_median=np.median(R), R_spend_weighted=(R * w).sum() / w.sum(),
                x_mean=x.mean(), x_median=np.median(x), x_rent_weighted=(x * rent).sum() / rent.sum(),
                dwl_per_rent=(0.5 * R * x * w).sum() / rent.sum(),
                dwl_per_spend=(0.5 * R * x * w).sum() / w.sum(),
                x_trend_median=np.median(xt), x_trend_rent_weighted=(xt * rent).sum() / rent.sum(),
                dwl_per_rent_trend=(0.5 * R * xt * w).sum() / rent.sum())


def annuity(T, r):
    return (1 - (1 + r) ** (-T)) / r


# ----------------------------------------------------------------------------- main
def main():
    OUT.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)
    fetch_partd()
    prod, pat, exc = orange_book()
    solid_share = prod.groupby("key").solid.mean()

    print("Reading Part D releases")
    panels = {y: read_release(y) for y in RELEASES}
    Ws = {y: molecule_panel(p) for y, p in panels.items()}
    solid = {m for W in Ws.values() for m in W["units"].index
             if solid_share.get(ingredient_key(m.split("/")), 0) >= SOLID_SHARE}

    print("Generic entries")
    evs, paths = zip(*[find_events(Ws[y], y, solid) for y in RELEASES])
    ev, path = pd.concat(evs, ignore_index=True), pd.concat(paths, ignore_index=True)
    ev = ev.sort_values(["mol", "E"]).drop_duplicates("mol", keep="first")
    path = path.merge(ev[["mol", "E"]], on=["mol", "E"])
    k2 = path[path.k == 2].set_index("mol")
    ev = ev.set_index("mol")
    ev["did_lnp"], ev["did_lnq"] = k2.did_lnp, k2.did_lnq
    ev["raw_dlnp"], ev["raw_dlnq"] = k2.dlnp, k2.dlnq
    ev["R"], ev["x"] = 1 - np.exp(ev.did_lnp), np.exp(ev.did_lnq) - 1
    # Robustness: extend each drug's own pre-entry dose trend (E-2 to E-1, net of controls) three years forward.
    ev["did_lnq_pre"] = path[path.k == -2].set_index("mol").did_lnq
    ev["x_trend"] = np.exp(ev.did_lnq + 3 * ev.did_lnq_pre) - 1
    p24 = panels[RELEASES[-1]]
    makers = []
    for m, r in ev.iterrows():
        p = panels[int(r.release)]
        makers.append(p[(p.mol == m) & (p.year == r.E + 2) & ~p.is_brand].makers.sum())
    ev["generic_makers"] = makers
    brand_names = []
    for m, r in ev.iterrows():
        p = panels[int(r.release)]
        b = p[(p.mol == m) & (p.year == r.E - 1) & p.is_brand].sort_values("spend", ascending=False)
        brand_names.append(b.brand.iloc[0] if len(b) else "")
    ev["brand"] = brand_names
    ev = ev.reset_index()
    print(f"Unique generic entries kept: {len(ev)} molecules, entry years {ev.E.min()}-{ev.E.max()}")
    ev.sort_values("spend_pre", ascending=False).to_csv(OUT / "entry_events.csv", index=False)

    # Headline summaries with bootstrap over events.
    s = summarize(ev)
    boot = pd.DataFrame([summarize(ev.iloc[rng.integers(0, len(ev), len(ev))]) for _ in range(N_BOOT)])
    pre = path[path.k == -2]
    summ = pd.DataFrame({"statistic": list(s), "estimate": list(s.values()),
                         "ci_low": boot.quantile(0.025).values, "ci_high": boot.quantile(0.975).values,
                         "se_boot": boot.std(ddof=1).values})
    summ.loc[len(summ)] = ["pretrend_did_lnp_mean", pre.did_lnp.mean(), np.nan, np.nan,
                           pre.did_lnp.std(ddof=1) / np.sqrt(len(pre))]
    summ.loc[len(summ)] = ["pretrend_did_lnq_mean", pre.did_lnq.mean(), np.nan, np.nan,
                           pre.did_lnq.std(ddof=1) / np.sqrt(len(pre))]
    summ.loc[len(summ)] = ["raw_R_spend_weighted",
                           ((1 - np.exp(ev.raw_dlnp)) * ev.spend_pre).sum() / ev.spend_pre.sum(), np.nan, np.nan, np.nan]
    summ.loc[len(summ)] = ["n_events", len(ev), np.nan, np.nan, np.nan]
    summ.loc[len(summ)] = ["spend_pre_total", ev.spend_pre.sum(), np.nan, np.nan, np.nan]
    summ.to_csv(OUT / "entry_summary.csv", index=False)
    print(summ.round(4).to_string(index=False))

    # Path by year relative to entry, with bootstrap bands over molecules.
    rows = []
    for k, g in path.groupby("k"):
        for v in ["did_lnp", "did_lnq"]:
            b = [g[v].to_numpy()[rng.integers(0, len(g), len(g))].mean() for _ in range(N_BOOT)]
            rows.append(dict(k=k, var=v, mean=g[v].mean(), ci_low=np.percentile(b, 2.5),
                             ci_high=np.percentile(b, 97.5), n=len(g)))
    rows += [dict(k=-1, var=v, mean=0.0, ci_low=0.0, ci_high=0.0, n=len(ev)) for v in ["did_lnp", "did_lnq"]]
    pth = pd.DataFrame(rows).sort_values(["var", "k"])
    pth.to_csv(OUT / "entry_path.csv", index=False)

    # Competition: price fall against the number of generic makers.
    ev["makers_bin"] = pd.cut(ev.generic_makers, [0, 2, 5, 9, 1000], labels=["1-2", "3-5", "6-9", "10+"])
    bym = ev.groupby("makers_bin", observed=True).agg(n=("R", "size"), R_median=("R", "median"), R_mean=("R", "mean"),
                                                     x_median=("x", "median"), spend_pre=("spend_pre", "sum"))
    bym.to_csv(OUT / "entry_by_makers.csv")
    print(bym.round(3).to_string())
    ev["ln_makers"] = np.log(ev.generic_makers.clip(lower=1))
    fit = smf.ols("did_lnp ~ ln_makers + C(E)", data=ev).fit(cov_type="HC1")
    reg = pd.DataFrame({"term": ["ln_makers"], "coef": [fit.params["ln_makers"]], "se_hc1": [fit.bse["ln_makers"]],
                        "t": [fit.tvalues["ln_makers"]], "p": [fit.pvalues["ln_makers"]],
                        "ci_low": [fit.conf_int().loc["ln_makers", 0]], "ci_high": [fit.conf_int().loc["ln_makers", 1]],
                        "n": [int(fit.nobs)], "r2": [fit.rsquared]})
    reg.to_csv(OUT / "makers_regression.csv", index=False)
    print(f"did_lnp on ln(generic makers), entry-year effects, HC1: b = {fit.params['ln_makers']:.3f} "
          f"(se {fit.bse['ln_makers']:.3f}, p = {fit.pvalues['ln_makers']:.3f}), N = {int(fit.nobs)}")

    # ------------------------------------------------------------- the buyout bill, 2024 Part D
    y24 = RELEASES[-1]
    d = p24[p24.year == y24]
    generic_mols = set(d[~d.is_brand].mol)
    b = d[d.is_brand & ~d.mol.isin(generic_mols)].groupby(["brand", "mol"], as_index=False)[["spend", "units"]].sum()
    total_partd = d.spend.sum()
    print(f"\nPart D {y24}: ${total_partd / 1e9:.1f}B gross spending; {len(b):,} brand products with no generic "
          f"version of the molecule (${b.spend.sum() / 1e9:.1f}B)")
    b["trade"] = b.brand.str.upper().str.replace(r"[*]", "", regex=True).str.strip()
    ends = [protection_end(t, prod, pat, exc) for t in b.trade]
    b["protection_end"], b["compound_patent"], b["exclusivity"], b["protection_set_by"] = zip(*ends)
    b["in_orange_book"] = [t in set(prod.Trade_Name) for t in b.trade]
    anda_keys = set(prod[prod.Appl_Type == "A"].key)
    brand_key = prod[prod.Appl_Type == "N"].groupby("Trade_Name").key.first()
    b["generic_approved"] = [brand_key.get(t) in anda_keys for t in b.trade]   # an ANDA for the same ingredients
    n_ob = int(b.in_orange_book.sum())
    b = b[b.protection_end.notna()].copy()
    b["years_left"] = ((pd.to_datetime(b.protection_end) - AS_OF).dt.days / 365.25).clip(lower=0)
    n_comp = len(b)
    b = b[b.years_left > 0].copy()
    print(f"  {n_ob} match an Orange Book trade name; {n_comp} list a compound patent; "
          f"{len(b)} still protected after {AS_OF.date()} (${b.spend.sum() / 1e9:.1f}B in {y24})")
    R = s["R_spend_weighted"]
    R_lo, R_hi = summ.set_index("statistic").loc["R_spend_weighted", ["ci_low", "ci_high"]]
    x = s["x_rent_weighted"]
    b["spend_per_dose"] = b.spend / b.units
    b["rent_per_year"] = R * b.spend
    for r in RATES:
        tag = f"{int(r * 100)}pct"
        a = annuity(b.years_left, r)
        b[f"private_value_{tag}"] = b.rent_per_year * a
        b[f"buyout_offer_{tag}"] = MARKUP * b[f"private_value_{tag}"]
        b[f"net_cost_{tag}"] = (MARKUP - 1) * b[f"private_value_{tag}"]
        b[f"dwl_recovered_{tag}"] = 0.5 * R * x * b.spend * a
    b["dwl_recovered_7pct_trend"] = 0.5 * R * s["x_trend_rent_weighted"] * b.spend * annuity(b.years_left, 0.07)
    b["offer_7pct_R_low"] = MARKUP * R_lo * b.spend * annuity(b.years_left, 0.07)
    b["offer_7pct_R_high"] = MARKUP * R_hi * b.spend * annuity(b.years_left, 0.07)
    b["trial_fund_days"] = TRIAL_FUND / (MARKUP * b.rent_per_year) * 365.25
    b = b.sort_values("spend", ascending=False)
    keep = ["brand", "mol", "spend", "units", "spend_per_dose", "compound_patent", "exclusivity", "protection_end",
            "protection_set_by", "years_left",
            "generic_approved",
            "rent_per_year", "private_value_7pct", "buyout_offer_7pct", "net_cost_7pct", "dwl_recovered_7pct",
            "dwl_recovered_7pct_trend", "private_value_3pct", "buyout_offer_3pct", "net_cost_3pct",
            "dwl_recovered_3pct",
            "offer_7pct_R_low", "offer_7pct_R_high", "trial_fund_days"]
    b[keep].to_csv(OUT / "buyout_all_protected.csv", index=False)
    top = b.head(N_TOP)
    top[keep].to_csv(OUT / "buyout_named.csv", index=False)
    print(top[["brand", "spend", "protection_end", "years_left", "generic_approved", "buyout_offer_7pct"]]
          .to_string(index=False))

    tot = []
    for label, g in [(f"top {N_TOP}", top), ("all protected Orange Book brands", b)]:
        tot.append(dict(group=label, n_drugs=len(g), spend_2024=g.spend.sum(), rent_per_year=g.rent_per_year.sum(),
                        private_value_7pct=g.private_value_7pct.sum(), buyout_offer_7pct=g.buyout_offer_7pct.sum(),
                        net_cost_7pct=g.net_cost_7pct.sum(), dwl_recovered_7pct=g.dwl_recovered_7pct.sum(),
                        dwl_recovered_7pct_trend=g.dwl_recovered_7pct_trend.sum(),
                        buyout_offer_3pct=g.buyout_offer_3pct.sum(), offer_7pct_R_low=g.offer_7pct_R_low.sum(),
                        offer_7pct_R_high=g.offer_7pct_R_high.sum(),
                        spend_weighted_years_left=np.average(g.years_left, weights=g.spend),
                        n_generic_approved=int(g.generic_approved.sum()),
                        n_end_set_by_exclusivity=int((g.protection_set_by != "compound patent").sum()),
                        offer_7pct_end_set_by_exclusivity=g.loc[g.protection_set_by != "compound patent",
                                                                "buyout_offer_7pct"].sum(),
                        partd_total_2024=total_partd, rent_share_used=R, x_used=x, markup=MARKUP))
    tot = pd.DataFrame(tot)
    tot.to_csv(OUT / "buyout_totals.csv", index=False)
    print(tot.T.to_string())

    # ------------------------------------------------------------- figures
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), sharex=True)
    for ax, v, title in [(axes[0], "did_lnp", "Price per dose"), (axes[1], "did_lnq", "Doses dispensed")]:
        q = pth[pth["var"] == v]
        ax.axhline(0, color="#bbbbbb", lw=1)
        ax.axvline(-0.5, color="#bbbbbb", lw=1, ls=":")
        ax.fill_between(q.k, 100 * (np.exp(q.ci_low) - 1), 100 * (np.exp(q.ci_high) - 1), color="#1f5f8b", alpha=0.2)
        ax.plot(q.k, 100 * (np.exp(q["mean"]) - 1), color="#1f5f8b", marker="o", lw=2)
        ax.set_title(title, fontsize=10)
        ax.set_xticks([-2, -1, 0, 1, 2])
        ax.set_xlabel("Years from first generic sales")
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("% change since the year before entry,\nnet of brand-only drugs")
    fig.suptitle(f"{len(ev)} drugs that went generic in Medicare Part D, 2014-2022", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "entry_path.png", dpi=150)

    fig, ax = plt.subplots(figsize=(8, 5.2))
    t = top.iloc[::-1]
    ax.barh(t.brand, t.spend / 1e9, color="#c7d6e3", label=f"Part D gross spending, {y24}")
    ax.barh(t.brand, t.buyout_offer_7pct / 1e9, height=0.4, color="#1f5f8b",
            label="Buyout offer at Kremer's markup (2 x private value)")
    for i, (_, r) in enumerate(t.iterrows()):
        ax.text(max(r.spend, r.buyout_offer_7pct) / 1e9 + 0.3, i, f"protected to {pd.Timestamp(r.protection_end):%Y}",
                va="center", fontsize=8, color="#555555")
    ax.set_xlabel("$ billion")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="lower right", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(OUT / "buyout_named.png", dpi=150)
    print("\nWrote entry_events.csv, entry_summary.csv, entry_path.csv, entry_by_makers.csv, makers_regression.csv,"
          " buyout_all_protected.csv, buyout_named.csv, buyout_totals.csv, entry_path.png, buyout_named.png")


if __name__ == "__main__":
    main()
