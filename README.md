# Income Classification Projections

Underlying data for "The Great Income Inversion", published on
[Moving Frontiers](https://movingfrontiers.substack.com).

World Bank income classifications and GNI per capita, actual 1987 to 2025,
projected 2026 to 2050.

## Files

`income-classification-through-2050.xlsx` is the full workbook. Seven sheets,
with every projected figure driven by formulas off a single Assumptions sheet.
Change an assumption cell and everything downstream recomputes.

The `csv/` folder holds the same content as flat text.

| File | Contents |
|---|---|
| `panel-long.csv` | Tidy long format, one row per economy-year, 13,612 rows |
| `classification.csv` | Income group by economy and year, wide |
| `gni-per-capita.csv` | GNI per capita, Atlas method, current US$, wide |
| `growth-calculation.csv` | The ten annual rates per economy, the median, the rate used |
| `thresholds.csv` | Official thresholds 1987 to 2025, then projected |
| `assumptions.csv` | The six assumptions and the derivation of the drift and caps |
| `coverage.csv` | Economy counts at each step, and where the others drop out |
| `readme.txt` | Full methodology note from the workbook |

Start with `panel-long.csv` for analysis. It carries a `series` column marking
actual against projected, which replaces the yellow shading used in the workbook.

## Coverage

The OGHIST worksheet lists 226 rows and 224 parse into the workbook. Six left
the classification before 2025 and are not projected. That leaves 218 economies
classified in 2025, of which 197 are projected forward and 21 are held at their
2025 class. The 197 carry 97.8 percent of the 2050 population total.

## Method in brief

Each economy starts from its latest reported GNI per capita and grows at the
median of its ten annual rates over the decade to 2025. A floor of 1.244 percent
equal to the threshold drift means no economy is downgraded anywhere in the
projection. A cap at the 90th percentile of decade-median growth within each
income group means no economy outgrows the top decile of its own group. The
floor and the cap together set 58 of the 197 rates. Full detail sits in
`readme.txt` and on the Assumptions sheet.

## Sources

World Bank OGHIST, 1 July 2026, Thresholds and Country Analytical History
worksheets. WDI GNI per capita, Atlas method, July 2026 vintage.

## Licence

CC BY 4.0. Free to share and adapt with attribution to Philip Schellekens,
Moving Frontiers. Source data are World Bank OGHIST and WDI, subject to the
World Bank's own terms of use.

## Use

Free to use with attribution to Philip Schellekens, Moving Frontiers.
