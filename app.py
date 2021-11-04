from flask import Flask, render_template, request, redirect

from connections import get_redis_connection
from services import get_active_list_dataset, get_active_list_hist, get_active_list_info, get_maturity_date_hist


app = Flask(__name__)
redis = get_redis_connection()


@app.route("/")
def home():
    df = get_active_list_dataset()
    active_list_distr_image = get_active_list_hist(df)
    maturity_date_image = get_maturity_date_hist(df)
    kwargs = get_active_list_info(df)
    balance_reserve = redis.get("kucoin:balance_reserve:USDT")
    lend_order_quantity = redis.get("kucoin:lend_order_quantity:USDT")
    min_daily_rate = redis.get("kucoin:min_daily_rate:USDT")
    kwargs.update({
        'active_list_distr_image': active_list_distr_image,
        'maturity_date_image': maturity_date_image,
        'balance_reserve': balance_reserve,
        'lend_order_quantity': lend_order_quantity,
        'min_daily_rate': min_daily_rate
    })
    return render_template("plot.html", **kwargs)


@app.route("/bot_options", methods=["POST"])
def bot_options():
    balance_reserve = request.form.get('balance_reserve')
    lend_order_quantity = request.form.get('lend_order_quantity')
    min_daily_rate = request.form.get('min_daily_rate')
    redis.set("kucoin:balance_reserve:USDT", balance_reserve)
    redis.set("kucoin:lend_order_quantity:USDT", lend_order_quantity)
    redis.set("kucoin:min_daily_rate:USDT", min_daily_rate)
    return redirect('/')
