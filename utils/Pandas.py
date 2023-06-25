import json

import pandas as pd


def filter_df(df, cln, val): return df.loc[df[cln] == val]


pluck_row = lambda row, *clns: [row[cln].iloc[0] for cln in clns]
drop_cols = lambda df, *clns: df.drop(list(clns), axis=True, inplace=True)
def num_col(col): return pd.to_numeric(col)
def to_date(col): return pd.to_datetime(col, unit='ms')


def unique_indexes(df): return df.index.unique()


def unique_columns(df): return df.nunique()


def latest_date(df): return str(df['date'].iloc[-1])
def latest_time(df): return str(df.index[-1])


def set_element(df, index, cln, val):
    df.loc[index, cln] = val
    return


def jsonify(df: pd.DataFrame) -> str:
    dict_df = df.to_dict(orient='records')
    json_dump = json.dumps(dict_df)
    return json_dump
