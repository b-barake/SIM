import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt

def fit_distribution(data, distributions=None):
    """
    Fit various probability distributions to the data and return the best fit.

    Parameters:
    -----------
    data : array-like
        Data to fit the distribution to.
    distributions : list of str, optional
        List of distribution names to try, defaults to all distributions.

    Results:
    --------
    results : dict
        Dictionary with best fit distribution and parameters.
    """

    if distributions is None:
        distributions = ['norm', 'lognorm', 'expon', 'gamma',
                         'weibull_min', 'uniform', 'triang']

    # convert data to array
    data = np.array(data)

    # Fit each distribution
    results = {}
    for dist_name in distributions:
        try:
            # Get distributions from scipy.stats
            distribution = getattr(stats, dist_name)

            # Fit distribution to data
            params = distribution.fit(data)

            # Calculate the Kolmogorov-Smirnov test
            ks_statistic, p_value = stats.kstest(data, dist_name, args=params)

            # Store results
            results[dist_name] = {
                'params': params,
                'ks_statistic': ks_statistic,
                'p_value': p_value
            }

        except Exception as e:
            print(f"Error fitting {dist_name}: {e}")

    # Find the best fit
    best_fit = min(results, key=lambda x: results[x]['ks_statistic'])

    return {
        'best_fit': best_fit,
        'params': results[best_fit]['params'],
        'ks_statistic': results[best_fit]['ks_statistic'],
        'p_value': results[best_fit]['p_value'],
        'all_results': results
    }


def plot_distribution_fit(data, dist_name, params, bins=30, title=None):
    """
    Plot the data histogram and the fitted distribution.

    Parameters:
    -----------
    data : array-like
        Data to plot
    dist_name : str
        Name of the distribution
    params : tuple
        Parameters of the distribution
    bins : int, optional
        Number of bins for histogram
    title : str, optional
        Title for the plot

    Returns:
    --------
    fig : matplotlib.figure.Figure
        The figure object
    """

    # Convert data to numpy array
    data = np.array(data)

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot histogram
    hist,bin_edges = np.histogram(data, bins=bins, density=True)
    width = bin_edges[1] - bin_edges[0]
    ax.bar(bin_edges[:-1], hist, width=width, alpha=0.5, label='Data')

    # Get Distribution from scipy.stats
    distribution = getattr(stats, dist_name)

    # Plot PDF
    x = np.linspace(min(data), max(data), 1000)
    pdf = distribution.pdf(x, *params)
    ax.plot(x, pdf, 'r-', label=f'{dist_name} PDF')

    # Set title and label
    if title:
        ax.set_title(title)
    else:
        ax.set_title(f'Fit of {dist_name} distribution to data')

    ax.set_xlabel('Value')
    ax.set_ylabel('Density')
    ax.legend()

    return fig


def analyze_lead_time(hist_supply_df):
    """
    Analyze historical lead times from supply data.

    Parameters:
    -----------
    hist_supply_df : pandas.DataFrame
        DataFrame containing historical supply order data

    Returns:
    --------
    lead_time_results : dict
        Dictionary with lead time analysis results
    """

    # Convert dtype
    hist_supply_df['Orderdate'] = pd.to_datetime(hist_supply_df['Orderdate'])
    hist_supply_df['OrderDueDate'] = pd.to_datetime(hist_supply_df['OrderDueDate'])

    # Calculate actual lead times

    return None




