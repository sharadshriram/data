# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Utility to generate the Indian geojson mcf files based on the maps from the Survey of India (SoI) website
"""
import os
import sys
import json
import pandas as pd
import geopandas as gpd
from absl import app, flags

# Allows the following module imports to work when running as a script
_SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(_SCRIPT_PATH, '../../'))  # to india root

from india.geo.states import IndiaStatesMapper
from india.formatters import CodeFormatter

# Note1: When we emit geojson string, we use two json.dumps() so it
# automatically escapes all inner quotes, and encloses the entire string in
# quotes.
# Note2: Having the appropriate type helps downstream consumers of this data
#        (e.g., IPCC pipeline).
_MCF_FORMAT = """
Node: india_place_{ext_id}
typeOf: dcs:{place_type}
{ext_id_prop}: "{ext_id}"
geoJsonCoordinates: {gj_str}
"""
_EPS_LEVEL_MAP = {0.01: 1, 0.03: 2, 0.05: 3}

_LGD_PATH = os.path.join(_SCRIPT_PATH, "../geo/LocalGovernmentDirectory_Districts.csv")

def fix_the_bad_letters(w:str)->str:
    """
    The shapefile has a few characters decoded incorrectly, which is fixed by this method.
    """
    if '|' in w:
        w = w.replace('|', 'I')
    if '>' in w:
        w = w.replace('>', 'A')
    if '@' in w:
        w = w.replace('@', 'U')
    return w

def fix_dist_st_names(row:pd.Series)->pd.Series:
    """
    Wrapper function for fix_the_bad_letters
    """
    row['STATE'] = fix_the_bad_letters(row['STATE'])
    row['District'] = fix_the_bad_letters(row['District'])
    return row

def generate_simplified_mcf(input_file:str)->None:
    """
    Method to generate simplified geojson mcfs for a given input geojson mcf file
    This module is from @chejennifer's branch
    """
    mcf_file = open(input_file)
    mcf_file_lines = mcf_file.readlines()
    simplified_files = {}
    for _, dp_level in _EPS_LEVEL_MAP.items():
        file_name = f'{input_file[:-4]}_dp{dp_level}.mcf'
        print(file_name)
        dp_level_file = open(f"{input_file[:-4]}_dp{dp_level}.mcf", "w")
        simplified_files[dp_level] = dp_level_file
    geoJsonCoordinates = ''
    for line in mcf_file_lines:
        if line.startswith("geoJsonCoordinates"):
            geoJsonCoordinates += line
            continue
        if line == '\n' and len(geoJsonCoordinates) > 0:
            geoJsonCoordinates = geoJsonCoordinates[len('geoJsonCoordinates: '):]
            geoJsonObject = json.loads(geoJsonCoordinates)
            gdf = gpd.read_file(geoJsonObject)
            for threshold, display_level in _EPS_LEVEL_MAP.items():
                simplified_series = gdf.simplify(threshold)
                simplified_geojson = json.loads(simplified_series.to_json())
                simplified_geojson_features = simplified_geojson.get("features", [])
                if len(simplified_geojson_features) > 0:
                    simplified_geo = simplified_geojson_features[0].get("geometry", {})
                    prop = f"geoJsonCoordinatesDP{display_level}: "
                    value = json.dumps(simplified_geo).replace('"', '\\\"')
                    simplified_files.get(display_level).writelines(prop + f'"{value}"' + "\n")
            geoJsonCoordinates = ''
        for _, simplified_file in simplified_files.items():
            simplified_file.writelines(line)


def generate_districts(gdf:gpd.GeoDataFrame, output_path:str)->None:
	"""
	
	"""
	lgd = pd.read_csv(_LGD_PATH, usecols=['LGDDistrictCode', 'census2011Code', 'WikiDataId'], dtype = {'LGDDistrictCode': str})
	gdf = gdf.apply(fix_dist_st_names, axis=1)
	
	# fix the representation of district LGD codes for convenient merge with LGD District dataset
	gdf['DISTRICT_L'] = gdf['DISTRICT_L'].apply(lambda x: '{0:0>3}'.format(x))
	
	geo_df = pd.DataFrame(gdf)

	# merge the shapefile with LGD District dataset to append wikidataId
	geo_df = pd.merge(geo_df, lgd, left_on='DISTRICT_L', right_on='LGDDistrictCode', how='left')

	# manually add the missing wikidataId
	geo_df.loc[geo_df['District'] == 'MIRPUR', 'WikiDataId'] = 'Q2571434'
	geo_df.loc[geo_df['District'] == 'MUZAFFARABAD', 'WikiDataId'] = 'Q461307'

	# there are 11 district boundaries that are disputed between states but they have been added in atleast on of the disputing states, implying we do not miss the polygon for the disputed district boundaries and hence we drop all rows that contain the term 'Disputed'
	geo_df = geo_df[~geo_df['District'].str.contains('DISPUTED')]

	# convert back to geoDataFrame and dump to geoJSON
	gdf = gpd.GeoDataFrame(geo_df)
	del geo_df
	
	#TODO: a new function from the df
    j = json.load(fin)
    for f in j['features']:
        if ('properties' not in f or 'censuscode' not in f['properties'] or
                'geometry' not in f):
            continue
        census2011 = str(f['properties']['censuscode'])
        census2011 = CodeFormatter.format_census2011_code(census2011)
        gj = json.dumps(json.dumps(f['geometry']))
        fout.write(
            _MCF_FORMAT.format(ext_id=census2011,
                               place_type='AdministrativeArea2',
                               ext_id_prop='indianCensusAreaCode2011',
                               gj_str=gj))

#TODO: a new function from the df and 
def generate_states():
	    j = json.load(fin)
    for f in j['features']:
        if ('properties' not in f or 'ST_NM' not in f['properties'] or
                'geometry' not in f):
            continue
        iso = IndiaStatesMapper.get_state_name_to_iso_code_mapping(
            f['properties']['ST_NM'])
        gj = json.dumps(json.dumps(f['geometry']))
        fout.write(
            _MCF_FORMAT.format(ext_id=iso,
                               place_type='AdministrativeArea1',
                               ext_id_prop='isoCode',
                               gj_str=gj))



def main(_):
		FLAGS = flags.FLAGS

		flags.DEFINE_string('input_state_geojson', '',
				                'Path to the India State geojson file.')
		flags.DEFINE_string('input_district_geojson', '',
				                'Path to the India District geojson file.')
		flags.DEFINE_string('output_geojson_dir', '/tmp', 'Output directory path.')

	# path to the .shp file
	gdf = gpd.read_file(input_file)
	
	if option == 'st':
		generate_states(gdf)
	
	if option == 'dist':
		generate_districts(gdf)




    generate(FLAGS.input_state_geojson, FLAGS.input_district_geojson,
             FLAGS.output_geojson_dir)


if __name__ == "__main__":
    app.run(main)

