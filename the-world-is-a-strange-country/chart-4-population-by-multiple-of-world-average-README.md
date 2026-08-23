# Chart 4: Population by economy GNI per capita relative to the world average

**Two in three people live in a country poorer than the world average**

Seven bars for 2026, the count of economies printed inside each, with the world average marked by a dashed line between the fourth and fifth.

Published in [If the World Were a Country, It Would Be a Very Strange One](https://movingfrontiers.substack.com/p/the-world-turns-rich-this-year), Post 5 of The Moving Escalator on [Moving Frontiers](https://movingfrontiers.substack.com).

## Files

```
chart-4-population-by-multiple-of-world-average-build.py  the script that draws the chart
chart-4-population-by-multiple-of-world-average.csv       the data behind it
chart-4-population-by-multiple-of-world-average.png       the chart as published
income-classification-2050.xlsx                           the source workbook the data are pulled from
```

## Running it

```
python3 chart-4-population-by-multiple-of-world-average-build.py
```

Run it from inside this folder. It reads `chart-4-population-by-multiple-of-world-average.csv` and overwrites `chart-4-population-by-multiple-of-world-average.png` at 1520 x 1370 pixels. Nothing else is required and nothing is downloaded.

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
| `band` | the seven bands, plus a total row |
| `lower_bound_multiple, upper_bound_multiple` | band edges |
| `population_millions, population_billions` | bar height |
| `share_of_covered_population_percent` | the shares quoted on the chart |
| `n_economies` | the number printed inside each bar |
| `side_of_world_average` | below or above |

## The source workbook

`income-classification-2050.xlsx` is the formula-driven workbook behind the nowcast: the classification panel, GNI per capita, population, the ten annual growth rates per economy with the median, floor and cap applied, and the thresholds. `chart-4-population-by-multiple-of-world-average-build.py` does not read it. The csv is the extract, and the workbook is included so the chain from source to chart is complete in one folder.

The full method and the six assumptions are documented in the folder for the earlier post:

> https://github.com/movingfrontiers/income-classification/tree/main/the-great-income-inversion

## Notes on the build

The callout box and its leader are drawn as plain text plus a line rather than as a matplotlib annotation, because get_window_extent on an Annotation includes the arrow and makes overlap checks unreliable.

The title and subtitle are composited above the figure with pillow after matplotlib has rendered it, so a two-line title never squeezes the plot area. The caption block and the watermark follow the Moving Frontiers standard and are measured from rendered bounding boxes rather than estimated.

## Reproducibility

Rebuilding from the csv reproduces the published png to within antialiasing. Differences come only from the rounding in the csv, which carries populations to three decimals and ratios to four.

---

Last edited 23 August 2026. Philip Schellekens, Moving Frontiers. Licensed CC BY 4.0, see the LICENSE in the parent folder.
