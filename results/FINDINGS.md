# Kremer (1998) on modern data: findings

## In plain English

- **Kremer's arithmetic checks out.** If people would pay for a new drug in proportion to their income, a seller
  charging one price captures only about 1/2.66 of the drug's value with 1997 incomes, matching the 2.6 in the
  paper. With 2025 incomes the figure is 1/2.83, because incomes are more unequal.
- **Generic entry does what a buyout would do to prices.** When Lyrica (Upjohn), Crestor (AstraZeneca), Abilify
  (Otsuka) and Cymbalta (Eli Lilly) went generic, Medicare's price per dose fell by 76% to 90% within two years, net of
  brand price trends. Across 99 pills the spending-weighted fall is 67.9%, and it is larger when more firms enter.
- **In Medicare, use barely rises when the price falls.** Doses rise about 3% after entry on the main comparison, so
  the deadweight loss a buyout would remove is about 1 cent per dollar of monopoly profit, against the 57 to 60 cents
  Kremer's income calculation implies. Insurance is the likeliest reason, though the data cannot show it.
- **Buying out the patents would be expensive.** At Kremer's markup of two, the 327 brand drugs still protected in
  Part D (Eliquis, Ozempic, Jardiance, Mounjaro and the rest) would cost about $720 billion, against $143.5 billion
  of Part D spending on them in 2024. Kremer's suggested $100 million trial fund buys 1.3 days of Eliquis.

A friendlier tour is in the [README](../README.md). Methods and test statistics are in
[TECHNICAL.md](../TECHNICAL.md).

**Key to the labels.** *ratio_sv_profit* = social value divided by monopoly profit. *dwl_share* = deadweight loss
divided by (profit + consumer surplus). *dwl_per_profit* = deadweight loss per dollar of profit. *profit_share_sv* =
profit as a share of social value. *price_over_mean* = the monopoly price as a multiple of the average valuation. *mc_share_of_price* = marginal cost
as a share of the monopoly price.
*tail_solution* = the optimal price serves under 5% of buyers. *protection_set_by* = the Orange Book listing that sets the end of protection (compound patent, PED pediatric or ODE orphan exclusivity). *R* = share of the brand's price per dose that
disappears two years after generic entry, net of brand-only drugs. *x* = proportional change in doses over the same
span, net of long-generic drugs. *x_trend* = *x* after extending each drug's own pre-entry trend. *E* = first year of
generic sales. All dollar figures are gross Part D spending (before manufacturer rebates).

## 1. Replication: income-proportional willingness to pay (`income_ratio.csv`)

Main specification with bootstrap intervals (500 household draws) and Kremer's chain, $`2 \times 4/3 \times (1 + d)`$:

| year | ratio_sv_profit | ratio_ci_low | ratio_ci_high | ratio_se | dwl_share | dwl_share_ci_low | dwl_share_ci_high | dwl_share_se | kremer_chain |
|---|---|---|---|---|---|---|---|---|---|
| 1997 | 2.656 | 2.628 | 2.682 | 0.013 | 0.275 | 0.269 | 0.282 | 0.005 | 3.401 |
| 2025 | 2.831 | 2.797 | 2.859 | 0.016 | 0.269 | 0.262 | 0.275 | 0.003 | 3.383 |

Worked example with each household valuing the drug at 1% of income, dollars per household in the country
(`worked_example.csv`):

| year | mean_value | price | share_buying | profit | cs | dwl | social_value | households_millions | k |
|---|---|---|---|---|---|---|---|---|---|
| 1997 | $496.88 | $399.98 | 46.8% | $187.10 | $202.54 | $107.24 | $496.88 | 102.58 | 0.01 |
| 2025 | $1,266.66 | $999.96 | 44.7% | $447.36 | $550.96 | $268.34 | $1,266.66 | 137.12 | 0.01 |

Every unit and marginal cost:

| year | unit | mc_share_of_price | price_over_mean | share_buying | ratio_sv_profit | dwl_share | dwl_per_profit | profit_share_sv | tail_solution |
|---|---|---|---|---|---|---|---|---|---|
| 1997 | household | 0.00 | 0.80 | 46.8% | 2.656 | 0.275 | 0.573 | 0.377 | False |
| 1997 | household | 0.10 | 0.91 | 41.3% | 2.709 | 0.302 | 0.628 | 0.369 | False |
| 1997 | household | 0.20 | 1.01 | 36.5% | 2.752 | 0.307 | 0.646 | 0.363 | False |
| 1997 | household | 0.30 | 1.01 | 36.5% | 2.813 | 0.243 | 0.549 | 0.355 | False |
| 1997 | household | 0.40 | 6.64 | 1.1% | 1.945 | 0.530 | 0.674 | 0.514 | True |
| 1997 | household | 0.50 | 6.64 | 1.1% | 1.698 | 0.281 | 0.372 | 0.589 | True |
| 1997 | person_per_capita | 0.00 | 0.73 | 50.2% | 2.746 | 0.244 | 0.539 | 0.364 | False |
| 1997 | person_per_capita | 0.10 | 0.78 | 46.7% | 2.824 | 0.246 | 0.557 | 0.354 | False |
| 1997 | person_per_capita | 0.20 | 0.91 | 38.9% | 2.927 | 0.287 | 0.653 | 0.342 | False |
| 1997 | person_per_capita | 0.30 | 1.04 | 32.6% | 3.013 | 0.296 | 0.688 | 0.332 | False |
| 1997 | person_per_capita | 0.40 | 1.30 | 22.9% | 3.132 | 0.326 | 0.771 | 0.319 | False |
| 1997 | person_per_capita | 0.50 | 4.28 | 1.8% | 3.171 | 0.559 | 1.137 | 0.315 | True |
| 1997 | person_equivalized | 0.00 | 0.75 | 51.7% | 2.571 | 0.250 | 0.514 | 0.389 | False |
| 1997 | person_equivalized | 0.10 | 0.81 | 47.5% | 2.643 | 0.263 | 0.551 | 0.378 | False |
| 1997 | person_equivalized | 0.20 | 0.90 | 41.9% | 2.719 | 0.282 | 0.598 | 0.368 | False |
| 1997 | person_equivalized | 0.30 | 0.94 | 39.8% | 2.800 | 0.249 | 0.559 | 0.357 | False |
| 1997 | person_equivalized | 0.40 | 1.09 | 31.9% | 2.942 | 0.270 | 0.625 | 0.340 | False |
| 1997 | person_equivalized | 0.50 | 1.40 | 19.9% | 3.161 | 0.315 | 0.758 | 0.316 | False |
| 2025 | household | 0.00 | 0.79 | 44.7% | 2.831 | 0.269 | 0.600 | 0.353 | False |
| 2025 | household | 0.10 | 0.95 | 36.7% | 2.902 | 0.327 | 0.715 | 0.345 | False |
| 2025 | household | 0.20 | 1.11 | 30.4% | 2.954 | 0.351 | 0.768 | 0.339 | False |
| 2025 | household | 0.30 | 1.18 | 27.6% | 3.003 | 0.310 | 0.710 | 0.333 | False |
| 2025 | household | 0.40 | 8.68 | 0.5% | 2.645 | 0.855 | 1.219 | 0.378 | True |
| 2025 | household | 0.50 | 8.68 | 0.5% | 2.256 | 0.494 | 0.746 | 0.443 | True |
| 2025 | person_per_capita | 0.00 | 0.76 | 46.6% | 2.827 | 0.269 | 0.599 | 0.354 | False |
| 2025 | person_per_capita | 0.10 | 0.85 | 41.1% | 2.899 | 0.292 | 0.656 | 0.345 | False |
| 2025 | person_per_capita | 0.20 | 0.95 | 36.6% | 2.955 | 0.292 | 0.667 | 0.338 | False |
| 2025 | person_per_capita | 0.30 | 1.14 | 28.3% | 3.060 | 0.323 | 0.748 | 0.327 | False |
| 2025 | person_per_capita | 0.40 | 1.33 | 22.5% | 3.105 | 0.303 | 0.722 | 0.322 | False |
| 2025 | person_per_capita | 0.50 | 1.69 | 14.6% | 3.220 | 0.296 | 0.735 | 0.311 | False |
| 2025 | person_equivalized | 0.00 | 0.70 | 52.3% | 2.735 | 0.222 | 0.497 | 0.366 | False |
| 2025 | person_equivalized | 0.10 | 0.81 | 45.2% | 2.806 | 0.264 | 0.587 | 0.356 | False |
| 2025 | person_equivalized | 0.20 | 0.99 | 35.3% | 2.902 | 0.335 | 0.728 | 0.345 | False |
| 2025 | person_equivalized | 0.30 | 1.04 | 32.9% | 2.966 | 0.294 | 0.674 | 0.337 | False |
| 2025 | person_equivalized | 0.40 | 1.16 | 28.0% | 3.050 | 0.270 | 0.649 | 0.328 | False |
| 2025 | person_equivalized | 0.50 | 1.63 | 15.1% | 3.227 | 0.323 | 0.788 | 0.310 | False |

## 2. Generic entry in Medicare Part D, 2014-2022 (`entry_summary.csv`)

Bootstrap over the 99 drugs (2,000 draws). Pre-trend rows give the controlled change from $`E-2`$ to $`E-1`$ in logs,
with a conventional standard error.

| statistic | estimate | ci_low | ci_high | se_boot |
|---|---|---|---|---|
| R_mean | 0.5553 | 0.5117 | 0.5972 | 0.0227 |
| R_median | 0.5811 | 0.5271 | 0.6746 | 0.0387 |
| R_spend_weighted | 0.6787 | 0.6132 | 0.7361 | 0.0315 |
| x_mean | -0.0873 | -0.1754 | 0.0163 | 0.0492 |
| x_median | -0.1570 | -0.2222 | -0.0732 | 0.0401 |
| x_rent_weighted | 0.0259 | -0.1193 | 0.1577 | 0.0707 |
| dwl_per_rent | 0.0130 | -0.0597 | 0.0788 | 0.0353 |
| dwl_per_spend | 0.0088 | -0.0367 | 0.0563 | 0.0241 |
| x_trend_median | 0.2107 | 0.1129 | 0.2857 | 0.0470 |
| x_trend_rent_weighted | 0.3185 | 0.1869 | 0.4377 | 0.0644 |
| dwl_per_rent_trend | 0.1593 | 0.0935 | 0.2189 | 0.0322 |
| pretrend_did_lnp_mean | -0.0226 |  |  | 0.0081 |
| pretrend_did_lnq_mean | 0.0816 |  |  | 0.0343 |
| raw_R_spend_weighted | 0.5890 |  |  |  |
| n_events | 99.0000 |  |  |  |
| spend_pre_total | 42,065,219,651.4100 |  |  |  |

Path relative to the year before entry, mean controlled log change (`entry_path.csv`):

| k | var | mean | ci_low | ci_high | n |
|---|---|---|---|---|---|
| -2 | did_lnp | -0.023 | -0.041 | -0.008 | 99 |
| -1 | did_lnp | 0.000 | 0.000 | 0.000 | 99 |
| 0 | did_lnp | -0.070 | -0.098 | -0.042 | 99 |
| 1 | did_lnp | -0.542 | -0.625 | -0.470 | 99 |
| 2 | did_lnp | -0.951 | -1.060 | -0.846 | 99 |
| -2 | did_lnq | 0.082 | 0.011 | 0.140 | 99 |
| -1 | did_lnq | 0.000 | 0.000 | 0.000 | 99 |
| 0 | did_lnq | -0.137 | -0.179 | -0.097 | 99 |
| 1 | did_lnq | -0.196 | -0.261 | -0.136 | 99 |
| 2 | did_lnq | -0.200 | -0.290 | -0.109 | 99 |

By number of generic makers in $`E+2`$ (`entry_by_makers.csv`):

| makers_bin | n | R_median | R_mean | x_median | spend_pre |
|---|---|---|---|---|---|
| 1-2 | 15 | 26.0% | 23.7% | -34.1% | $1.8B |
| 3-5 | 23 | 41.2% | 45.3% | -22.4% | $3.4B |
| 6-9 | 33 | 67.5% | 62.3% | -13.6% | $9.6B |
| 10+ | 28 | 76.4% | 72.9% | -5.5% | $27.2B |

Controlled log price change on log generic makers with entry-year effects, HC1 errors (`makers_regression.csv`):

| term | coef | se_hc1 | t | p | ci_low | ci_high | n | r2 |
|---|---|---|---|---|---|---|---|---|
| ln_makers | -0.569 | 0.055 | -10.417 | 2.1e-25 | -0.676 | -0.462 | 99 | 0.615 |

The 25 largest entries by pre-entry spending (`entry_events.csv` has all 99):

| brand | mol | E | spend_pre | price_pre | price_post | R | x | x_trend | generic_makers |
|---|---|---|---|---|---|---|---|---|---|
| Lyrica | pregabalin | 2019 | $3.0B | $7.54 | $0.84 | 90.5% | 20.9% | 31.8% | 21 |
| Crestor | rosuvastatin calcium | 2016 | $2.9B | $6.92 | $0.87 | 90.4% | 62.4% | 80.8% | 22 |
| Nexium | esomeprazole magnesium | 2015 | $2.7B | $7.81 | $4.45 | 58.2% | -33.1% | 2.5% | 6 |
| Abilify | aripiprazole | 2015 | $2.6B | $30.04 | $9.65 | 76.4% | 8.2% | 30.4% | 14 |
| Cymbalta | duloxetine hcl | 2014 | $2.0B | $6.96 | $1.21 | 87.6% | 40.4% | 60.8% | 16 |
| Namenda | memantine hcl | 2015 | $1.9B | $5.85 | $3.54 | 55.5% | -4.1% | 62.7% | 20 |
| Renvela | sevelamer carbonate | 2017 | $1.5B | $5.78 | $2.80 | 61.0% | -11.3% | 4.9% | 11 |
| Sensipar | cinacalcet hcl | 2018 | $1.4B | $40.36 | $22.28 | 54.3% | -74.9% | -72.1% | 13 |
| Latuda | lurasidone hcl | 2022 | $1.4B | $49.92 | $7.38 | 86.7% | 2.3% | 24.9% | 15 |
| Gleevec | imatinib mesylate | 2016 | $1.2B | $213.33 | $143.81 | 48.4% | -6.9% | -10.6% | 11 |
| Zetia | ezetimibe | 2016 | $1.2B | $7.43 | $2.08 | 78.6% | 21.6% | 39.7% | 13 |
| Diovan | valsartan | 2014 | $1.2B | $4.22 | $0.97 | 83.6% | -12.1% | 57.3% | 13 |
| Celebrex | celecoxib | 2014 | $0.9B | $5.25 | $2.14 | 71.0% | -22.2% | 8.9% | 11 |
| Zytiga | abiraterone acetate | 2018 | $0.9B | $81.52 | $43.32 | 56.0% | 62.6% | 100.0% | 16 |
| Vimpat* | lacosamide | 2022 | $0.8B | $10.78 | $1.69 | 85.9% | 32.0% | 24.8% | 24 |
| Vesicare | solifenacin succinate | 2019 | $0.7B | $11.83 | $1.70 | 87.8% | -10.6% | 59.2% | 14 |
| Dexilant | dexlansoprazole | 2022 | $0.7B | $10.60 | $5.47 | 53.6% | -30.3% | -10.5% | 4 |
| Esbriet | pirfenidone | 2022 | $0.7B | $52.76 | $15.95 | 72.8% | -21.2% | 11.3% | 9 |
| Letairis | ambrisentan | 2019 | $0.6B | $319.00 | $182.76 | 51.3% | 8.1% | 59.9% | 6 |
| Ranexa | ranolazine | 2018 | $0.6B | $6.63 | $1.88 | 76.5% | 20.6% | 29.8% | 10 |
| Exelon | rivastigmine | 2015 | $0.5B | $11.75 | $12.91 | 19.3% | -41.5% | -24.2% | 2 |
| Evista | raloxifene hcl | 2014 | $0.5B | $5.77 | $3.29 | 59.5% | -41.9% | -5.3% | 6 |
| Bystolic | nebivolol hcl | 2021 | $0.5B | $5.02 | $1.45 | 76.0% | -4.2% | 15.2% | 9 |
| Afinitor | everolimus | 2020 | $0.5B | $266.51 | $158.80 | 48.9% | 14.3% | 7.0% | 6 |
| Lovaza | omega-3 acid ethyl esters | 2014 | $0.5B | $1.68 | $1.26 | 46.4% | -30.2% | -8.5% | 4 |

## 3. The buyout bill (`buyout_named.csv`, `buyout_totals.csv`)

The 15 protected brands with the most 2024 Part D spending. Private value = 67.9% of 2024 spending, held flat and
discounted to the end of protection. Offer = 2 x private value. *trial_fund_days* = days of rent that Kremer's
$100 million trial budget would buy at the markup.

| brand | spend | spend_per_dose | compound_patent | protection_end | years_left | generic_approved | rent_per_year | private_value_7pct | buyout_offer_7pct | buyout_offer_3pct | dwl_recovered_7pct | trial_fund_days |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Eliquis | $20.8B | $9.63 | 2026-11-21 | 2028-10-17 | 2.02 | True | $14.1B | $25.8B | $51.5B | $54.6B | $0.33B | 1.3 |
| Ozempic | $13.0B | $306.45 | 2034-05-02 | 2034-05-02 | 7.56 | False | $8.8B | $50.4B | $100.7B | $117.5B | $0.65B | 2.1 |
| Jardiance | $11.4B | $18.93 | 2028-08-01 | 2028-08-01 | 1.81 | True | $7.8B | $12.8B | $25.6B | $27.0B | $0.17B | 2.4 |
| Mounjaro | $6.3B | $511.65 | 2039-06-14 | 2039-06-14 | 12.68 | False | $4.3B | $35.4B | $70.8B | $89.6B | $0.46B | 4.2 |
| Trelegy Ellipta | $5.3B | $10.52 | 2027-12-18 | 2027-12-18 | 1.19 | False | $3.6B | $4.0B | $7.9B | $8.3B | $0.05B | 5.1 |
| Entresto | $4.0B | $11.04 | 2027-05-27 | 2027-05-27 | 0.63 | True | $2.7B | $1.6B | $3.3B | $3.4B | $0.02B | 6.7 |
| Januvia | $3.8B | $17.96 | 2026-11-24 | 2026-11-24 | 0.13 | True | $2.6B | $0.3B | $0.6B | $0.6B | $0.00B | 7.1 |
| Biktarvy | $3.5B | $131.33 | 2035-06-19 | 2035-06-19 | 8.69 | False | $2.3B | $14.9B | $29.8B | $35.4B | $0.19B | 7.8 |
| Xtandi | $3.4B | $136.49 | 2027-08-13 | 2027-08-13 | 0.84 | True | $2.3B | $1.8B | $3.7B | $3.8B | $0.02B | 7.9 |
| Vyndamax | $2.8B | $743.93 | 2035-08-31 | 2035-08-31 | 8.89 | False | $1.9B | $12.4B | $24.8B | $29.6B | $0.16B | 9.5 |
| Imbruvica | $2.3B | $411.94 | 2033-10-30 | 2033-10-30 | 7.06 | True | $1.5B | $8.3B | $16.7B | $19.3B | $0.11B | 11.9 |
| Pomalyst | $2.2B | $1,094.76 | 2031-06-21 | 2031-06-21 | 4.70 | True | $1.5B | $5.7B | $11.4B | $12.6B | $0.07B | 12.5 |
| Ofev | $2.1B | $216.45 | 2025-10-01 | 2027-03-06 | 0.41 | True | $1.4B | $0.5B | $1.1B | $1.1B | $0.01B | 12.9 |
| Jakafi | $2.1B | $283.64 | 2028-06-12 | 2029-03-22 | 2.45 | False | $1.4B | $3.1B | $6.2B | $6.6B | $0.04B | 12.9 |
| Ibrance | $2.0B | $744.25 | 2034-02-08 | 2034-02-08 | 7.33 | True | $1.4B | $7.7B | $15.4B | $17.9B | $0.10B | 13.2 |

Totals:

| | Top 15 | All 327 protected brands |
|---|---|---|
| Part D spending, 2024 | $84.9B | $143.5B |
| Rent per year (67.9% of spending) | $57.7B | $97.4B |
| Private value, 7% | $184.7B | $360.0B |
| Buyout offer, 7% | $369.5B | $720.0B |
| Buyout offer, 7%, rent share at 95% bounds | $333.8B to $400.7B | $650.6B to $780.9B |
| Buyout offer, 3% | $427.4B | $835.5B |
| Net cost after rent no longer paid, 7% | $184.7B | $360.0B |
| Deadweight loss recovered, 7%, main | $2.4B | $4.7B |
| Deadweight loss recovered, 7%, trend-extended | $29.4B | $57.3B |
| Spending-weighted years of protection left | 4.19 | 4.85 |
| Drugs with an FDA-approved generic application | 9 | 83 |
| Drugs whose end date is set by an exclusivity, not the compound patent | 3 | 22 |
| Buyout offer for those drugs, 7% | $58.8B | $81.3B |
| All Part D gross spending, 2024 | $288.7B | $288.7B |

`buyout_all_protected.csv` lists all 327 drugs.

## Figures

- `profit_curve.png`: profit at each price as a share of social value, 1997 and 2025 household incomes.
- `entry_path.png`: controlled price per dose and doses around generic entry.
- `buyout_named.png`: 2024 Part D spending and the buyout offer for the 15 largest protected brands.
