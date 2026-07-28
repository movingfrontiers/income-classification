# Income classification through 2050

Data behind **The Moving Escalator**, an opening series on [Moving Frontiers](https://movingfrontiers.substack.com) about four decades of movement through the World Bank's country income classification, where the world is heading by 2050, and whether the classification itself remains fit for purpose.

The repository holds the full panel of 218 economies, actual from 1987 and projected to 2050, together with the thresholds, the growth rates, the population weights and every assumption behind them.

## Contents

```
income-classification-2050.xlsx     the workbook, eight sheets, formula-driven
csv/
   panel-long.csv                   tidy long format, one row per economy-year-series
   classification.csv               income group by economy and year, 1987-2050
   gni-per-capita.csv               GNI per capita by economy and year, 1987-2050
   population.csv                   population by economy and year, 1990-2050
   growth-calculation.csv           the ten annual rates, median, floor, cap, rate used
   thresholds.csv                   official and projected thresholds, 1987-2050
   assumptions.csv                  the six assumptions as they appear in the workbook
   coverage.csv                     how many economies the projection covers
   readme.txt                       the workbook's own notes
```

Start with **`panel-long.csv`** if you work in pandas or R. One `read_csv` and you can plot without reshaping anything: columns are `economy`, `code`, `year`, `series`, `value`, `status`, where `series` is one of `class`, `gni_pc` or `population_millions` and `status` distinguishes actual from projected.

The wide files carry the same information in the layout of the workbook sheets, with a `Status` column instead. Growth rates are at full precision rather than the rounding shown in the sheet, so `0.015808597462` where the workbook displays 1.6 percent.

## The projection in six assumptions

Every projected figure derives from these. They live in labelled cells on the workbook's Assumptions sheet, so changing one re-computes everything downstream.

1. **Starting level.** Each economy starts from its latest reported GNI per capita, Atlas method, used exactly as published. No value is adjusted to fit the band implied by its 2025 class.

2. **Growth rate.** The median of the ten annual growth rates over the decade to 2025. A median rather than a compound rate, so that a single devaluation year cannot set a twenty-five year path.

3. **Threshold drift.** One common rate of 1.244 percent a year for all three thresholds, the median annual increase over the same decade. The Bank indexes all three to the SDR deflator, and since 1990 the ratios between them have held at 3.96 and 3.09.

4. **Floor of 1.244 percent**, equal to the drift, so no economy is downgraded anywhere in the projection. It binds for 37 economies.

5. **Cap at the 90th percentile** of decade-median growth within each income group: 5.6 percent low income, 7.5 lower-middle, 9.1 upper-middle, 7.2 high income. It binds for 21 economies.

6. **Freeze.** An economy with fewer than 8 of the 10 annual observations is held at its 2025 class. This applies to 21 economies, of which six are not high income: Cuba, Eritrea, Korea Dem. Rep., South Sudan, Syria and Yemen.

Together the floor and the cap set 58 of the 197 projected growth rates, covering 21.7 percent of the classified population. About three-quarters of humanity is projected on its own observed growth rate.

## Coverage

The World Bank's historical dataset lists 226 rows, of which 224 parse as economies, every one classified in at least one year since 1987. Six left the classification before 2025 and cannot be projected: the USSR, Yugoslavia, Czechoslovakia, Serbia and Montenegro, the Netherlands Antilles and Mayotte. That leaves **218 economies** classified in 2025, of which 197 are projected forward and 21 held at their 2025 class. The 197 carry 98.2 percent of the classified population, and the classified set covers more than 99 percent of world population throughout.

## Sources

| | |
|---|---|
| Classifications and thresholds | World Bank OGHIST, 1 July 2026, Country Analytical History and Thresholds worksheets |
| GNI per capita, Atlas method | World Bank World Development Indicators, July 2026 release |
| Population to 2025 | World Bank World Development Indicators, `SP.POP.TOTL` |
| Population from 2026 | UN World Population Prospects, 2024 revision, medium variant, rebased to each economy's 2025 level |

Thresholds for 1987 to 2025 are the official values exactly as published, with no smoothing. Population weights drive the population shares and levels charts and play no part in the classification projection itself.

## Licence

The contents of this repository are licensed under a Creative Commons Attribution 4.0 International Licence, see [`LICENSE`](LICENSE). Attribution to Philip Schellekens, Moving Frontiers.

Suggested citation:

> Schellekens, Philip (2026). World Bank income classification projections to 2050. Moving Frontiers. https://movingfrontiers.substack.com

Source data carry the terms of use of the World Bank and the United Nations respectively. The projections and the assumptions behind them are the author's own.

Philip Schellekens writes in a personal capacity. Views expressed are his own and do not represent UNDP, the United Nations, or any other institution with which he is or has been affiliated.
