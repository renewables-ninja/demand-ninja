import os

import numpy as np
import pandas as pd

from demand_ninja.util import smooth_temperature, get_cdd, get_hdd


DIURNAL_PROFILES = pd.read_csv(
    os.path.join(os.path.dirname(__file__), "diurnal_profiles.csv"), index_col=0
)


def _bait(
    weather: pd.DataFrame,
    smoothing: float,
    solar_gains: float,
    wind_chill: float,
    humidity_discomfort: float,
) -> pd.Series:

    # We compute 'setpoint' values for wind, sun and humidity
    # these are the 'average' values for the given temperature
    # and are used to decide if it is windier than average,
    # sunnier than aveage, etc.  this makes N correlate roughly
    # 1:1 with T, rather than is biased above or below it.
    T = weather["temperature"]
    setpoint_S = 100 + 7 * T  # W/m2
    setpoint_W = 4.5 - 0.025 * T  # m/s
    setpoint_H = (1.1 + 0.06 * T).rpow(np.e)  # g water per kg air
    setpoint_T = 16  # degrees - around which 'discomfort' is measured

    # Calculate the unsmoothed ninja temperature index
    # this is a 'feels like' index - how warm does it 'feel' to your building

    # Initialise it to temperature
    N = weather["temperature"].copy()

    # If it's sunny, it feels warmer
    N = N + (weather["radiation_global_horizontal"] - setpoint_S) * solar_gains

    # If it's windy, it feels colder
    N = N + (weather["wind_speed_2m"] - setpoint_W) * wind_chill

    # If it's humid, both hot and cold feel more extreme
    discomfort = N - setpoint_T
    N = (
        setpoint_T
        + discomfort
        + (
            discomfort
            # Convert humidity from kg/kg to g/kg
            * ((weather["humidity"] * 1000) - setpoint_H)
            * humidity_discomfort
        )
    )

    # Apply temporal smoothing to our temperatures over the last two days
    # we assume 2nd day smoothing is the square of the first day (i.e. compounded decay)
    N = smooth_temperature(N, weights=[smoothing, smoothing**2])

    # Blend the smoothed BAIT with raw temperatures to account for occupant
    # behaviour changing with the weather (i.e. people open windows when it's hot)

    # These are fixed parameters we don't expose the user to
    lower_blend = 15  # *C at which we start blending T into N
    upper_blend = 23  # *C at which we have fully blended T into N
    max_raw_var = 0.5  # maximum amount of T that gets blended into N

    # Transform this window to a sigmoid function, mapping lower & upper onto -5 and +5
    avg_blend = (lower_blend + upper_blend) / 2
    dif_blend = upper_blend - lower_blend
    blend = (weather["temperature"] - avg_blend) * 10 / dif_blend
    blend = max_raw_var / (1 + (-blend).rpow(np.e))

    # Apply the blend
    N = (weather["temperature"] * blend) + (N * (1 - blend))

    return N


def _energy_demand_from_bait(
    bait: pd.Series,
    heating_threshold: float,
    cooling_threshold: float,
    base_power: float,
    heating_power: float,
    cooling_power: float,
    use_diurnal_profile: bool,
) -> pd.DataFrame:
    """
    Convert temperatures into energy demand.

    """
    output = pd.DataFrame(index=bait.index.copy())
    output["hdd"] = 0
    output["cdd"] = 0
    output["heating_demand"] = 0
    output["cooling_demand"] = 0
    output["total_demand"] = 0

    # Add demand for heating
    if heating_power > 0:
        output["hdd"] = get_hdd(bait, heating_threshold)
        output["heating_demand"] = output["hdd"] * heating_power

    # Add demand for cooling
    if cooling_power > 0:
        output["cdd"] = get_cdd(bait, cooling_threshold)
        output["cooling_demand"] = output["cdd"] * cooling_power

    # Apply the diurnal profiles if wanted
    if use_diurnal_profile:
        # Get the hour of day for each timestep - which we use as an array index
        hours = output.index.hour
        profiles = DIURNAL_PROFILES.loc[hours, :]
        profiles.index = output.index

        # Convolute
        output["heating_demand"] = output["heating_demand"] * profiles.loc[:, "heating"]
        output["cooling_demand"] = output["cooling_demand"] * profiles.loc[:, "cooling"]

    # Sum total demand
    output["total_demand"] = (
        base_power + output["heating_demand"] + output["cooling_demand"]
    )

    return output


def demand(
    hourly_inputs: pd.DataFrame,
    heating_threshold: float = 14,
    cooling_threshold: float = 20,
    base_power: float = 0,
    heating_power: float = 0.3,
    cooling_power: float = 0.15,
    smoothing: float = 0.5,
    solar_gains: float = 0.012,
    wind_chill: float = -0.20,
    humidity_discomfort: float = 0.05,
    use_diurnal_profile: bool = True,
    raw: bool = False,
) -> pd.DataFrame:
    """
    Returns a pd.DataFrame of heating_demand, cooling_demand, and total_demand. If
    `raw` is True (default False), then also returns the input data and the
    intermediate BAIT.

    Params
    ------

    hourly_inputs : pd.DataFrame
        Must contain humidity, radiation_global_horizontal, temperature
        and wind_speed_2m columns

    """
    assert list(sorted(hourly_inputs.columns)) == [
        "humidity",
        "radiation_global_horizontal",
        "temperature",
        "wind_speed_2m",
    ]

    daily_inputs = hourly_inputs.resample("1D").mean()

    # Calculate BAIT
    daily_bait = _bait(
        daily_inputs,
        smoothing,
        solar_gains,
        wind_chill,
        humidity_discomfort,
    )

    # Upsample BAIT to hourly
    daily_bait.index = pd.date_range(
        daily_bait.index[0] + pd.Timedelta("12H"),
        daily_bait.index[-1] + pd.Timedelta("12H"),
        freq="1D",
    )
    hourly_inputs["bait"] = daily_bait.reindex(hourly_inputs.index).interpolate(
        method="cubicspline", limit_direction="both"
    )

    # Transform to degree days and energy demand
    result = _energy_demand_from_bait(
        hourly_inputs["bait"],
        heating_threshold,
        cooling_threshold,
        base_power,
        heating_power,
        cooling_power,
        use_diurnal_profile,
    )

    result = result.loc[:, ["total_demand", "heating_demand", "cooling_demand"]]

    if raw:
        result = pd.concat((result, hourly_inputs), axis=1)

    return result
