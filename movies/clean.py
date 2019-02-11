from collections import defaultdict

import pandas as pd
import json
import numpy as np
import datetime as dt
from pathlib import Path
ROOT = Path(__file__).parent
TODAY= dt.datetime.today()
NOW = dt.datetime.now()
output_filename = f"clean_{TODAY.year}{TODAY.month:02d}{TODAY.day:02d}_{NOW.hour:02d}"
outfile = (ROOT / 'data' /  output_filename).with_suffix('.csv')

train = pd.read_csv('data/train.csv', index_col=0)
test = pd.read_csv('data/test.csv', index_col=0)
df = train.append(test, ignore_index=True, sort=False)
df.drop(columns=['homepage', 'overview', 'poster_path', 'tagline'], inplace=True, errors='ignore')

##### Flatening Json columns
def get_dictionary(s):
    try:
        d = eval(s)
    except:
        d = {}
    return d


def split_columns(col_series):
    temp_df = col_series.map(lambda x: dict.fromkeys(x.split(','), 1)).apply(pd.Series)
    temp_df.drop(columns=[''], inplace=True, errors='ignore')
    temp_df[~temp_df.isnull()] = True
    temp_df[temp_df.isnull()] = False
    return temp_df


df.belongs_to_collection = df.belongs_to_collection.map(lambda x: len(get_dictionary(x))).clip(0, 1)
df.genres = df.genres.map(lambda x: sorted([d['name'] for d in get_dictionary(x)])).map(lambda y: ','.join(map(str, y)))
df.production_companies = df.production_companies.map(lambda x: [d['name'] for d in get_dictionary(x)]).map(
    lambda x: ','.join(map(str, x)))
df.production_countries = df.production_countries.map(lambda x: [d['name'] for d in get_dictionary(x)]).map(
    lambda x: ','.join(map(str, x)))
df.spoken_languages = df.spoken_languages.map(lambda x: [d['name'] for d in get_dictionary(x)]).map(
    lambda x: ','.join(map(str, x)))
df.Keywords = df.Keywords.map(lambda x: [d['name'] for d in get_dictionary(x)]).map(lambda x: ','.join(map(str, x)))

#My Approach
# Well there is some of these with 4 digit years so let's deal with those
#Since only last two digits of year are provided, this is the correct way of getting the year.
release_dt=\
    df['release_date'].str.split('/',expand=True).replace(np.nan, -1).astype(int)
release_dt.rename(columns={0:'month',1:'day',2:'year'},inplace=True)
# Deal with 4 digit release dates
# If the date is already 4 digits (i.e. > 1000)- then just return it, else assume anything between 0 and 18 is 20xx
release_dt.year = release_dt.year.apply(lambda x: x if x > 1000 else x + (2000 if (x <= 18) else 1900))

release_dt['release_dt'] = pd.to_datetime(release_dt, errors="coerce")
release_dt.rename(columns={'month':"release_month","day":"release_day","year":"release_year"},
                  inplace=True)
release_dt['release_dow']=release_dt['release_dt'].dt.dayofweek
df = pd.concat([df, release_dt],axis=1, sort=False)
df.drop(columns={'release_date'},inplace=True)

# Genres ****
genres = df.genres.str.get_dummies(sep=',')
df = pd.concat([df, genres], axis=1, sort=False)
df.drop(columns=['genres'], inplace=True)

# Spoken Languages ****
spoken_languages = df.spoken_languages.str.get_dummies(sep=',')
spoken_languages.rename(columns={'العربية':'Arabic',
                                 'हिन्दी':'Hindi',
                                 '广州话 / 廣州話':'Guangzhou',
                                 '日本語':'Japanese',
                                 '普通话': 'Mandarin',
                                 '한국어/조선말':'Korean',
                                 'Pусский':'Russian',
                                 'Español':'Spanish',
                                 'Français':'French',
                                 'Italiano':'Italian',
                                 'Português':'Portuguese',
                                 'Deutsch':'German'
                                 }, inplace=True
                        )
total_records = len(df)
keepers = langs_to_keep = []
for x in spoken_languages.columns:
    records = spoken_languages[x].sum() / total_records
    if records > .01:
        keepers.append((x,records))
        langs_to_keep.append(x)
languages_to_drop = set(spoken_languages.columns)-set(langs_to_keep)
spoken_languages['Other_Languages'] = 0
for langs in languages_to_drop:
    spoken_languages['Other_Languages'] += spoken_languages[langs]
spoken_languages['Spoken_Lang_Other'] = (spoken_languages['Other_Languages'] > 0)*1
spoken_languages.drop(columns=['Other_Languages'],inplace=True)
spoken_languages.drop(columns=languages_to_drop,inplace=True)
df.drop(columns=['spoken_languages',],inplace=True)
df = pd.concat([df,spoken_languages], axis=1, sort=False)

# Production Countries ****
prod_countries = df['production_countries'].str.get_dummies(sep=',')
df = pd.concat([df, prod_countries], axis=1, sort=False)
df.drop(columns=['production_countries'], inplace=True)

df.to_csv(outfile,index_label='id')
df.to_csv(ROOT / 'data/clean.csv',index_label='id')
