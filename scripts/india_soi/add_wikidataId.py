"""
Utility to add wikidataId to City in the AQI dataset

Command to run: python3 add_wikidataId.py --input_dir=./aqi --place_path=./aqi/waqi-places-resolved.csv --skiprows=4 --output_dir=./aqi/resolved_csv
"""

import os
import pandas as pd
from absl import app, flags

_SKIP_LIST = ['airquality-covid19-cities.json', 'waqi-places.csv', 'waqi-places-resolved.csv', 'resolved_csv']

## INPUT FLAGS
FLAGS = flags.FLAGS
flags.DEFINE_string('input_dir', None, 'Path to the input directory with csv files')
flags.DEFINE_string('place_path', './aqi/waqi-places-resolved.csv', 'Path to the csv file which has the resolved places to wikidataId')
flags.DEFINE_integer('skiprows', 4, 'Specify the number of rows to skip while reading the dataset')
flags.DEFINE_string('output_dir', None, 'Path to the input directory with csv files')



def aqi_wikidata_to_cities(input_dir, place_path, skip_list, skip_rows, out_path):
    output_path = os.path.join(out_path, 'resolved_csv')
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    place_df = pd.read_csv(place_path)
    for data_file in os.listdir(input_dir):
        if data_file not in skip_list:
            print(f"processing {data_file} ", end=".......", flush=True)
            file_path = os.path.join(input_dir, data_file)
            data = pd.read_csv(file_path, skiprows=skip_rows)
            start_shape = data.shape[0]
            data = pd.merge(data, place_df, left_on="City", right_on="name", how="left")
            data.drop(columns=['name', 'errors', 'containedIn'], inplace=True)
            assert(start_shape, data.shape[0])
            data.to_csv(os.path.join(output_path, data_file), index=False)
            print("Done.", flush=True)

def main(_) -> None:
  aqi_wikidata_to_cities(input_dir=FLAGS.input_dir, 
  place_path=FLAGS.place_path, 
  skip_list=_SKIP_LIST, 
  skip_rows=FLAGS.skiprows, 
  out_path=FLAGS.output_dir)


if __name__ == '__main__':
  app.run(main)
