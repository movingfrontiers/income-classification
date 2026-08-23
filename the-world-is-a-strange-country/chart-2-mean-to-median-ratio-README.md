# Chart 2: Ratio of world GNI per capita to GNI per capita in the median person's country

**Between-country inequality has fallen dramatically, but the mean still exceeds the median by a factor of three**

A single line, 1987 to 2050, with a dashed reference at 1x and five labelled points: 1987, the 1991 peak, the 2012 trough, 2025 and 2050.

Published in [If the World Were a Country, It Would Be a Very Strange One](https://movingfrontiers.substack.com/p/the-world-turns-rich-this-year), Post 5 of The Moving Escalator on [Moving Frontiers](https://movingfrontiers.substack.com).

## Files

```
chart-2-mean-to-median-ratio-build.py  the script that draws the chart
chart-2-mean-to-median-ratio.csv       the data behind it
chart-2-mean-to-median-ratio.png       the chart as published
income-classification-2050.xlsx        the source workbook the data are pulled from
```

## Running it

```
python3 chart-2-mean-to-median-ratio-build.py
```

Run it from inside this folder. It reads `chart-2-mean-to-median-ratio.csv` and overwrites `chart-2-mean-to-median-ratio.png` at 1520 x 1397 pixels. Nothing else is required and nothing is downloaded.

## Required libraries

| | Tested with |
|---|---|
| Python | 3.12 |
| numpy | 2.4.4 |
| matplotlib | 3.10.8 |
| pillow | 12.1.1 |

`csv` is from the standard library. Later versions should work; the only version-sensitive parts are the text measurement calls, which set the caption wrapping and the label placement.

## What the csv holds

Rows beginning with `#` carry the source, the method and the caveats. Skip them and the remainder is a clean table.

| Column | |
|---|---|
| `year` | 1987 to 2050 |
| `actual_or_nowcast` | actual through 2025, nowcast thereafter |
| `world_gni_per_capita_usd` | numerator |
| `median_person_country_gni_per_capita_usd` | denominator |
| `mean_to_median_ratio` | the plotted line |
| `median_person_iso3, median_person_country` | context for the steps |

## The source workbook

`income-classification-2050.xlsx` is the formula-driven workbook behind the nowcast: the classification panel, GNI per capita, population, the ten annual growth rates per economy with the median, floor and cap applied, and the thresholds. `chart-2-mean-to-median-ratio-build.py` does not read it. The csv is the extract, and the workbook is included so the chain from source to chart is complete in one folder.

The full method and the six assumptions are documented in the folder for the earlier post:

> https://github.com/movingfrontiers/income-classification/tree/main/the-great-income-inversion

## Notes on the build

The peak and trough years are found from the data, not hard-coded, so they move if the series is revised. The five label positions are hand-set, because the curve is a steep descent into a narrow V and no automatic placement clears it.

The title and subtitle are composited above the figure with pillow after matplotlib has rendered it, so a two-line title never squeezes the plot area. The caption block and the watermark follow the Moving Frontiers standard and are measured from rendered bounding boxes rather than estimated.

## Reproducibility

Rebuilding from the csv reproduces the published png to within antialiasing. Differences come only from the rounding in the csv, which carries populations to three decimals and ratios to four.

---

Last edited 23 August 2026. Philip Schellekens, Moving Frontiers. Licensed CC BY 4.0, see the LICENSE in the parent folder.
