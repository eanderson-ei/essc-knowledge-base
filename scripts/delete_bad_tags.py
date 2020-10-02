import pandas as pd
from graph_database import delete_bad_tags

df = pd.read_csv('data/bad_tags.csv')

bad_kws = df['bad_kw'].to_list()

print(bad_kws)

delete_bad_tags(bad_kws)