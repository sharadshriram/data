
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
    'orig_file', '', ''
)
flags.DEFINE_string(
    'simplified_file', '', ''
)

def check(orig_file, simplified_file):
    diff_file = open("diff_file.txt", "w")
    simplified_file_lines = open(simplified_file).readlines()
    simplified_file_dcids = set()
    for line in simplified_file_lines:
        if line.startswith("dcid:"):
            simplified_file_dcids.add(line)
    orig_file_lines = open(orig_file).readlines()
    for line in orig_file_lines:
        if line.startswith("dcid:") and not line in simplified_file_dcids:
            diff_file.writelines(line)

    

def main(_):
    check(FLAGS.orig_file, FLAGS.simplified_file)


if __name__ == '__main__':
    app.run(main)