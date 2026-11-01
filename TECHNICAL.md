# Technical notes

This is the technical companion to the [README](README.md). It covers the original study, the data, the rules,
every test statistic and how to reproduce the results. All tables are in [results/FINDINGS.md](results/FINDINGS.md).

## The original study

Michael Kremer, "Patent Buyouts: A Mechanism for Encouraging Innovation," *Quarterly Journal of Economics* 113(4),
1998, pp. 1137-1167 (NBER Working Paper 6304, December 1997). Kremer proposes that governments estimate a patent's
private value by sealed-bid auction, offer the holder that value times a markup $`M`$ ("perhaps two"), place most
purchased patents in the public domain, and sell a random few to the high bidder so that bids stay honest. The
quantitative case for the markup rests on one calculation (WP p. 8, credited to Atif Mian): if willingness to pay is
proportional to income, the US income distribution implies that the social value of a new drug is 2.6 times the
profit of a single-price monopolist, and that deadweight loss is one quarter of profit plus consumer surplus. With
spillovers and duplicative research the paper reaches 3.33 times the private return (p. 10) and settles on a markup
of two.

## Headline results

| Quantity | Kremer (1998) | This repository | 95% interval |
|---|---|---|---|
| Social value ÷ profit, 1997 households | 2.6 | 2.656 | [2.628, 2.682] |
| DWL ÷ (profit + CS), 1997 households | 0.25 | 0.275 | [0.269, 0.282] |
| Social value ÷ profit, 2025 households | | 2.831 | [2.797, 2.859] |
| DWL ÷ (profit + CS), 2025 households | | 0.269 | [0.262, 0.275] |
| Price fall at generic entry, spend-weighted (99 Part D pills) | | 0.679 | [0.613, 0.736] |
| Rise in doses at entry, rent-weighted | | 0.026 | [-0.119, 0.158] |
| DWL per $1 of rent at entry | | 0.013 | [-0.060, 0.079] |
| Buyout offer, 327 protected Part D brands, 7% | | $720.0 billion | $650.6 to $780.9 billion |

## Data

- **Incomes.** Census Bureau, CPS Annual Social and Economic Supplement public-use files: `mar98supp.zip`
  (income year 1997, fixed-width; household record positions from the NBER dictionary `cpsmar98.dct`) and
  `asecpub26csv.zip` (income year 2025, `hhpub26.csv`). The script reduces each to household income, persons and
  supplement weight in `data/raw/asec_households_1997.csv` and `data/raw/asec_households_2025.csv` (committed).
  Downloaded 2026-11-01.
- **Drug spending.** CMS, Medicare Part D Spending by Drug, Excel releases for data years 2016 to 2024, each
  covering five calendar years (55 MB zip, fetched into `data/raw/partd/`). Downloaded 2026-11-01.
- **Patents.** FDA Orange Book data files (`products.txt`, `patent.txt`, `exclusivity.txt`), files dated
  2026-10-09, in `data/raw/orange_book_20261101.zip` (committed). Downloaded 2026-11-01.

## Method

Rules fixed before looking at results:

- **Replication.** Valuation $`v_i = k\,y_i`$ with $`y_i`$ total household money income (negative values set to
  zero), weighted by the household supplement weight; vacant and non-interview records dropped. One price, zero
  marginal cost. Units: households (main), people with per-capita household income, and people with income divided
  by the square root of household size. 500 household bootstrap draws for the main unit. Sensitivity: marginal cost
  equal to 10% to 50% of the monopoly price it induces; optima where under 5% of buyers are served are flagged.
- **Generic entry.** Molecule-level Part D panels, one per release. Entry year $`E`$ is the release year minus two,
  so every event uses the five years of one release. Generic share of doses under 5% in $`E-2`$ and $`E-1`$, at least
  50% in $`E+1`$ and $`E+2`$; gross spending at least $10 million in $`E-1`$; at least half of the molecule's Orange
  Book listings oral tablets or capsules. Generic products are rows whose brand name and generic name share a first
  word. Each molecule's first qualifying entry is kept.
- **Controls.** Price: brand-only pills (generic share under 5% throughout) with at least $10 million in $`E-1`$.
  Doses: pills with generic share of at least 50% throughout.
- **Weights.** Price falls weighted by $`E-1`$ spending; dose changes weighted by rent, $`R_i S_i`$.
- **Buyout bill.** 2024 brand products whose molecule had no generic doses in 2024, matched by trade name to an
  NDA in the Orange Book. Protection ends at the later of the latest drug-substance patent and the latest NCE, orphan
  or pediatric exclusivity on the brand's NDAs, and the drug must list a drug-substance patent. Years left counted
  from 2026-10-09. Spending held at its 2024 level. Markup 2; discount rates 7% and 3% (OMB Circular A-4).

The estimating equations:

```math
\begin{aligned}
\Delta_i &= \ln p_{i,E_i+2} - \ln p_{i,E_i-1} \\
\widehat{\delta}_i &= \Delta_i - \frac{1}{|C_{E_i}|}\sum_{j\in C_{E_i}} \Delta_j, \qquad R_i = 1 - e^{\widehat{\delta}_i} \\
\bar{R} &= \frac{\sum_i S_i R_i}{\sum_i S_i}, \qquad
\frac{DWL}{\text{rent}} = \frac{\sum_i \tfrac{1}{2} R_i x_i S_i}{\sum_i R_i S_i}
\end{aligned}
```

with $`S_i`$ spending in $`E_i - 1`$ and $`x_i`$ the controlled proportional change in doses. Intervals come from
2,000 bootstrap draws over drugs. The competition test is OLS with HC1 standard errors:

```math
\widehat{\delta}_i = \alpha + \beta \ln N_i + \gamma_{E_i} + \varepsilon_i, \qquad H_0:\ \beta = 0
```

where $`N_i`$ counts generic makers in $`E_i + 2`$. The buyout offer for drug $`d`$ is

```math
B_d = M\,\bar{R}\,S_d\,\frac{1 - (1+r)^{-T_d}}{r}, \qquad \text{net cost} = (M-1)\,\frac{B_d}{M}
```

## Full test statistics

- **Replication, other units.** People, per capita: 2.746 (1997) and 2.827 (2025); people, size-adjusted: 2.571
  and 2.735. DWL shares 0.244, 0.269, 0.250 and 0.222. Kremer's chain $`2 \times 4/3 \times (1+d)`$ gives 3.401
  (1997) and 3.383 (2025) against his 3.33.
- **Marginal cost.** Household ratio at a cost of 30% of price: 2.813 (1997), 3.003 (2025). At 40% and 50% the
  household optimum serves 0.5% to 1.1% of households (flagged).
- **Price.** Mean fall 0.555 [0.512, 0.597], median 0.581 [0.527, 0.675], spend-weighted 0.679 [0.613, 0.736].
  Without controls the spend-weighted fall is 0.589. Pre-period ($`E-2`$ against $`E-1`$) controlled log price
  change -0.023 (s.e. 0.008).
- **Doses.** Mean -0.087 [-0.175, 0.016], median -0.157 [-0.222, -0.073], rent-weighted 0.026 [-0.119, 0.158].
  Pre-period controlled log change 0.082 (s.e. 0.034), so treated drugs were already declining relative to the
  controls. Extending each drug's own pre-period change three years forward gives a rent-weighted rise of 0.319
  [0.187, 0.438] and DWL per dollar of rent of 0.159 [0.094, 0.219].
- **Makers.** $`\hat\beta = -0.569`$ (HC1 s.e. 0.055), t = -10.42, 95% CI [-0.676, -0.462], N = 99, R² = 0.615.
  Median price falls of 26.0%, 41.2%, 67.5% and 76.4% for 1-2, 3-5, 6-9 and 10+ makers.
- **Bill.** 327 drugs, $143.5 billion of 2024 spending (of $288.7 billion in Part D), spend-weighted 4.85 years left,
  private value $360.0 billion, offer $720.0 billion at 7% and $835.5 billion at 3%. Deadweight loss recovered $4.7
  billion (main) or $57.3 billion (trend-extended). FDA lists an approved generic application for 83 of the 327. For 22 drugs (12 pediatric, 10 orphan) the end date
  is set by an exclusivity rather than the compound patent; they carry $81.3 billion of the offer.

## Reproducing the results

```bash
pip install -r requirements.txt
python src/income_ratio.py
python src/buyout_bill.py
```

The first script runs offline from the committed extracts. The second downloads the 55 MB CMS file on its first
run. Both write to `results/`.

## References

- Kremer, M. (1998). Patent buyouts: A mechanism for encouraging innovation. *QJE* 113(4), 1137-1167. NBER
  Working Paper 6304 (1997).
- Shavell, S. and van Ypersele, T. (2001). Rewards versus intellectual property rights. *Journal of Law and
  Economics* 44(2), 525-547.
- Office of Management and Budget (2003). Circular A-4, Regulatory Analysis.
