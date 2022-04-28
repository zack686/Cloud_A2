import pandas as pd
import json

# Specify file paths
csv_path = 'restaurants_bars.csv'
jsonFilePath = 'aurin.json'

# making data frame from csv file 
data = pd.read_csv(csv_path) 
  
# dropping ALL duplicte values 
print(data.shape)
data.drop_duplicates(subset =["property_id", "trading_name"], inplace = True)
print(data.shape)

# reset index
data = data.reset_index()
data = data.drop(columns=['index'])

# dataframe to dictionary and write to json ('index' to map objects to index, 'records' ro have a list of objects)
dict = data.to_dict('index')
with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
    jsonf.write(json.dumps(dict, indent=4))


