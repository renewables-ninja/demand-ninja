# Demand.ninja

The Demand.ninja model delivers an hourly time-series of energy demand for a given location, for your chosen temperaure thresholds and BAIT (building-adjusted internal temperature) parameters which describe the characteristics of a building and its occupants.

This code also runs online on the [Renewables.ninja service](https://www.renewables.ninja/).

## Example use

```python

import demand_ninja

# `inputs` has to be a pandas.DataFrame with four columns,
# humidity, radiation_global_horizontal, temperature,
# and wind_speed_2m
inputs = pd.DataFrame(...)

# `result`` will be a pandas.DataFrame
# setting raw=True includes the input data and intermediate results
# in the final DataFrame
result = demand_ninja.demand(inputs, raw=True)

```

## Version history

See [CHANGELOG.md](CHANGELOG.md).

## Credits and contact

Contact [Iain Staffell](mailto:i.staffell@imperial.ac.uk) and [Nathan Johnson](mailto:nathan.johnson17@imperial.ac.uk) if you have questions about Demand.ninja.  Demand.ninja is a component of the [Renewables.ninja](https://renewables.ninja) project, developed by Stefan Pfenninger and Iain Staffell.

## Citation

If you use Demand.ninja or code derived from it in academic work, please cite:

Iain Staffell, Stefan Pfenninger and Nathan Johnson (2023). _A global model of hourly space heating and cooling demand at multiple spatial scales._ Nature Energy.

## License

The code is available under a BSD-3-Clause license.
