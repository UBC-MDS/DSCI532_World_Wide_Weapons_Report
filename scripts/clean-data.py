import pandas as pd

# Make the WorldBank GDP dataset tidy
dirty_df = pd.read_csv("../data/dirty/gdp_1960_2018_worldbank.csv",
                       skiprows = 4)
(dirty_df.melt(id_vars = ['Country Name'],
         value_vars = dirty_df.columns[4:],
         var_name = "Year",
         value_name = "GDP").
    rename(columns = {'Country Name': 'Country'}).
    to_csv("../data/clean/gdp_1960_2018_worldbank.csv"))

# Make the UN Arms and Ammunition dataset tidy
dirty_df = pd.read_csv("../data/dirty/un-arms-and-ammunition_1988-2018.csv")
tidy_df = dirty_df.groupby(['Country or Area', 'Year',
                            'Flow']).agg({'Trade (USD)': sum}).reset_index()
tidy_df['Flow'] = (tidy_df['Flow'].str.replace('Re-Export', 'Export').
                                   str.replace('Re-Import', 'Import'))
tidy_df = tidy_df.rename(columns = {"Trade (USD)": "USD_Value",
                                    "Country or Area": "Country",
                                    "Flow": "Direction"})
tidy_df = tidy_df.groupby(['Country', 'Year', 'Direction']).agg({'USD_Value': sum}).reset_index()
tidy_df.to_csv("../data/clean/un-arms-and-ammunition_1988-2018.csv")

print("Success!")