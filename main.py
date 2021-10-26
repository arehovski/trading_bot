from dataclasses import dataclass
import time
from decimal import Decimal

from kucoin.client import Margin, User
from redis import Redis

from config import API_KEY, API_SECRET, API_PASSPHRASE, is_sandbox
from connections import get_redis_connection


@dataclass
class LendHandler:
    margin_api: Margin = Margin(key=API_KEY, secret=API_SECRET, passphrase=API_PASSPHRASE, is_sandbox=is_sandbox)
    user_api: User = User(key=API_KEY, secret=API_SECRET, passphrase=API_PASSPHRASE, is_sandbox=is_sandbox)
    term: int = 7
    currency: str = "USDT"
    account_type: str = "main"
    redis: Redis = get_redis_connection()

    def __post_init__(self):
        self.balance_reserve = self.redis.get(f"kucoin:balance_reserve:{self.currency}") or 0
        self.balance_reserve = Decimal(self.balance_reserve)
        self.lend_order_quantity = self.redis.get(f"kucoin:lend_order_quantity:{self.currency}") or 500
        self.lend_order_quantity = Decimal(self.lend_order_quantity)
        self.min_daily_rate = self.redis.get(f"kucoin:min_daily_rate") or '0.0005'
        self.min_daily_rate = Decimal(self.min_daily_rate)

    def get_lend_daily_rate(self):
        market = self.margin_api.get_lending_market(self.currency, self.term)
        best = market[0]
        rate = Decimal(best.get('dailyIntRate'))
        return rate - Decimal('0.00001')

    def run(self):
        balances: list[dict] = self.user_api.get_account_list(self.currency, self.account_type)
        balance = balances[0]
        whole_balance = Decimal(balance["balance"]) - self.balance_reserve
        if whole_balance < 1:
            time.sleep(30)
            return
        else:
            available_balance = Decimal(balance["available"]) - self.balance_reserve
            if available_balance > 1:
                orders_count = available_balance // self.lend_order_quantity
                order_sizes = (self.lend_order_quantity,) * orders_count + (
                    available_balance - orders_count * self.lend_order_quantity,
                )
                order_sizes = tuple(map(str, order_sizes))

                int_rate = self.get_lend_daily_rate()
                if int_rate < self.min_daily_rate:
                    time.sleep(30)
                    return
                int_rate = str(int_rate)
                for order_size in order_sizes:
                    self.margin_api.create_lend_order(self.currency, order_size, int_rate, self.term)
