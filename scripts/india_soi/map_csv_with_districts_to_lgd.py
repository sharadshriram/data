"""Utility to map the district name to the place dcid from LGD code


"""

import os
import sys

import pandas as pd
from absl import app, flags

from districts import IndiaDistrictsMapper

## INPUT FLAGS
FLAGS = flags.FLAGS
flags.DEFINE_string('csv_in', None, 'Path to the input csv file')
flags.DEFINE_string('csv_out', None, 'Path to the output csv file')
flags.DEFINE_string('transpose', 'n', 'Flag to set if the input file needs to be toggled such that rows contain district data and columns are StatVars. To transpose, set flag as "y" (default:n)')
flags.DEFINE_string('header', 'y', 'Flag to set if the input file has a header row or not. Set "n" if no header rows are present (default:y)')
flags.DEFINE_string('state', None, 'Specify the column in the input csv file where the state name is present. Column can be specified either by name or by id (0-indexed), if the dataset does not have a state column, you specify the name of the state in uppercase.')
flags.DEFINE_string('district', None, 'Sepcify the column in the input csv file where the district name is present. Column can be specified either by name or by id (0-indexed), if the dataset does not have district name specified, you can specify the name of the district')

def get_column_index(df_columns:pd.Index, place:str)->int:
  """
  Utility function to return the index of the column based on the value of the state

  Args:
    - df_columns: list of columns of the pandas dataframe
    - place: string with the column name or column index. If neither is satified
      the function returns None
  """
  # check for numeric value -- index specification of column
  if place.isdecimal():
    if int(place) <= len(df_columns.to_list()):
      return int(place)
  # check if column name exists in the dataframe
  else:
    try:
      return df_columns.get_loc(place)
    except:
      return None

def get_lgd_code(row):
  # Get the lgd codes from Thej's mapper tool
  mapper = IndiaDistrictsMapper()
  try:
    return mapper.get_district_name_to_lgd_code_mapping(row['state'], row['district'])
  except:
    return ''

def map_lgd_districts_to_wikidataId(row):
  wikidata_df = pd.read_csv('districts_local_directory.csv')
  if (row['district_code'] is not None) and (len(row['district_code']) > 0):
    wikidata_id = wikidata_df[wikidata_df['DistrictCode'] == float(row['district_code'])]['wikidataId'].values[0]
    return 'wikidataId/' + wikidata_id
  else:
    return ''

def process_csv(input_path:str, transpose:str, header:str, state:str, district:str, output_path:str)->None:
  """
  Function to process input csv file and map districts to LGD codes

  Args:
    - input_path:str -
    - transpose:str -
    - header:str -
    - state:str -
    - district:str -
    - output_path:str -
  """
  data = None
  # header flag based file-read
  if header == 'n':
    data = pd.read_csv(input_path, header=None)
  else:
    data = pd.read_csv(input_path)

  if transpose == 'y':
    data = data.transpose()

  # find the state column by name or index
  st_column_idx = get_column_index(data.columns, state)
  if st_column_idx is None:
    data['state'] = state
  else:
    data.columns.values[st_column_idx] = 'state'

  # find the district column by name or index
  dt_column_idx = get_column_index(data.columns, district)
  if dt_column_idx is None:
    data['district'] = district
  else:
    data.rename(columns={data.columns[dt_column_idx]: 'district'}, inplace=True)
	
  # map district names to LGD codes
  places_df = data[['state', 'district']].drop_duplicates().dropna()
  places_df['district_code'] = places_df.apply(get_lgd_code,axis=1)

  places_df['wikidataId'] = places_df.apply(map_lgd_districts_to_wikidataId, axis=1)
  places_df.drop('state', axis=1, inplace=True)

  # merge LGD codes with data
  data = data.merge(places_df, on='district', how='left')

  # add the file as resolved.csv - it will have the 
  data.to_csv(output_path, index=False)

def main(_) -> None:
  process_csv(FLAGS.csv_in, FLAGS.transpose, FLAGS.header, FLAGS.state, FLAGS.district, FLAGS.csv_out)

### add the city name -> wikidataId
### based on gs://unresolved_mcf/karnataka_gov_poc/data/aqi/waqi-places-resolved.csv


if __name__ == '__main__':
  app.run(main)
