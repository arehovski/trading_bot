import numpy as np
from flask import Flask, request
import pandas as pd

from utils import get_active_list

app = Flask(__name__)


@app.route("/")
def home():
    active_list = get_active_list()
    df = pd.DataFrame(active_list)
    df = df.astype({'size': 'int64', 'dailyIntRate': 'float'})
    df_grouped: pd.DataFrame = df.groupby(pd.cut(df["dailyIntRate"], np.arange(0, 0.0015, 0.0001))).sum()[["size"]]
    return df_grouped.to_html()
