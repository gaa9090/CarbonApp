import pandas as pd
import random
YEARS = 50
SECTORS = ("waste_percent", "transportation_percent", "energy_percent")

def generate_fake_emissions_correlation(years, sectors):
    
    df = pd.DataFrame()
    df['Year'] = range(2023 - years + 1, 2023 + 1)
    df.at[0, "waste_percent"] = 190234
    df.at[0, "transportation_percent"] = 254245
    df.at[0, "energy_percent"] = 543245

    for x in range(1, years):
        change = random.randint(-2, 8) / 1000
        df['waste_percent'][x] = df['waste_percent'][x] * (1 + change)

    
    

    # print(df)

def generate_fake_emissions(years, sectors):
    df = pd.DataFrame()
    df['Year'] = range(2023 - years + 1, 2023 + 1)

    for sector in sectors:
        start_emissions = random.randint(1000000, 5000000) 
        emissions = [start_emissions] 

        for _ in range(1, years):
            change_percent = random.uniform(0, 8) 
            current_emissions = emissions[-1] * (1 + change_percent / 1000)  
            emissions.append(current_emissions)  

        df[sector] = emissions

    df['Year'] = range(2023 - years + 1, 2023 + 1)
    df['total_emissions'] = df[['waste_percent', 'transportation_percent', 'energy_percent']].sum(axis=1)

    return df

def website_format(df):
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

def program_format(df):
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


if __name__ == "__main__":
    pass
    fake_emissions = pd.read_csv("example_io/website_format2.csv")
    print(fake_emissions)
    fake_emissions = website_format(fake_emissions)
    print(fake_emissions)
    fake_emissions.to_csv("example_io/website_format1.csv", index=False)

    # restructured_emissions = restructure_data(fake_emissions)
    # derestructured_emissions = destructure_data(restructured_emissions)
    # # generate_fake_emissions_correlation(YEARS, SECTORS)

    # print(f"fake emissions: {fake_emissions}")
    # print(f"restructured: {restructured_emissions}")
    # print(f"derestructured: {derestructured_emissions}")
