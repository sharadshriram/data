
# Copyright 2021 Google LLC
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
import geopandas as gpd
import glob
import io
import json
import numpy as np
import os
import pandas as pd
import requests
import tempfile
import zipfile

from absl import app
from absl import flags

EPS_LEVEL_MAP = {0.01: 1, 0.03: 2, 0.05: 3}

FLAGS = flags.FLAGS
flags.DEFINE_string(
    'input_file', '', ''
)

def generate_simplified_mcf(input_file):
    mcf_file = open(input_file)
    mcf_file_lines = mcf_file.readlines()
    simplified_files = {}
    for _, dp_level in EPS_LEVEL_MAP.items():
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
            for threshold, display_level in EPS_LEVEL_MAP.items():
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

def main(_):
    generate_simplified_mcf(FLAGS.input_file)


if __name__ == '__main__':
    app.run(main)