from flask import Flask, render_template

from services import get_active_list_dataset, get_active_list_hist, get_active_list_info, get_maturity_date_hist

app = Flask(__name__)


@app.route("/")
def home():
    df = get_active_list_dataset()
    active_list_distr_image = get_active_list_hist(df)
    maturity_date_image = get_maturity_date_hist(df)
    kwargs = get_active_list_info(df)
    return render_template(
        "plot.html", active_list_distr_image=active_list_distr_image, maturity_date_image=maturity_date_image, **kwargs
    )
