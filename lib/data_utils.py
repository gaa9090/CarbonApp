import pandas as pd
from lib._model_training import MinMaxScaler

def load_dataset(file_path):
    """Load a CSV file into a pandas DataFrame."""
    return pd.read_csv(file_path)

def clean_data(df):
    """
    Perform basic cleaning on the DataFrame.
    - Drop duplicates
    - Fill or drop missing values, etc.
    """
    df = df.drop_duplicates()
    df = df.fillna(method='ffill')  # Example: forward-fill
    return df

def merge_datasets(df1, df2, on_columns=['year', 'region'], how='left'):
    """
    Merge two DataFrames on specified columns.
    'how' can be 'left', 'right', 'inner', or 'outer'.
    """
    merged_df = pd.merge(df1, df2, on=on_columns, how=how)
    return merged_df


# NEW 
# def scale_features(df, feature_cols):
#     """
#     Scale the given feature columns between 0 and 1.
#     Returns the scaled DataFrame and the scaler object.
#     """
#     scaler = MinMaxScaler()
#     df_scaled = df.copy()
#     df_scaled[feature_cols] = scaler.fit_transform(df[feature_cols])
#     return df_scaled, scaler
