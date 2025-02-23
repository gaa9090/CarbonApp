import matplotlib.pyplot as plt

class plot_data:
    def __init__(self, historical_df, bau_df, optim_df, last_hist_year):
        """
        Parameters:
        -----------
        historical_df : DataFrame
            Historical data, containing 'Year' and 'total_emissions'.
        bau_df : DataFrame
            Business-as-usual forecast, containing 'Year' and 'total_emissions'.
        optim_df : DataFrame
            Optimized forecast, containing 'Year' and 'total_emissions'.
        last_hist_year : int
            The final year of the historical dataset, used to draw the 'forecast start' line.
        """
        self.historical_df = historical_df
        self.bau_df = bau_df
        self.optim_df = optim_df
        self.last_hist_year = last_hist_year

    def plot(self):
        plt.figure(figsize=(10, 6))

        # Plot the historical data
        plt.plot(
            self.historical_df['Year'],
            self.historical_df['total_emissions'],
            label='Historical',
            color='blue',
            marker='o'
        )

        # Dotted vertical line for forecast start
        plt.axvline(
            x=self.last_hist_year,
            color='black',
            linestyle='--',
            label='Forecast Start'
        )
        print(self.bau_df)
        # Plot BAU forecast
        plt.plot(
            self.bau_df['Year'],
            self.bau_df['total_emissions'],
            label='BAU Forecast',
            color='red',
            marker='o'
        )

        # Plot Optimized forecast
        plt.plot(
            self.optim_df['Year'],
            self.optim_df['total_emissions'],
            label='Optimized Forecast',
            color='green',
            marker='o'
        )

        plt.xlabel('Year')
        plt.ylabel('Emissions (MT CO2e)')
        plt.title('Carbon Emissions: Historical vs. Forecast')
        plt.legend()
        plt.grid(True)
        plt.show()
