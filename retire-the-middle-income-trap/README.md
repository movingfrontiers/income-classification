# Retire the Middle-Income Trap

Data behind **Retire the Middle-Income Trap**, Post 3 of [The Moving Escalator](https://movingfrontiers.substack.com), a series on four decades of movement through the World Bank's country income classification, where the world is heading by 2050, and whether the classification itself remains fit for purpose.

The post argues that the middle-income trap is conceptually flawed and empirically unsupported. The repository holds the data behind each of its twelve charts, together with the projection workbook that generates every figure from 2026 onward.

## Contents

```
income-classification-2050.xlsx     the workbook, eight sheets, formula-driven
csv/
   chart-1-completed-runs-from-LMIC-to-UMIC.csv
   chart-2-ongoing-runs-from-LMIC-to-UMIC.csv
   chart-3-completed-runs-from-UMIC-to-HIC.csv
   chart-4-ongoing-runs-from-UMIC-to-HIC.csv
   chart-5-growth-in-middle-income-economies-decade-by-decade.csv
   chart-6-the-world-has-reached-peak-middle-income.csv
   chart-7-where-people-live-by-country-income-group.csv
   chart-8-the-middle-of-the-classification-is-emptying-out.csv
   chart-9-how-many-economies-sit-in-each-income-group.csv
   chart-10-how-country-income-groups-fill-up.csv
   chart-11-how-population-growth-and-reclassification-affect-income-group-size.csv
   chart-12-the-high-income-line-is-not-a-finish-line.csv
```

Each file carries exactly what its chart plots, one file per chart, in the order the charts appear in the post. Files 6 to 9 open with commented metadata lines, so read them with `comment='#'` in pandas or `comment.char='#'` in R.

## The charts, file by file

**Charts 1 to 4. Transit runs through the middle bands.** A run starts the year an economy enters lower-middle income (charts 1 and 2) or upper-middle income (charts 3 and 4) and tracks GNI per capita, Atlas method, as a percentage of the threshold it must cross next. One row per economy-year, indexed by `years_since_entry`. Completed runs end the year the line is crossed. Charts 1 and 3 each show seven completed runs, tagged `fastest`, `median` and `slowest`: Azerbaijan crossed to upper-middle in 6 years, Viet Nam in 16, Indonesia in 29, while Russia crossed to high income in 8, Romania in 16, Argentina in 23. Ongoing runs in charts 2 and 4 are censored at 2025. There `latest_income_pct_of_line` gives the current position and `distance_to_median_years` gives the number of years the run stands behind the pace of the median completed run at that same position.

**Chart 5. Growth in middle-income economies, decade by decade.** A balanced sample of 82 economies that were middle income at the start of the window and report a usable growth record in all four decades: 1988-95, 1996-2005, 2006-15 and 2016-25. Rows with `record_type` of `chart_series` carry the unweighted and population-weighted median of decade-median growth in GNI per capita, with `weighted_median_economy` naming the economy at the weighted median. Rows with `record_type` of `economy` carry every underlying economy-decade observation.

**Charts 6 and 7. People.** Middle-income population in levels and as a share of world population, 1987 to 2050 (chart 6), and the same for all three groups (chart 7). Levels peak in 2025, shares peaked in 2016. Peak Middle Income is already behind us.

**Charts 8 and 9. Economies.** The count of middle-income economies and their share of all classified economies (chart 8), and the counts and shares for all three groups (chart 9). Counts of economies, not people. Both middle-income peaks date to 1992 and reflect the post-Soviet entrants.

**Chart 10. How country income groups fill up.** Two row types. Rows with `row_type` of `bar` give population by group in 2000, 2025 and 2050. Rows with `row_type` of `ribbon` give the flows between groups over 2000-2025 and 2025-2050, with population growth split into the part before and the part after reclassification. Over 2000-2025, forty economies led by India carried 2.5 billion people from low to middle income. Over 2025-2050, thirty-seven economies led by China are projected to carry 2.3 billion from middle to high income.

**Chart 11. The decomposition.** Each group's population in 2025 and 2050 split three ways: people already in the group at the start, people who arrived through upward reclassification, and population growth. The memo columns separate incumbent growth from arrival growth before and after the move.

**Chart 12. The high-income line is not a finish line.** All 207 classified economies with a reported GNI per capita for 2025, ranked from Bermuda at 139,370 dollars to Burundi at 240, with 2025 population and FY27 income group. The dispersion above the high-income line dwarfs the distance to it from below.

## The projection in six assumptions

Every projected figure from 2026 onward derives from the workbook. The six assumptions live in labelled cells on its Assumptions sheet, so changing one re-computes everything downstream.

1. **Starting level.** Each economy starts from its latest reported GNI per capita, Atlas method, used exactly as published. No value is adjusted to fit the band implied by its 2025 class.

2. **Growth rate.** The median of the ten annual growth rates over the decade to 2025. A median rather than a compound rate, so that a single devaluation year cannot set a twenty-five year path.

3. **Threshold drift.** One common rate of 1.244 percent a year for all three thresholds, the median annual increase over the same decade. The Bank indexes all three to the SDR deflator, and since 1990 the ratios between them have held at 3.96 and 3.09.

4. **Floor of 1.244 percent**, equal to the drift, so no economy is downgraded anywhere in the projection. It binds for 37 economies.

5. **Cap at the 90th percentile** of decade-median growth within each income group: 5.6 percent low income, 7.5 lower-middle, 9.1 upper-middle, 7.2 high income. It binds for 21 economies.

6. **Freeze.** An economy with fewer than 8 of the 10 annual observations is held at its 2025 class. This applies to 21 economies, of which six are not high income: Cuba, Eritrea, Korea Dem. Rep., South Sudan, Syria and Yemen.

Together the floor and the cap set 58 of the 197 projected growth rates, covering 21.7 percent of the classified population. About three-quarters of humanity is projected on its own observed growth rate.

## Coverage

The World Bank's historical dataset lists 226 rows, of which 224 parse as economies, every one classified in at least one year since 1987. Six left the classification before 2025 and cannot be projected: the USSR, Yugoslavia, Czechoslovakia, Serbia and Montenegro, the Netherlands Antilles and Mayotte. That leaves **218 economies** classified in 2025, of which 197 are projected forward and 21 held at their 2025 class. The 197 carry 98.2 percent of the classified population, and the classified set covers more than 99 percent of world population throughout.

Charts 1 to 5 and 12 rest on actual data only. Charts 6 to 11 combine actual data through 2025 with the projection from 2026.

## Sources

| | |
|---|---|
| Classifications and thresholds | World Bank OGHIST, 1 July 2026, Country Analytical History and Thresholds worksheets |
| GNI per capita, Atlas method | World Bank World Development Indicators, July 2026 release |
| Population to 2025 | World Bank World Development Indicators, `SP.POP.TOTL` |
| Population from 2026 | UN World Population Prospects, 2024 revision, medium variant, rebased to each economy's 2025 level |

Thresholds for 1987 to 2025 are the official values exactly as published, with no smoothing. Population weights drive the population charts and play no part in the classification projection itself.

## Licence

The contents of this repository are licensed under a Creative Commons Attribution 4.0 International Licence, see [`LICENSE`](LICENSE). Attribution to Philip Schellekens, Moving Frontiers.

Suggested citation:

> Schellekens, Philip (2026). Retire the Middle-Income Trap. Moving Frontiers. https://movingfrontiers.substack.com

Source data carry the terms of use of the World Bank and the United Nations respectively. The projections, the run definitions and the derived tables are the author's own.

Philip Schellekens writes in a personal capacity. Views expressed are his own and do not represent UNDP, the United Nations, or any other institution with which he is or has been affiliated.
