# Chart 1: World GNI per capita and the income of the median person's country

**World GNI per capita crosses the high-income line in 2026**

Two lines against the four shaded income bands, 1987 to 2050 on a log scale. Markers sit at every threshold crossing, labelled with the year and the economy concerned.

Published in [If the World Were a Country, It Would Be a Very Strange One](https://movingfrontiers.substack.com/p/the-world-turns-rich-this-year), Post 5 of The Moving Escalator on [Moving Frontiers](https://movingfrontiers.substack.com).

## Files

```
chart-1-world-gni-per-capita-and-the-median-person-build.py  the script that draws the chart
chart-1-world-gni-per-capita-and-the-median-person.csv       the data behind it
chart-1-world-gni-per-capita-and-the-median-person.png       the chart as published, 1600 x 1585
income-classification-2050.xlsx                              the source workbook the data are pulled from
```

## Running it

```
python3 chart-1-world-gni-per-capita-and-the-median-person-build.py
```

Run it from inside this folder. It reads `chart-1-world-gni-per-capita-and-the-median-person.csv` and overwrites `chart-1-world-gni-per-capita-and-the-median-person.png` at 1600 x 1585 pixels. Nothing else is required and nothing is downloaded.

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
| `world_gni_per_capita_usd` | the white line |
| `median_person_country_gni_per_capita_usd` | the amber line |
| `median_person_iso3, median_person_country` | which economy the median person lives in that year |
| `n_economies, n_economies_with_population` | coverage |
| `covered_population_millions` | denominator of the weighting |
| `threshold_lic_lmic_usd, threshold_lmic_umic_usd, threshold_umic_hic_usd` | the boundaries of the four shaded bands |

## The source workbook

`income-classification-2050.xlsx` is the formula-driven workbook behind the nowcast: the classification panel, GNI per capita, population, the ten annual growth rates per economy with the median, floor and cap applied, and the thresholds. `chart-1-world-gni-per-capita-and-the-median-person-build.py` does not read it. The csv is the extract, and the workbook is included so the chain from source to chart is complete in one folder.

The full method and the six assumptions are documented in the folder for the earlier post:

> https://github.com/movingfrontiers/income-classification/tree/main/the-great-income-inversion

## Notes on the build

The build recomputes the crossings from the data rather than hard-coding them: for each series and each threshold it compares consecutive years against that year's own threshold, since the thresholds move. It should print five crossings, at 1998, 2010, 2020, 2022 and 2026.

The title and subtitle are composited above the figure with pillow after matplotlib has rendered it, so a two-line title never squeezes the plot area. The caption block and the watermark follow the Moving Frontiers standard and are measured from rendered bounding boxes rather than estimated.

## Reproducibility

Rebuilding from the csv reproduces the published png to within antialiasing. Differences come only from the rounding in the csv, which carries populations to three decimals and ratios to four.

---

Last edited 23 August 2026. Philip Schellekens, Moving Frontiers. Licensed CC BY 4.0, see the LICENSE in the parent folder.
