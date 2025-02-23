# model_training.py
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
import time

pd.options.display.float_format = '{:.2f}'.format

class ModelTraining():
    def __init__(self, df, start_year):
        self.df = df
        self.start_year = start_year
        self.window_size = len(self.df.columns) - 3


    def load_dataset(self, file_path):
        """Load a CSV file into a pandas DataFrame."""
        self.df = pd.read_csv(file_path)
        return self.df

    def merge_datasets(self, df1, df2, on_columns=['year', 'region'], how='left'):
        """
        Merge two DataFrames on specified columns.
        'how' can be 'left', 'right', 'inner', or 'outer'.
        """
        merged_df = pd.merge(df1, df2, on=on_columns, how=how)
        return merged_df

    # NEW 
    def scale_features(self, df, feature_cols, target_col):
        """
        Scale the given feature columns + target column between 0 and 1.
        Returns the scalsed DataFrame and the scaler object.
        """
        all_cols = feature_cols + [target_col]  # e.g. ['transportation_percent', 'energy_percent', 'waste_percent', 'total_emissions']
        
        scaler = MinMaxScaler()
        df_scaled = df.copy()
        
        # Fit + transform on all columns (features + target)
        df_scaled[all_cols] = scaler.fit_transform(df_scaled[all_cols])
        
        return df_scaled, scaler


    # reads raw data, returns cleaned dataset
    def prepare_data(self):
        return self.clean_data(self.load_dataset("emissions_rochester.csv"))



    def create_sequences(self, df, feature_cols, target_col):
        data = df[feature_cols + [target_col]].values
        X, y = [], []
        
        for i in range(len(data) - self.window_size):

            X.append(data[i : i + self.window_size, 0:len(feature_cols)])
            y.append(data[i + self.window_size, len(feature_cols)])  
        
        return np.array(X), np.array(y)



    # NEW
    def build_lstm_model(self, shape):
        model = tf.keras.Sequential([
            layers.LSTM(64, return_sequences=True, input_shape=shape),
            layers.Dropout(0.2),
            layers.LSTM(32, return_sequences=False),
            layers.Dense(16, activation='relu'),
            layers.Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')
        return model




    def train_model_lstm(self, df):
        df = df.sort_values('Year').reset_index(drop=True)
        
        feature_cols = list(tuple(self.df.columns[1:-1]))
        target_col = self.df.columns[-1]
        
        # Scale both features + target
        df_scaled, scaler = self.scale_features(df, feature_cols, target_col)

        # Drop rows where scaled columns might be NaN
        df_scaled = df_scaled.dropna(subset=feature_cols + [target_col])
        
        # window_size = len(df.columns) - 3
        
        # print(f"WINDOW SIZE: {window_size}")
        # print(len(df.columns))
        # time.sleep(2)
        X, y = self.create_sequences(df_scaled, feature_cols, target_col)
        
        # The rest is unchanged
        num_samples = X.shape[0]
        train_end = int(num_samples * 0.7)
        val_end = int(num_samples * 0.85)
        
        X_train, y_train = X[:train_end], y[:train_end]
        X_val,   y_val   = X[train_end:val_end], y[train_end:val_end]
        X_test,  y_test  = X[val_end:], y[val_end:]


        
        # Build + train model
        input_shape = (self.window_size, len(feature_cols))
        model = self.build_lstm_model(input_shape)
        
        early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
        
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=100,
            batch_size=16,
            verbose=1,
            callbacks=[early_stopping]
        )
        
        # Evaluate
        y_pred_test = model.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred_test)
        mse = mean_squared_error(y_test, y_pred_test)
        print(f"Test MAE: {mae:.3f}, Test MSE: {mse:.3f}")

        # print("X_train shape:", X_train.shape)
        # print("X_val shape:", X_val.shape)
        # print("X_test shape:", X_test.shape)
        # print("Model input shape:", model.input_shape)
        # time.sleep(10)
        
        # Return model + scaler
        return model, X_test, y_test, scaler




    def enhanced_sensitivity_analysis(self,
        model,
        base_seq,
        sector_indices,
        sector_delta=-5,
        keep_sum_100=False
    ):
        if len(base_seq.shape) == 2:
            # (window_size, num_features) -> (1, window_size, num_features)
            base_seq = np.expand_dims(base_seq, axis=0)

        # base_seq.shape => (1, window_size, num_features)
        batch_size, timesteps, num_features = base_seq.shape

        if timesteps != self.window_size:
            print(f"Warning: The input sequence has {timesteps} timesteps, "
                f"which does not match window_size={self.window_size}.")

        base_pred = model.predict(base_seq)[0][0]  

        results = []

        for t in range(self.window_size):

            for sector, idx in sector_indices.items():
                
                new_seq = base_seq.copy()

                original_val = new_seq[0, t, idx]
                new_val = original_val + sector_delta

                new_val = max(new_val, 0.0)

                if keep_sum_100:
                    sum_others = 0
                    for s, j in sector_indices.items():
                        if j != idx:
                            sum_others += new_seq[0, t, j]
                    
                    # old total
                    old_total = sum_others + original_val
                    new_total = sum_others + new_val

                    if old_total > 0 and new_total > 0:
                        scale_factor = (old_total - original_val) / (new_total - new_val)
                        # scale only the other sectors
                        for s2, j2 in sector_indices.items():
                            if j2 != idx:
                                # proportionally scale this sector
                                old_val2 = new_seq[0, t, j2]
                                new_seq[0, t, j2] = old_val2 * scale_factor

                new_seq[0, t, idx] = new_val

                new_pred = model.predict(new_seq)[0][0]
                reduction = base_pred - new_pred

                # Store result in list
                results.append({
                    "sector": sector,
                    "timestep": t,
                    "base_pred": base_pred,
                    "new_pred": new_pred,
                    "reduction": reduction
                })

        return results


    def pick_best_sector_to_reduce(self,
        model,
        current_seq,
        sector_indices,
        delta=-5
    ):
        """
        Perform a small sensitivity analysis on the current sequence, 
        returning the sector name that yields the largest predicted emission reduction 
        when decreased by 'delta'.
        """
        # We can reuse your existing enhanced_sensitivity_analysis but with keep_sum_100=False 
        # (or True, if you prefer).

        base_pred = model.predict(current_seq)[0][0]  # Get base prediction
        print(f"Original Prediction: {base_pred:.3f}")  # <-- Debugging line



        results = self.enhanced_sensitivity_analysis(
            model=model,
            base_seq=current_seq,
            sector_indices=sector_indices,
            sector_delta=delta,
            keep_sum_100=False  # or True, if you want sums to remain 100%
        )
        
        # Sort results by the biggest 'reduction' field
        sorted_results = sorted(results, key=lambda r: r["reduction"], reverse=True)

        if not sorted_results or sorted_results[0]['reduction'] <= 0:
            print("No meaningful reduction detected. Model may not be learning dependencies.")

        
        best = sorted_results[0]

        # can remove later if needed
        print(f"Best sector to reduce: {best['sector']}, "
            f"Reduction: {best['reduction']:.3f}, "
            f"New prediction: {best['new_pred']:.3f}")

        return best["sector"], best["reduction"], best["new_pred"]




    def compute_linear_slopes(self, df, feature_cols, start_year):
        slopes = {}
        # Filter
        hist = df[df['Year'] <= start_year]

        # numeric and reshaped as 2D
        X = hist['Year'].values.reshape(-1, 1)
        for col in feature_cols:
            y = hist[col].values

            model_lr = LinearRegression().fit(X, y)
            # slope = model_lr.coef_[0]
            # intercept = model_lr.intercept_
            current_year = hist['Year'].max()
            current_value = hist[hist['Year'] == current_year][col].values[0]
            predicted_next = model_lr.predict(np.array([[current_year + 1]]))[0]
            change = predicted_next - current_value
            slopes[col] = change


        return slopes



    def forecast_future(
    self,
    model,
    df,
    start_year,
    end_year,
    feature_cols,
    target_col,
    scenario="business_as_usual",
    slope_per_year=None,
    sector_indices=None,
    scaler=None
    ):
        df = df.sort_values('Year').reset_index(drop=True)
        df['Year'] = df['Year'].astype(int)
        
        forecast_df = df.copy()
        
        # Grab only historical data up to 'start_year'
        hist_subset = forecast_df[forecast_df['Year'] <= start_year]
        if len(hist_subset) < self.window_size:
            raise ValueError(
                f"Not enough data up to year {start_year} to form a {self.window_size}-step sequence."
            )
        
        # Compute or retrieve slopes
        if scenario == "business_as_usual" and slope_per_year is None:
            slopes = self.compute_linear_slopes(hist_subset, feature_cols, start_year)
        else:
            # If slope_per_year=1 or any number, we set all slopes to that fixed value
            slopes = {col: slope_per_year for col in feature_cols}
        
        # Prepare the initial 'window' for the LSTM
        last_window = hist_subset.tail(self.window_size)
        seq = np.expand_dims(last_window[feature_cols].values, axis=0)  
        # shape: (1, window_size, num_features)

        current_year = start_year
        while current_year < end_year:
            next_year = current_year + 1

            # 1) Predict the current total_emissions using the last window
            pred_emissions = model.predict(seq)[0][0]

            # 2) Retrieve the last timestep from seq so we can modify the features
            last_timestep = seq[0, -1, :].copy()
            feature_dict = dict(zip(feature_cols, last_timestep))

            # 3) Branch: BAU or Optimized
            if scenario == "business_as_usual":
                # For each feature, apply some fraction of the slope
                # so the forecast naturally grows
                for col in feature_cols:
                    # e.g. use 0.2 * slope => 20% of the slope
                    # to avoid huge jumps
                    feature_dict[col] += (slopes[col] or 0) * 0.2

                new_row = {
                    'Year': next_year,
                    **feature_dict,
                    target_col: pred_emissions
                }

            elif scenario == "optim_reduction":
                if sector_indices is None:
                    raise ValueError("For 'optim_reduction' scenario, you must supply 'sector_indices'")

                # First, apply the same small slope so there's
                # some upward pressure
                for col in feature_cols:
                    feature_dict[col] += (slopes[col] or 0) * 0.2

                # Then choose best sector to reduce
                best_sector, best_reduction, best_new_pred = self.pick_best_sector_to_reduce(
                    model=model,
                    current_seq=seq,
                    sector_indices=sector_indices,
                    delta=-5  # small negative tweak for sensitivity analysis
                )

                # Instead of subtracting a big constant (like 10000),
                # reduce that sector by e.g. 10% of its *new* value
                if best_sector in feature_dict:
                    current_val = feature_dict[best_sector]
                    feature_dict[best_sector] = max(current_val * 0.9, 0)  # 10% cut

                # Re-predict after the cut
                new_pred_emissions = model.predict(seq)[0][0]

                # If you want to keep a clamp, keep it loose
                # so you see real reductions in the final line
                prev_emissions = forecast_df.iloc[-1][target_col]
                max_drop = 0.2  # allow up to 20% drop year to year, for instance
                min_allowed = prev_emissions * (1 - max_drop)

                if new_pred_emissions < min_allowed:
                    new_pred_emissions = min_allowed

                new_row = {
                    'Year': next_year,
                    **feature_dict,
                    target_col: new_pred_emissions
                }

            else:
                # Fallback scenario
                new_row = {
                    'Year': next_year,
                    **feature_dict,
                    target_col: pred_emissions
                }

            # Append new row to forecast
            new_row_df = pd.DataFrame([new_row], columns=forecast_df.columns)
            forecast_df = pd.concat([forecast_df, new_row_df], ignore_index=True)

            # 4) Shift the seq window for the next iteration
            new_seq_array = np.array(list(feature_dict.values())).reshape(1, 1, -1)
            seq = np.concatenate([seq[:, 1:, :], new_seq_array], axis=1)

            current_year = next_year

        # Inverse transform if a scaler is provided
        if scaler is not None:
            all_cols = feature_cols + [target_col]
            scaled_data = forecast_df[all_cols].values
            original_data = scaler.inverse_transform(scaled_data)
            forecast_df[all_cols] = original_data

        return forecast_df

            

    


    # if __name__ == "__main__":
    #     df_merged = prepare_data()
    #     model, X_test, y_test, scaler = train_model_lstm(df_merged)
        
    #     if len(X_test) > 0:
    #         sample_seq = X_test[0]
    #         last_timestep = {
    #             'transportation_percent': sample_seq[-1][0],
    #             'energy_percent': sample_seq[-1][1],
    #             'waste_percent': sample_seq[-1][2]
    #         }
    #         print("\n--- Sensitivity Analysis ---")
    #         sample_seq_reshaped = np.expand_dims(sample_seq, axis=0)
    #         sector_map = {
    #             'waste_percent': 0,
    #             'transportation_percent': 1,
    #             'energy_percent': 2
    #         }
    #         results = enhanced_sensitivity_analysis(
    #             model=model,
    #             base_seq=sample_seq_reshaped,
    #             sector_indices=sector_map,
    #             window_size=3,
    #             sector_delta=-500,
    #             keep_sum_100=True
    #         )
    #         results_sorted = sorted(results, key=lambda x: x["reduction"], reverse=True)
    #         print("Top 5 scenarios with largest predicted emission reduction:")
    #         for scenario in results_sorted[:5]:
    #             print(
    #                 f"Timestep={scenario['timestep']}, "
    #                 f"Sector={scenario['sector']}, "
    #                 f"Reduction={scenario['reduction']:.3f}, "
    #                 f"NewPred={scenario['new_pred']:.3f}"
    #             )
        
    #     # Forecast outcomes
    #     last_hist_year = 2023
    #     end_year = 2043
        
    #     bau_df = forecast_future(
    #         model=model,
    #         df=df_merged,
    #         start_year=last_hist_year,
    #         end_year=end_year,
    #         feature_cols=['transportation_percent', 'energy_percent', 'waste_percent'],
    #         target_col='total_emissions',
    #         window_size=3,
    #         scenario='business_as_usual',
    #         slope_per_year=None  # Linear regression will compute slopes
    #     )
        
    #     print("BAU Forecast:")
    #     print(bau_df.tail())
    #     print("Optimized Forecast:")
    #     print(optim_df.tail())optim