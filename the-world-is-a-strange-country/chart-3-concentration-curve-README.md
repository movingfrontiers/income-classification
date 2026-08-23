# Chart 3: Cumulative share of world GNI against cumulative share of world population

**Between countries, half of humanity lives on nine percent of world income**

The concentration curve for 2026, with the equality diagonal, and three marked points: the poorest half, the position of the world average, and the richest tenth.

Published in [If the World Were a Country, It Would Be a Very Strange One](https://movingfrontiers.substack.com/p/the-world-turns-rich-this-year), Post 5 of The Moving Escalator on [Moving Frontiers](https://movingfrontiers.substack.com).

## Files

```
chart-3-concentration-curve-build.py  the script that draws the chart
chart-3-concentration-curve.csv       the data behind it
chart-3-concentration-curve.png       the chart as published
income-classification-2050.xlsx       the source workbook the data are pulled from
```

## Running it

```
python3 chart-3-concentration-curve-build.py
```

Run it from inside this folder. It reads `chart-3-concentration-curve.csv` and overwrites `chart-3-concentration-curve.png` at 1520 x 1440 pixels. Nothing else is required and nothing is downloaded.

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
| `rank_poorest_to_richest` | 1 to 197 |
| `iso3, economy` | identity |
| `gni_per_capita_usd` | 2026 nowcast level |
| `ratio_to_world_average` | the same as a multiple |
| `population_millions` | the weight |
| `cumulative_population_share_percent` | the x axis |
| `cumulative_gni_share_percent` | the y axis |
| `at_or_below_world_average` | yes or no |

## The source workbook

`income-classification-2050.xlsx` is the formula-driven workbook behind the nowcast: the classification panel, GNI per capita, population, the ten annual growth rates per economy with the median, floor and cap applied, and the thresholds. `chart-3-concentration-curve-build.py` does not read it. The csv is the extract, and the workbook is included so the chain from source to chart is complete in one folder.

The full method and the six assumptions are documented in the folder for the earlier post:

> https://github.com/movingfrontiers/income-classification/tree/main/the-great-income-inversion

## Notes on the build

The curve plots straight from two columns of the csv. The marked position of the world average is computed as the share of population in economies below it, counted directly. Do not interpolate that position by income: China sits on the boundary with 1.4 billion people, and linear interpolation through it overstates the percentile by seven points.

The title and subtitle are composited above the figure with pillow after matplotlib has rendered it, so a two-line title never squeezes the plot area. The caption block and the watermark follow the Moving Frontiers standard and are measured from rendered bounding boxes rather than estimated.

## Reproducibility

Rebuilding from the csv reproduces the published png to within antialiasing. Differences come only from the rounding in the csv, which carries populations to three decimals and ratios to four.

---

Last edited 23 August 2026. Philip Schellekens, Moving Frontiers. Licensed CC BY 4.0, see the LICENSE in the parent folder.
