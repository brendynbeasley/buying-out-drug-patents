# Methods review: Kremer (1998)

- **Paper.** Michael Kremer, "Patent Buyouts: A Mechanism for Encouraging Innovation," *Quarterly Journal of
  Economics* 113(4), 1998, pp. 1137-1167. Working paper version: NBER Working Paper 6304, December 1997.
- **Statistical focus.** The claim that the social value of new pharmaceuticals is 2.6 times the profit of a
  single-price monopolist, with deadweight loss equal to one quarter of profits plus consumer surplus, and the
  markup of "perhaps two" that the paper derives from it and from the literature on returns to R&D.
- **Review standard.** Internal consistency of the formal results, explicit statement of assumptions, the
  testability of predictions, and, for the one numerical calculation, current expectations for reporting data
  sources, sample construction and uncertainty (as in the AEA Data and Code Availability Policy).
- **What was read.** The full text of NBER Working Paper 6304 (62 scanned pages, including figures and
  bibliography), from nber.org, and the published abstract on the RePEc/IDEAS page for the QJE article. The
  published QJE text was not read; page references below are to the working paper, and statements about the
  published version are limited to its abstract.

## Research design

A theory and mechanism-design paper. It reviews historical inventor rewards (prizes, the 1839 French purchase of the
Daguerreotype process, state purchases of Eli Whitney's cotton gin rights), proposes an auction-based buyout with a
fixed markup and random resale with probability $`p`$, and analyzes its properties in stylized models: a
common-value auction with an informed inventor (Section III.A, equation 1), a private-value auction with cost
differences under constant-elasticity demand (III.B, equations 2 to 6), development incentives (IV), buyouts as a
research subsidy in steady state (V.A, equations 7 and 8), substitute patents with joint randomization (V.B, game
trees in Figures 2 to 4), durable goods (V.C), complementary patents (V.D) and collusion (VI). There is no empirical design in the econometric sense.

## Sampling strategy

Does not apply to the formal analysis. The one quantitative calculation (p. 8) uses "data on the U.S. income
distribution," but the paper does not name the survey, year, unit (households, families or people), income concept
or treatment of top-coding. The calculation is credited to Atif Mian and described as available from the author.

## Sample size

Not reported for the income calculation. The supporting evidence on social and private returns is cited from other
studies (Mansfield's 17 innovations, Nadiri's survey, Trajtenberg's CT scanner study) with their own samples.

## Inclusion and exclusion criteria

Not stated for the income calculation. For the policy proposal the paper argues for restricting buyouts to
pharmaceuticals, and within them to drugs that are easy to manufacture and have many potential producers (p. 40),
which is a design recommendation rather than a sample rule.

## Independent and dependent variables

In the income calculation the input is the income distribution and the outputs are the monopoly price, the share
of social value captured as profit and the deadweight loss share. In the mechanism analysis the choice variables
are the markup $`M`$, the resale probability $`p`$ and the bid rule (for example a multiple of the third-highest
bid, p. 18), and the outcomes are whether inventors sell, bidding behavior and research incentives.

## Statistical methods

None in the inferential sense. The income calculation is a deterministic computation under the assumption that
willingness to pay is proportional to income and that the monopolist cannot price discriminate. Marginal cost is
not mentioned and appears to be zero. Formal results are derived analytically.

## Reported effect sizes

The paper's numbers are calibrations and cited magnitudes, listed in the table below. The working paper abstract
gives the markup as "perhaps two"; the published abstract describes a markup "equal to the typical ratio of
inventions' social and private value" without a number.

## Confidence intervals

None reported. The 2.6 and the one-quarter figures are point values with no sensitivity analysis to the income
data, the unit of analysis or marginal cost.

## p-values, if applicable

Not applicable; no hypothesis tests are performed.

## Missing data treatment

Not applicable to the formal results and not described for the income calculation.

## Stated limitations

The paper is candid about them. It calls the income-proportional assumption "crude" (p. 8) and notes that some
deadweight loss is recovered through price discrimination. It states that the auction need not be the best
mechanism (p. 16), that buyouts are vulnerable to collusion between patent holders and bidders (Section VI), that
durable goods weaken the incentive argument (V.C), and that "based on theory alone, it is impossible to know"
whether buyouts would be a useful supplement, recommending a limited trial (p. 46).

## Methods summary

The paper's empirical content is light by design. Its formal results are internally consistent within their
stated models; for example, equation (1) correctly implies that with a markup of two and a uniform prior, bidders
bid $`(L+U)/2`$ and every patent sells, and the complementary-patents argument correctly gives the selling condition
$`2 - p < M`$ (p. 36). The quantitative case for a markup near two rests on two legs: cited estimates that social
returns to R&D are roughly twice private returns, and the income-distribution calculation. Only the second is
computed in the paper, and it is reported without data documentation, code or uncertainty.

## Statistics extraction table

| Statistic | Value and unit | Source location | What it measures | What it does not establish |
|---|---|---|---|---|
| Social value of new drugs ÷ monopoly profit | 2.6 (ratio) | WP p. 8, footnote 6 | Share of total willingness to pay a single-price seller captures if valuations are proportional to US income | That real drug demand is income-proportional; any effect of insurance, price discrimination or production cost |
| Deadweight loss ÷ (profit + consumer surplus) | 0.25 (ratio) | WP p. 8 | Value lost from buyers priced out under the same assumption | The size of deadweight loss in actual insured drug markets |
| Social ÷ private return to R&D, at monopoly quantities | "at least twice" | WP p. 10, citing Nadiri (1993), Mansfield et al. (1977), Trajtenberg (1990) | Literature-based ratio of social to private rates of return | A precise markup; the cited studies use different methods and samples |
| Share of research that is duplicative | one quarter (guess) | WP p. 10, based on Mansfield (1984, 1985) | Assumed fraction of R&D spent imitating existing products | An estimated quantity; the paper calls it a guess |
| Chained social ÷ private return | 2 × 4/3 × 5/4 = 3.33 | WP p. 10 | Combined calibration of spillovers, duplication and deadweight loss | Independence of the three factors; the 5/4 factor reuses the income calculation |
| Recommended markup | 2 ("perhaps two", "at least twice") | WP abstract; p. 17 | Conservative policy choice below the 3.33 calibration | Optimality; p. 28 argues the optimal markup is larger than the static ratio |
| Plausible optimal markup with collusion | 3, reduced to 2 if collusion raises bids 50% | WP p. 44 | Illustrative adjustment | An estimate of collusion |
| Equilibrium bid with informed inventor | $`\min((L+U)/2,\ \max[0, L/(2-M)])`$ | WP eq. (1), p. 20 | Bid under uniform common-value prior | Behavior under skewed or unknown priors |
| Daguerreotype buyout | Pension of 6,000 francs a year to Daguerre, 4,000 to his partner | WP p. 12, citing Barger and White (1991), Nelson (1996) | Historical buyout price | The private or social value of the process |
| Whitney sale to South Carolina | $50,000, 1802 | WP p. 13, citing Green (1956), Olmstead (1972) | Historical buyout price | That the price reflected value |
| Suggested trial appropriation | $100 million over two years | WP p. 47 | Scale of a proposed pilot | Its adequacy for any particular drug |

## Interpretation notes

- The 2.6 and one-quarter figures are best read as an illustration of how much value a single price leaves on the
  table when buyers are unequal, not as an estimate of drug-market welfare. They depend only on the shape of the
  income distribution, because the proportionality constant cancels.
- The 3.33 chain multiplies factors drawn from different sources and partly overlapping concepts. The social return
  figures from the R&D literature already include some consumer surplus, so adding a separate deadweight-loss factor
  may double count; the paper does not discuss this.
- The paper's argument that the optimal markup exceeds the static social-to-private ratio (Section V.A) is a
  qualitative result about steady-state research, not a number.
- A modern rerun in this repository recomputes the income calculation on Census household microdata and obtains
  2.66 and 0.275 for income year 1997. That agreement supports the arithmetic under the stated assumption; it is a
  recomputation from public data, not a reproduction of the original calculation, whose inputs are unknown.

## Unanswered questions

- Which income data, year and unit were used for the 2.6 figure, and how were top-coded incomes handled?
- Was marginal cost set to zero, and how sensitive is the ratio to positive production costs?
- How would the deadweight-loss share change in markets where insurance, not the patient, pays most of the price?
- What resale probability $`p`$ would be needed to keep bids informative while keeping most patents public?
- How large would administrative and bidding costs be relative to the value of a typical pharmaceutical patent?

## Items requiring expert verification

- Whether the published QJE version changes any numbers from the working paper, since only its abstract was read.
- The historical details of the Daguerreotype and Whitney cases, which the paper takes from secondary sources.
- The legal feasibility of voluntary buyouts with random resale under current US patent and procurement law.
- Whether the literature estimates of social returns cited on pp. 9-10 support a factor of two for pharmaceuticals
  specifically.
