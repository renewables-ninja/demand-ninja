import pandas as pd


def smooth_temperature(temperature: pd.Series, weights: list) -> pd.Series:
    """
    Smooth a temperature series over time with the given weighting for previous days.

    Params
    ------

    temperature : pd.Series
    weights : list
        The weights for smoothing. The first element is how much
        yesterday's temperature will be, the 2nd element is 2 days ago, etc.

    """
    assert isinstance(temperature, pd.Series)
    lag = temperature.copy()
    smooth = temperature.copy()

    # Run through each weight in turn going one time-step backwards each time
    for w in weights:
        # Create a time series of temperatures the day before
        lag = lag.shift(1, fill_value=lag[0])

        # Add on these lagged temperatures multiplied by this smoothing factor
        if w != 0:
            smooth = (smooth + (lag * w)).reindex()

    smooth = smooth.reindex().dropna()

    # Renormalise and return
    return smooth / (1 + sum(weights))


def get_hdd(temperature: list, threshold: float) -> list:
    return (threshold - pd.Series(temperature)).clip(lower=0).to_list()


def get_cdd(temperature: list, threshold: float) -> list:
    return (pd.Series(temperature) - threshold).clip(lower=0).to_list()
