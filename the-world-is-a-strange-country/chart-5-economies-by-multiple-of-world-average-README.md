# Chart 5: Every economy as a multiple of world GNI per capita

**A 600-fold range, from Burundi to Bermuda**

All 197 economies as bubbles on a log scale for 2026, area proportional to population on a logarithmic scale, with six labelled and a population size legend.

Published in [If the World Were a Country, It Would Be a Very Strange One](https://movingfrontiers.substack.com/p/the-world-turns-rich-this-year), Post 5 of The Moving Escalator on [Moving Frontiers](https://movingfrontiers.substack.com).

## Files

```
chart-5-economies-by-multiple-of-world-average-build.py  the script that draws the chart
chart-5-economies-by-multiple-of-world-average.csv       the data behind it
chart-5-economies-by-multiple-of-world-average.png       the chart as published
income-classification-2050.xlsx                          the source workbook the data are pulled from
```

## Running it

```
python3 chart-5-economies-by-multiple-of-world-average-build.py
```

Run it from inside this folder. It reads `chart-5-economies-by-multiple-of-world-average.csv` and overwrites `chart-5-economies-by-multiple-of-world-average.png` at 1360 x 1651 pixels. Nothing else is required and nothing is downloaded.

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
| `rank_poorest_to_richest` | 1 to 197, bottom to top of the chart |
| `iso3, economy` | identity |
| `gni_per_capita_usd` | 2026 nowcast level |
| `ratio_to_world_average` | the x axis |
| `population_millions` | the weight |
| `bubble_area` | the plotted marker area, already computed |
| `side_of_world_average` | below or above, which sets the colour |

## The source workbook

`income-classification-2050.xlsx` is the formula-driven workbook behind the nowcast: the classification panel, GNI per capita, population, the ten annual growth rates per economy with the median, floor and cap applied, and the thresholds. `chart-5-economies-by-multiple-of-world-average-build.py` does not read it. The csv is the extract, and the workbook is included so the chain from source to chart is complete in one folder.

The full method and the six assumptions are documented in the folder for the earlier post:

> https://github.com/movingfrontiers/income-classification/tree/main/the-great-income-inversion

## Notes on the build

Six labels are placed by a solver that tests each candidate box against every bubble as a circle in display space, plus the other labels and the axes edges. Bermuda and Burundi are hand-placed with vertical leaders. The bubble area formula is reproduced in the bubble_area column of the csv.

The title and subtitle are composited above the figure with pillow after matplotlib has rendered it, so a two-line title never squeezes the plot area. The caption block and the watermark follow the Moving Frontiers standard and are measured from rendered bounding boxes rather than estimated.

## Reproducibility

Rebuilding from the csv reproduces the published png to within antialiasing. Differences come only from the rounding in the csv, which carries populations to three decimals and ratios to four.

---

Last edited 23 August 2026. Philip Schellekens, Moving Frontiers. Licensed CC BY 4.0, see the LICENSE in the parent folder.
