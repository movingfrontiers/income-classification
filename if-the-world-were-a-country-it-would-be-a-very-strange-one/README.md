# If the World Were a Country, It Would Be a Very Strange One

Data behind [**If the World Were a Country, It Would Be a Very Strange One**](https://movingfrontiers.substack.com/p/the-world-turns-rich-this-year), Post 5 of **The Moving Escalator** on [Moving Frontiers](https://movingfrontiers.substack.com), published 21 August 2026.

Treat the world as a single country and it is nowcast to cross the World Bank's high-income threshold in 2026. On average, the planet is about to become rich. This folder holds the seven charts that ask what that average is hiding.

## Contents

Files are numbered in the order the charts appear in the post.

```
chart-1-world-gni-per-capita-and-the-median-person.csv
chart-2-mean-to-median-ratio.csv
chart-3-concentration-curve.csv
chart-4-population-by-multiple-of-world-average.csv
chart-5-economies-by-multiple-of-world-average.csv
chart-6-classification-thresholds-in-dollars.csv
chart-7-classification-thresholds-in-logs.csv
```

| File | Rows | Chart in the post |
|---|---|---|
| chart 1 | 64 | World GNI per capita and GNI per capita in the median person's country, 1987 to 2050, against the four income bands. The average crosses the high-income line in 2026; the median line does not reach it by 2050 |
| chart 2 | 64 | The ratio between the two, a measure of skewness, over the same span |
| chart 3 | 197 | Every economy ranked poorest to richest with cumulative population and cumulative GNI: the concentration curve. Plots directly from two columns |
| chart 4 | 8 | The 5.2 billion below the average are not homogeneous. Population by band of GNI per capita relative to the world average |
| chart 5 | 197 | Every economy as a multiple of the world average, from Burundi to Bermuda, with population and the bubble area used on the chart |
| chart 6 | 15 | The four income bands on a linear dollar scale, where the three lower bands together cover less than a tenth of the axis |
| chart 7 | 15 | The same bands on a logarithmic scale, which stretches the bottom and compresses the top |

Every file carries its source, its method and its caveats in commented header rows beginning with `#`. Skip those rows and the remainder reads as a clean table.

## Two reference years, deliberately

The files do not all sit in the same year, and mixing them will give wrong answers.

**Charts 6 and 7 describe the 2025 classification**, on the FY27 operational thresholds of $1,175, $4,635 and $14,375, with GNI per capita for the 2025 data year. Published figures, not projections.

**Charts 3, 4 and 5 are a 2026 snapshot**, the first nowcast year, on thresholds of $1,190, $4,693 and $14,554. World GNI per capita is $14,801 across 197 economies and 8.14 billion people.

**Charts 1 and 2 run 1987 to 2050**, actual through 2025 and nowcast thereafter, with an `actual_or_nowcast` column so the two regimes can be separated.

The year matters more than usual here, because China crosses the world average between them. On 2025 actuals China sits at 0.99 times the world average and 81 percent of humanity lives below it; on the 2026 nowcast China is at 1.01 times and the figure is the 64 percent the post reports. That is one economy of 1.4 billion people moving across a line, not a change in the shape of the distribution.

## The two definitions the post turns on

**World GNI per capita** is the population-weighted mean: the sum of all countries' GNI divided by the sum of their populations. It is the series the World Bank publishes as `NY.GNP.PCAP.CD` for the `WLD` aggregate.

**GNI per capita in the median person's country** is the population-weighted median: sort economies by their single per capita income figure, accumulate population, and take the value of the economy at which the running total first reaches half the world. It is that country's average income, not a person-level median.

Both are **between-country** measures. Every person carries the average income of the country they live in, so inequality within countries is invisible throughout this folder. The post says so explicitly and returns to it in Post 6. A survey-based measure across people would be considerably wider, and the concentration curve would sit further from the diagonal.

The identity of the median person's country changes over the period, and the files record it year by year because the series steps when the identity changes. It was India in the late 1980s, China when the line crossed the lower-middle threshold in 1998 and the upper-middle threshold in 2010, Indonesia today, and India again by the mid-2040s.

## The nowcast

Values from 2026 reflect a nowcast on a conservative constant-pace scenario that replicates country-level median per capita income growth over the last decade. Each economy grows from its 2025 level at its own median annual growth rate over the decade to 2025, floored at the threshold drift so that no economy is downgraded, and capped at the 90th percentile of decade medians within its own 2025 income group. Thresholds rise at 1.244 percent a year. Population follows the UN medium variant.

Conservative because it extrapolates a disappointing decade rather than a hopeful one. The full method, the six assumptions as they appear in the workbook, and the underlying panel of 218 economies are in the folder for the earlier post:

> https://github.com/movingfrontiers/income-classification/tree/main/the-great-income-inversion

That folder holds `income-classification-2050.xlsx` and the tidy long panel. Nothing here re-derives any of it; these seven files are the chart-level extracts.

## Figures quoted in the post

| | 1987 | 2025 | 2050 |
|---|---|---|---|
| World GNI per capita | $3,630 | $14,346 | $34,064 |
| Median person's country | $360 | $5,120 | $13,141 |
| | India | Indonesia | India |
| Mean-to-median ratio | 10.1× | 2.8× | 2.6× |

The ratio peaked at **12.7 times in 1991** and fell to **1.94 times in 2012**, a decline of almost sevenfold. It rebounded after 2015 as the commodity price collapse cut dollar GNI per capita across many exporters, and now stands at about three times, projected broadly flat to 2050.

In 2026, **64 percent of people, 5.2 billion, live in a country poorer than the world average**, and those countries together hold **17 percent of world GNI**. The poorest half of humanity holds **9 percent**; the richest tenth holds **49 percent**. Across 197 economies the range runs roughly **600-fold**, from Burundi at 0.016 times the world average to Bermuda at 9.7 times.

## Sources

| | |
|---|---|
| Classifications and thresholds | World Bank OGHIST, 1 July 2026, Country Analytical History and Thresholds worksheets |
| GNI per capita, Atlas method | World Bank World Development Indicators, July 2026 release, `NY.GNP.PCAP.CD` |
| Population to 2025 | World Bank World Development Indicators, `SP.POP.TOTL` |
| Population from 2026 | UN World Population Prospects, 2024 revision, medium variant, rebased to each economy's 2025 level |

Regional and income-group aggregates are excluded throughout; every row is a single economy. Thresholds for 1987 to 2025 are the official values exactly as published, with no smoothing.

## Licence

The contents of this folder are licensed under a Creative Commons Attribution 4.0 International Licence, see [`LICENSE`](LICENSE). Attribution to Philip Schellekens, Moving Frontiers.

Suggested citation:

> Schellekens, Philip (2026). If the world were a country, it would be a very strange one. Moving Frontiers. https://movingfrontiers.substack.com/p/the-world-turns-rich-this-year

Source data carry the terms of use of the World Bank and the United Nations respectively. The nowcast, the assumptions behind it and the derived tables are the author's own.

Philip Schellekens writes in a personal capacity. Views expressed are his own and do not represent UNDP, the United Nations, or any other institution with which he is or has been affiliated.
