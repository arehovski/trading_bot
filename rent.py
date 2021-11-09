import os

from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By

from celery_app import celery_app
from config import BASE_DIR, MAIL_ADDRESS
from connections import get_redis_connection
from utils import send_mail


def rent(url):
    logger.debug("Starting parse onliner")
    redis = get_redis_connection()
    key = "onliner:viewed_ads"
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options, executable_path=os.path.join(BASE_DIR, 'geckodriver'))

    try:
        driver.get(url)
        items = driver.find_elements(by=By.XPATH, value="//a[@class='classified']")
        links = [item.get_attribute("href") for item in items]
        links = set(links)
        new_links = list(filter(lambda link: link not in redis.smembers(key), links))
        if new_links:
            redis.sadd(key, *new_links)
            send_mail((MAIL_ADDRESS, "handyshopetsy@gmail.com"), "\n".join(new_links), subject="Onliner new rent ads")
    except Exception as e:
        send_mail(MAIL_ADDRESS, f"Failed to get new ads {e}", subject="Onliner new rent ads")
    finally:
        driver.quit()


@celery_app.task
def new_ads():
    url = "https://r.onliner.by/ak/?rent_type%5B%5D=2_rooms&rent_type%5B%5D=3_rooms&price%5Bmin%5D=260&price%5Bmax%5D=440&currency=usd&only_owner=true#bounds%5Blb%5D%5Blat%5D=53.76393350751146&bounds%5Blb%5D%5Blong%5D=27.325158042712275&bounds%5Brt%5D%5Blat%5D=54.03231909735282&bounds%5Brt%5D%5Blong%5D=27.799779191799345&order=created_at:desc"
    rent(url)


@celery_app.task
def upped_ads():
    url = "https://r.onliner.by/ak/?rent_type%5B%5D=2_rooms&rent_type%5B%5D=3_rooms&price%5Bmin%5D=260&price%5Bmax%5D=440&currency=usd&only_owner=true#bounds%5Blb%5D%5Blat%5D=53.76393350751146&bounds%5Blb%5D%5Blong%5D=27.325158042712275&bounds%5Brt%5D%5Blat%5D=54.03231909735282&bounds%5Brt%5D%5Blong%5D=27.799779191799345"
    rent(url)
