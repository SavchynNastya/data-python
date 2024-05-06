import os
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tools.eval_measures import rmse
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller


class BeerProductionForecast:
    def __init__(self, csv_file_path):
        self.df = pd.read_csv(csv_file_path)
        self.df['Month'] = pd.to_datetime(self.df['Month'])
        self.df.set_index('Month', inplace=True)

    def visualize_time_series(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.df.index, self.df['Monthly beer production'], label='Monthly beer production')
        plt.title('Monthly beer production over Time')
        plt.xlabel('Month')
        plt.ylabel('Monthly beer production')
        plt.legend()
        plt.show()

    def check_stationarity(self):
        result = adfuller(self.df['Monthly beer production'])
        print('ADF Statistic:', result[0])
        print('p-value:', result[1])
        print('Critical Values:')
        for key, value in result[4].items():
            print('\t%s: %.3f' % (key, value))
        return result[1] > 0.05

    def difference_series(self, is_stationary):
        if is_stationary:
            diff = self.df['Monthly beer production']
        else:
            diff = self.df['Monthly beer production'].diff().dropna()
        plt.figure(figsize=(10, 6))
        plt.plot(diff.index, diff, label='Differenced Monthly beer production')
        plt.title('Differenced Monthly beer production over Time')
        plt.xlabel('Month')
        plt.ylabel('Differenced Monthly beer production')
        plt.legend()
        plt.show()
        return diff

    def train_and_forecast(self, diff):
        train_data = diff[:len(diff) - 12]
        test_data = diff[len(diff) - 12:]
        arima_model = SARIMAX(train_data, order=(2, 1, 1), seasonal_order=(4, 0, 3, 12))
        arima_result = arima_model.fit()
        arima_pred = arima_result.predict(start=len(train_data), end=len(diff) - 1, typ="levels").rename(
            "ARIMA Predictions")
        plt.figure(figsize=(10, 6))
        plt.plot(test_data.index, test_data, label='Actual')
        plt.plot(test_data.index, arima_pred, label='Forecast', color='red')
        plt.title('Forecast vs Actual Monthly beer production')
        plt.xlabel('Month')
        plt.ylabel('Monthly beer production')
        plt.legend()
        plt.show()
        arima_rmse_error = rmse(test_data, arima_pred)
        arima_mse_error = arima_rmse_error ** 2
        mean_value = self.df['Monthly beer production'].mean()
        print(f'MSE Error: {arima_mse_error}\nRMSE Error: {arima_rmse_error}\nMean: {mean_value}')


csv_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "monthly-beer-production-in-austr.csv")
beer_forecaster = BeerProductionForecast(csv_file_path)
beer_forecaster.visualize_time_series()
stationary = beer_forecaster.check_stationarity()
diff_series = beer_forecaster.difference_series(stationary)
beer_forecaster.train_and_forecast(diff_series)
