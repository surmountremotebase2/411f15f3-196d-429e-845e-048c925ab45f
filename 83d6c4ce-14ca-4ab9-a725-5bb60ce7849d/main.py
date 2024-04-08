from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Ticker for the leveraged ETF we are interested in trading
        self.ticker = "TQQQ"
        # Ticker for the index we want to analyze
        self.index_ticker = "QQQ"

    @property
    def assets(self):
        # We define the asset we are trading, which is TQQQ
        return [self.ticker]

    @property
    def interval(self):
        # We operate on daily intervals, checking conditions at market open
        return "1day"

    def run(self, data):
        # Extracting Historical Open-High-Low-Close-Volume (OHLCV) data for QQQ
        ohlcv_data = data["ohlcv"]
        
        # Calculating the 25-day Exponential Moving Average (EMA) for QQQ
        ema_qqq = EMA(self.index_ticker, ohlcv_data, 25)
        
        # Initializing the stake to allocate in TQQQ
        tqqq_stake = 0

        # If there's insufficient data to calculate EMA, we don't trade
        if ema_qqq is None or len(ema_qqq) < 1:
            log("Insufficient data for EMA calculation.")
            return TargetAllocation({self.ticker: tqqq_stake})
        
        # If the latest opening price of QQQ is above its 25-day EMA,
        # we take a 100% position in TQQQ. Otherwise, we sell any holdings.
        latest_open_price_qqq = ohlcv_data[-1][self.index_ticker]['open']
        latest_ema_qqq = ema_qqq[-1]
        
        if latest_open_price_qqq > latest_ema_qqq:
            tqqq_stake = 1  # Allocating 100% to TQQQ
            log("QQQ is above its 25-day EMA. Buying TQQQ.")
        else:
            tqqq_stake = 0  # Selling off any TQQQ holdings
            log("QQQ is not above its 25-day EMA. Selling TQQQ.")
        
        # Creating and returning the TargetAllocation object based on our decision
        return TargetAllocation({self.ticker: tqqq_stake})