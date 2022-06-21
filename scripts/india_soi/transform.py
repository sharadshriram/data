import pandas as pd

def tr(r):
	r[r['StatVar']] = r['Value']
	return r
df = pd.read_csv('cleaned.csv')
new_columns = list(df['StatVar'].unique())
# df = df.reindex(columns=new_columns)
df = pd.concat([df, pd.DataFrame(columns=new_columns)])

df = df.apply(tr, axis=1)
df.drop('StatVar', axis=1, inplace=True)
df.drop('Value', axis=1, inplace=True)
df.to_csv('src_data.csv', index=False)

s = ''
for i, stat_var in enumerate(new_columns):
	s += f"""Node: E:src_data->E{i}
typeOf: dcs:StatVarObservation
variableMeasured: dcs:{stat_var}
observationDate: C:src_data->Date
observationAbout: C:src_data->Place
observationPeriod: C:src_data->Period
value: C:src_data->{stat_var}
unit: C:src_data->Unit

"""

with open('output.tmcf', 'w') as fp:
	fp.write(s)
