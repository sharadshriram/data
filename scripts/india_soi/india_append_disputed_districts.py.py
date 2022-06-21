#!/usr/bin/env python
# coding: utf-8

# In[1]:


ind_districts_mcf = "India_districts_geojson.mcf"
jk_districts_mcf = "JK_Districts_GeoJson.mcf"

import json
import pandas as pd


# In[2]:


def get_file_content(fname):
    f = open(fname, 'r')
    data_list = [line.strip() for line in f.readlines()]
    f.close()
    return data_list

def jk_convert_mcf_to_json(mcf_list):
    json_list = []
    json_elem = {}
    
    for line in mcf_list:
        if line == '':
            json_list.append(json_elem)
            json_elem = {}
        else:
            try:
                k, v = line.split(': ')
                if k == 'wikidataId':
                    v = v.replace('"', '')
                json_elem[k] = v
            except ValueError:
                if line.startswith('geoJsonCoordinates'):
                    json_elem['geoJsonCoordinates'] = json.loads(line.split('geoJsonCoordinates: ')[1])
    json_list.append(json_elem)
    return json_list[1:]

def ind_convert_mcf_to_json(mcf_list):
    json_list = []
    json_elem = {}
    for line in mcf_list:
        if line.startswith('Node'):
            json_list.append(json_elem)
            json_elem = {}
        else:
            try:
                k, v = line.split(': ')
                json_elem[k] = v
            except ValueError:
                if line.startswith('geoJsonCoordinates'):
                    json_elem['geoJsonCoordinates'] = json.loads(line.split('geoJsonCoordinates: ')[1])
    json_list.append(json_elem)
    return json_list[1:]


# In[3]:


jk_list = get_file_content(jk_districts_mcf)
jk_json = jk_convert_mcf_to_json(jk_list)
jk_df = pd.DataFrame(jk_json)
del jk_list, jk_json


# In[4]:


ind_list = get_file_content(ind_districts_mcf)
ind_json = ind_convert_mcf_to_json(ind_list)
ind_df = pd.DataFrame(ind_json)
del ind_list, ind_json


# In[21]:


pok = jk_df[jk_df['indianCensusAreaCode2011'] == '""']
pok['Node'] = pok['dcid'].apply(lambda row: "india_place_" + row.replace('"', '').split('/')[1])
pok


# In[19]:


def update_geojson(row, jk_df):
    if row['indianCensusAreaCode2011'] in jk_df['indianCensusAreaCode2011'].values.tolist():
        row['geoJsonCoordinates'] = jk_df.loc[jk_df['indianCensusAreaCode2011'] == row['indianCensusAreaCode2011'], 'geoJsonCoordinates'].values[0]
    return row

updated = ind_df.apply(update_geojson, args=(jk_df,), axis=1)
updated['Node'] = 'india_place_' + updated['indianCensusAreaCode2011'].str.replace('"', '')
updated = updated[['Node', 'typeOf', 'indianCensusAreaCode2011', 'geoJsonCoordinates', 'dcid']]


# In[20]:


updated = updated.append(pok, ignore_index=True)


# In[28]:


f = open("india_district_geojson_jk_updated.mcf", "w")

_MCF_FORMAT = """
Node: {node}
typeOf: {place_type}
indianCensusAreaCode2011: "{indianCensusAreaCode2011}"
geoJsonCoordinates: {gj_str}
dcid: "{dcid}"
"""
def write_to_mcf(row):
        gj = json.dumps(row['geoJsonCoordinates'])
        f.write(
            _MCF_FORMAT.format(node=row['Node'],
                               place_type=row['typeOf'],
                               indianCensusAreaCode2011=row['indianCensusAreaCode2011'],
                               gj_str=gj,
                               dcid=row['dcid']
                              ))

updated.apply(write_to_mcf, axis=1)
f.close()


# In[ ]:




