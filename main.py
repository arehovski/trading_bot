import os
import time
from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN
from functools import partial

from loguru import logger
from kucoin.client import Margin, User
from redis import Redis

from config import API_KEY, API_SECRET, API_PASSPHRASE, BASE_DIR, LOGGING_LEVEL
from connections import get_redis_connection
from utils import get_items_from_paginated_result


logger.add(sink=os.path.join(BASE_DIR, 'logs', "kucoin_lend.log"), level=LOGGING_LEVEL, rotation="5 MB")


@dataclass
class LendHandler:
    margin_api: Margin = Margin(key=API_KEY, secret=API_SECRET, passphrase=API_PASSPHRASE)
    user_api: User = User(key=API_KEY, secret=API_SECRET, passphrase=API_PASSPHRASE)
    term: int = 7
    currency: str = "USDT"
    account_type: str = "main"
    redis: Redis = get_redis_connection()

    def get_lend_daily_rate(self) -> Decimal:
        market = self.margin_api.get_lending_market(self.currency, self.term)
        best = market[0]
        rate = Decimal(best.get("dailyIntRate"))
        return rate - Decimal("0.00001")

    def is_in_orders(self, balance: dict) -> bool:
        in_orders = Decimal(balance["holds"])
        return in_orders > 0

    def cancel_active_orders(self) -> None:
        orders = get_items_from_paginated_result(partial(self.margin_api.get_active_order, currency=self.currency))
        orders_ids = [order["orderId"] for order in orders]
        for order_id in orders_ids:
            try:
                self.margin_api.cancel_lend_order(order_id)
                logger.info(f"Order {order_id} cancelled.")
            except Exception as e:
                logger.error(f"Cannot cancel {order_id=}: {e}")

    def get_order_sizes(self, available_balance: Decimal, lend_order_quantity: Decimal) -> tuple[str]:
        orders_count = int(available_balance // lend_order_quantity)
        order_sizes = (lend_order_quantity,) * orders_count + (available_balance - orders_count * lend_order_quantity,)
        order_sizes = tuple(map(str, order_sizes))
        logger.debug(f"{available_balance=}; {order_sizes=}")
        return order_sizes

    def process_currency_lending(self) -> None:
        balance_reserve = Decimal(self.redis.get(f"kucoin:balance_reserve:{self.currency}") or 0)
        lend_order_quantity = Decimal(self.redis.get(f"kucoin:lend_order_quantity:{self.currency}") or 500)
        min_daily_rate = Decimal(self.redis.get(f"kucoin:min_daily_rate:{self.currency}") or "0.0005")
        logger.debug(f"{balance_reserve=}; {lend_order_quantity=}; {min_daily_rate=}")

        balances: list[dict] = self.user_api.get_account_list(self.currency, self.account_type)
        balance = balances[0]
        whole_balance = (Decimal(balance["balance"]) - balance_reserve).quantize(Decimal("0"), ROUND_DOWN)
        if whole_balance < 1:
            logger.debug(f"{whole_balance=}")
        else:
            if self.is_in_orders(balance):
                self.cancel_active_orders()

            available_balance = (Decimal(balance["balance"]) - balance_reserve).quantize(Decimal("0"), ROUND_DOWN)
            if whole_balance != available_balance:
                logger.warning(f"{whole_balance=} dont match {available_balance=}")

            int_rate = self.get_lend_daily_rate()
            if int_rate < min_daily_rate:
                logger.warning(f"{int_rate=} is below {min_daily_rate=}")
                return
            int_rate = str(int_rate)

            order_sizes = self.get_order_sizes(available_balance, lend_order_quantity)
            for order_size in order_sizes:
                try:
                    order_id = self.margin_api.create_lend_order(self.currency, order_size, int_rate, self.term)
                    logger.info(f"Created lend order:{self.currency=}; {order_size=}; {int_rate=}; {order_id}")
                except Exception as e:
                    logger.error(f"Failed creating order: {self.currency=}; {order_size=}; {int_rate=}; {e}")


def main():
    handler = LendHandler()
    while True:
        try:
            handler.process_currency_lending()
        except Exception as e:
            logger.error(f"Exception while processing lending: {e}")
        finally:
            time.sleep(30)


if __name__ == '__main__':
    main()
