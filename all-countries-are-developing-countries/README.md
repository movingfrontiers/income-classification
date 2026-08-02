# All countries are developing countries

Data behind **All Countries Are Developing Countries**, Post 2 of **The Moving Escalator**, a series on [Moving Frontiers](https://movingfrontiers.substack.com) about four decades of movement through the World Bank's country income classification, where the world is heading by 2050, and whether the classification itself remains fit for purpose.

The folder holds two kinds of data. The first is a snapshot of the classification itself: every classified economy in FY27 with its income level, population and group. The second is a decade of media language: how often twelve major news outlets around the world say "developing country", "developed country" and "high-income country", by outlet and by month.

For the full projection panel behind the series, 218 economies from 1987 to 2050 with thresholds, growth rates and assumptions, see the [root of this repository](../).

## Contents

```
chart-1-the-country-income-classification-on-linear-and-log-scale.csv
chart-2-how-major-news-outlets-label-countries.csv
chart-3-evolution-of-country-terminology-by-major-news-outlets.csv
chart-4-ratio-of-developed-vs-high-income-by-news-outlet.csv
```

Each file carries the data of the chart of the same name in the post.

### chart-1: the classification in FY27

One row per classified economy, 207 in all: every economy with a reported income level in the FY27 classification.

| column | content |
|---|---|
| `economy` | economy name as listed by the World Bank |
| `gni_per_capita_usd_atlas_2025` | GNI per capita, Atlas method, current US$, 2025 |
| `population_millions_2025` | population in millions, 2025 |
| `income_group_fy27` | Low, Lower middle, Upper middle or High income, per the classification of 1 July 2026 |
| `shown_in_linear_panel` | FALSE for the five economies above the $90,000 cut of the chart's linear panel: Bermuda, Liechtenstein, Switzerland, Norway and Luxembourg |

The FY27 thresholds are $1,175, $4,635 and $14,375. Argentina and Türkiye are upper-middle income in the FY27 classification while already reporting 2025 income above the high-income threshold, so they plot above the line.

### chart-2: mentions per 1,000 stories by outlet

One row per outlet, twelve in all. Columns give stories matching each query per 1,000 stories the outlet published over the full period, January 2016 to July 2026, for the three phrases `developing country`, `developed country` and `high-income country`.

### chart-3: the evolution over time

One row per month, `2017-01` to `2026-06`. Columns give twelve-month rolling shares per 1,000 stories, pooled across the twelve outlets, for the same three phrases. Complete months only. The series begins twelve months into the sample because of the rolling window.

### chart-4: the ratio of "developed" to "high-income"

One row per outlet: the number of "developed country" stories per "high-income country" story over the full period, as reported in the post. TASS mentioned the high-income term in only 10 stories across the whole decade, which is why its ratio should be read as an order of magnitude rather than a point estimate.

## The media data in brief

Queries were run against the [Media Cloud](https://mediacloud.org) story index, January 2016 to July 2026, retrieved August 2026. Queries match the exact phrases *developing country* or *countries*, *developed country* or *countries*, and *high-income country* or *countries*, language English. Shares are stories matching each query per 1,000 stories the outlet published, so differences in outlet size wash out.

The twelve outlets, grouped by country: Hong Kong SAR, China (South China Morning Post), India (The Times of India), Japan (The Japan Times), Malaysia (The Star), Nigeria (Punch), Qatar (Al Jazeera), Russia (Russian News Agency TASS), the United Kingdom (BBC and The Guardian) and the United States (CNN, Fox News and The New York Times).

Three caveats. The Japan Times, Punch and TASS have gaps in daily index coverage, covering 87, 93 and 93 percent of days, but results do not change significantly against a balanced sample. The sample is English-language only, so it says nothing about how these terms travel in other languages. And exact phrase matching is deliberately narrow: it misses "developing world", "developed economies" and every variant in between, which makes the counts conservative rather than complete.

Values are as plotted in the published figures: two decimals in the outlet file, three in the monthly file.

## Sources

| | |
|---|---|
| Classifications and thresholds | World Bank OGHIST, 1 July 2026, Country Analytical History and Thresholds worksheets |
| GNI per capita, Atlas method | World Bank World Development Indicators, July 2026 release |
| Population | World Bank World Development Indicators, `SP.POP.TOTL` |
| Media mentions | Media Cloud story index, January 2016 to July 2026, retrieved August 2026 |

## Licence

The contents of this folder are licensed under a Creative Commons Attribution 4.0 International Licence, see [`LICENSE`](LICENSE.txt). Attribution to Philip Schellekens, Moving Frontiers.

Suggested citation:

> Schellekens, Philip (2026). All countries are developing countries: data. Moving Frontiers. https://movingfrontiers.substack.com

Source data carry the terms of use of the World Bank and of Media Cloud respectively. The analysis and the derived tables are the author's own.

Philip Schellekens writes in a personal capacity. Views expressed are his own and do not represent UNDP, the United Nations, or any other institution with which he is or has been affiliated.
