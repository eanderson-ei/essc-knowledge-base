"""converts csv of tags to jsonl (new line delimitted json file)
when an alternative is supplied and adds custom tags"""

import json
import pandas as pd

output_path = 'data/entity-patterns.jsonl'

def create_pattern_from_df(output_path, df, in_row_id, out_row_id, label, append=False):
    """
    Write list of objects to JSON newline file
    https://medium.com/@galea/how-to-love-jsonl-using-json-line-format-in-your-workflow-b6884f65175b
    """    
    mode = 'a+' if append else 'w'
    with open(output_path, mode, encoding='utf-8') as f:
        for _, row in df.iterrows():
            words = row[in_row_id].lower().split()
            pattern = []
            for word in words:
                pattern_string = {"LOWER": word}
                pattern.append(pattern_string)
            entity_pattern = {"label": label, "pattern": pattern, "id": row[out_row_id]}
            entity_pattern = json.dumps(entity_pattern)
            f.write(entity_pattern + '\n')  

# from auto-generated tags
df = pd.read_csv('outputs/top_tags_1.csv')
df.dropna(axis=0, subset=['alt'], inplace=True)
df = df[df['alt'] != 'DELETE']

create_pattern_from_df(output_path, df, 0, 2, "ALT", True) 

# # from custom tags
# sf = pd.read_csv('data/custom_tags.csv')

# create_pattern_from_df(output_path, sf, 0, 0, "CUSTOM", True)
