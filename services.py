import base64
import io
import json

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from connections import get_redis_connection, get_margin_api
from utils import get_items_from_paginated_result


def get_active_list_dataset() -> pd.DataFrame:
    redis = get_redis_connection()
    if active_list := redis.get("kucoin:active_list:USDT"):
        active_list = json.loads(active_list)
    else:
        margin = get_margin_api()
        active_list = get_items_from_paginated_result(margin.get_active_list)
        active_list_json = json.dumps(active_list)
        redis.set("kucoin:active_list:USDT", active_list_json, 20)

    df = pd.DataFrame(active_list)
    df = df.astype({"size": "int64", "dailyIntRate": "float", "repaid": "float"})
    df["size"] = df["size"] - df["repaid"].astype("int64")
    return df


def get_plot_image(plot: Figure) -> str:
    output = io.BytesIO()
    plot.savefig(output)
    output.seek(0)
    image = base64.b64encode(b"".join(output))
    image = image.decode("utf-8")
    plt.close(plot)
    return image


def get_active_list_hist(df: pd.DataFrame) -> str:
    df_grouped: pd.DataFrame = df.groupby("dailyIntRate").sum()[["size"]]
    df_grouped.index = df_grouped.index.map(lambda item: round(item * 100, 3))
    plot = df_grouped.plot(kind="bar", figsize=(8, 5)).get_figure()
    plot.tight_layout()
    return get_plot_image(plot)


def get_maturity_date_hist(df: pd.DataFrame) -> str:
    df["maturityTime"] = pd.to_datetime(df["maturityTime"], unit="ms")
    df_grouped: pd.DataFrame = df.groupby(df["maturityTime"].dt.date).sum()[["size"]]
    df_grouped["wavg_rates"] = df.groupby(df["maturityTime"].dt.date).apply(
        lambda item: round(((item["dailyIntRate"] * item["size"]).sum() / item["size"].sum()) * 100, 4)
    )

    figure, ax1 = plt.subplots(figsize=(9, 5))
    color = "tab:blue"
    ax1.set_xlabel("Maturity date")
    ax1.set_ylabel("Size", color=color)
    ax1.bar(df_grouped.index, df_grouped["size"], color=color)
    ax1.tick_params(axis="y", labelcolor=color)

    color = "tab:red"
    ax2 = ax1.twinx()
    ax2.set_ylabel("Weighted av rates", color=color)
    ax2.plot(df_grouped.index, df_grouped["wavg_rates"], color=color)
    ax2.tick_params(axis="y", labelcolor=color)
    figure.tight_layout()

    return get_plot_image(figure)


def get_active_list_info(df: pd.DataFrame) -> dict:
    df_grouped: pd.DataFrame = df.groupby("dailyIntRate").sum()[["size"]]
    df_grouped.reset_index(inplace=True)
    df_grouped["product"] = df_grouped["dailyIntRate"] * df_grouped["size"]
    amount = df_grouped["size"].sum()
    wavg_rate = round((df_grouped["product"].sum() / amount), 6)
    a_day = round(amount * wavg_rate, 2)
    a_week = round(a_day * 7, 2)
    a_month = round(a_day * 30, 2)
    return {
        "amount": amount,
        "wavg_rate": round(wavg_rate * 100, 4),
        "a_day": a_day,
        "a_week": a_week,
        "a_month": a_month,
    }
