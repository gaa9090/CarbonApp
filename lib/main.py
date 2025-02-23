from .generate_fake_data import generate_fake_emissions, generate_fake_emissions_correlation, website_format, program_format
import pandas as pd
# from plot_data import plot_data
from ._model_training import ModelTraining
from .plot_data import plot_data
import warnings
import uuid
# import os
# from generate_fake_data import website_format, program_format

# os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

YEARS = 20
SECTORS = ("waste_percent", "transportation_percent", "energy_percent")


class root:
    def __init__(self, path, start_year, years):
        # self.df = generate_fake_emissions(40, ('waste_percent', 'transportation_percent', 'energy_percent'))
        self.df = pd.read_csv(path)
        print(self.df)
        self.df = self.df.rename(columns={'Category': 'sector'})
        print(self.df)
        self.df = program_format(self.df)

        print(self.df)
        # print(f"pre change: {self.df}")
        # # self.df = self.program_format(self.df)
        # print(f"post change: {self.df}")

        self.start_year = start_year
        
        # self.df = generate_fake_emissions_correlation(YEARS, SECTORS)
        self.mod_train = ModelTraining(self.df, start_year)

        self.df = self.mod_train.df.drop_duplicates()
        self.df = self.df.fillna(method='ffill')

        # self.df = self.program_format(self.df)
        
        self.model, self.X_test, self.y_test, self.scaler = self.mod_train.train_model_lstm(self.df)
        
        self.last_hist_year = start_year
        self.end_year = start_year + years

    def generate_outcome_helper(self):
        dic = {}
        increment = 0
        for x in list(tuple(self.df.columns[1:-1])):
            dic[x] = increment
            increment += 1
        return dic

    def generate_outcomes(self):

        # keeping this here so someone can see the beauty of what i had to go through to do this 

        # feature_cols = ['transportation_percent', 'energy_percent', 'waste_percent']
        # print(f"indexing columns: {list(tuple(self.df.columns[1:-1]))}, Type: {type(list(tuple(self.df.columns[1:-1])))}")
        # print(f"feature columns: {feature_cols}, Type: {type(feature_cols)}")
        feature_cols = list(tuple(self.df.columns[1:-1]))
        # target_col = self.df.columns[-1]
        target_col = self.df.columns[-1]
        
        # print(f"{self.df.columns[-1]} {type(str(self.df.columns))}")
        # print(f"{target_col} {type(target_col)}")
        # print('total_emissions' == str(self.df.columns[-1]))
        
        df_scaled, _ = self.mod_train.scale_features(self.df, feature_cols, target_col)
        
        self.bau_df = self.mod_train.forecast_future(
            model=self.model,
            df=df_scaled,
            start_year=self.last_hist_year,
            end_year=self.end_year,
            feature_cols=feature_cols,
            target_col=target_col,
            scenario='business_as_usual',
            slope_per_year=None  
        )
        
        self.optim_df = self.mod_train.forecast_future(
            model=self.model,
            df=df_scaled,
            start_year=self.last_hist_year,
            end_year=self.end_year,
            feature_cols=feature_cols,
            target_col=target_col,
            scenario='optim_reduction',
            slope_per_year=1,
            # sector_indices={'col1': 0, 'col2': 1, 'col3': 2, ..... , 'coln': n + 1}
            sector_indices = self.generate_outcome_helper()
        )
        
        all_cols = feature_cols + [target_col]
        scaled_bau = self.bau_df[all_cols].values
        original_bau = self.scaler.inverse_transform(scaled_bau)
        self.bau_df[all_cols] = original_bau

        scaled_optim = self.optim_df[all_cols].values
        original_optim = self.scaler.inverse_transform(scaled_optim)
        self.optim_df[all_cols] = original_optim
    
        return self.bau_df, self.optim_df

    def website_format(self, df):
    # Melt the DataFrame
        long_df = pd.melt(
        df,
        id_vars=['Year'],  # Columns to keep as identifiers
        value_vars=[col for col in df.columns if col not in ['total_emissions', 'Year']],  # Columns to unpivot (excluding 'Year')
        var_name='sector',  # Name for the new sector column
        value_name='emissions'  # Name for the new emissions column
    )
    
        # Sort the melted DataFrame by 'Year' and 'sector'
        sorted_df = long_df.sort_values(by=['Year', 'sector'], ascending=[True, True])
        return sorted_df

    def program_format(self, df):
        # Pivot the DataFrame back to wide format
        df.rename(columns={'Category': 'sector'}, inplace=True)
        
        print(df)
        wide_df = df.pivot(
            index='Year',  # Use 'Year' as the index
            columns='sector',  # Use 'sector' as the columns
            values='emissions'  # Use 'emissions' as the values
        )
        
        # Reset the index to make 'Year' a column again
        wide_df = wide_df.reset_index()
        
        # Rename columns to match the original format
        wide_df.columns.name = None  # Remove the 'sector' label from the columns
        
        # Dynamically calculate the 'total_emissions' column by summing all sector columns
        sector_columns = [col for col in wide_df.columns if col != 'Year']  # Exclude 'Year'
        wide_df['total_emissions'] = wide_df[sector_columns].sum(axis=1)
        
        return wide_df

    # def program_format(self, df):
    #     # Pivot the DataFrame
    #     # self.df = self.mod_train.df.drop_duplicates()
    #     wide_df = df.pivot(
    #         index='Year',  # Rows are indexed by 'Year'
    #         columns='sector',  # Columns are the unique values of 'sector'
    #         values='emissions'  # Values are the 'emissions'
    #     )
        
    #     # Reset the index to make 'Year' a column again
    #     wide_df = wide_df.reset_index()
        
    #     # Sort the DataFrame by 'Year' in ascending order
    #     wide_df = wide_df.sort_values(by='Year', ascending=True)
    #     wide_df['total_emissions'] = wide_df[['waste_percent', 'transportation_percent', 'energy_percent']].sum(axis=1)
    #     cols = list(wide_df.columns)
    #     cols[1], cols[3] = cols[3], cols[1]
    #     wide_df = wide_df[cols]
    #     return wide_df

    def generate_predictions(self):
        file_name_csv_file = None
        bau_df, optim_df = self.generate_outcomes()
        bau_future = bau_df[bau_df['Year'] > self.last_hist_year].copy()
        optim_future = optim_df[optim_df['Year'] > self.last_hist_year].copy()
        
        print("BAU Forecast:")
        print(bau_future.tail())
        print("Optimized Forecast:")
        print(optim_future.tail())
        
        # bau_df = self.website_format(bau_df)
        bau_df.rename(columns={'sector': 'Category'}, inplace=True)
        bau_df.to_csv("lib/output/bau.csv", index=False)
        # optim_df = self.website_format(optim_df)
        optim_df.rename(columns={'sector': 'Category'}, inplace=True)
        optim_df.to_csv("lib/output/optim.csv", index=False)

        merged_inner = pd.merge(bau_df, optim_df, on='Year')
        
        print(f"merged: {merged_inner}")
        
        _merged_inner = website_format(merged_inner)
        
        file_name_csv_file_1 = str(uuid.uuid4())[:8].replace('-', '').upper() + 'optim.csv'
        optim_df.to_csv("lib/output/"+file_name_csv_file_1, index=False)
        
        # plotter = plot_data(
        #     historical_df=self.df,  
        #     bau_df=optim_df,
        #     optim_df=bau_df,
        #     last_hist_year=self.last_hist_year
        # )
        # plotter.plot()

        
        # return plotter

        # plotter = plot_data(
        #     historical_df=self.df,  
        #     bau_df=bau_df,
        #     optim_df=optim_df,
        #     last_hist_year=self.last_hist_year
        # )
        return file_name_csv_file_1
        

# if __name__ == "__main__":
#     app = root("generated_csv/GeneratedExampleCSV.csv", 2024)
#     app.generate_predictions()

