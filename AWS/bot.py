import os
import ccxt
import pandas as pd
import numpy as np
import time
import logging
import threading
from datetime import datetime, timezone
from typing import Optional
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from pymongo import MongoClient
from flask import Flask
from dotenv import load_dotenv
import requests

# ----- LOAD ENV VARIABLES -----
load_dotenv() 
# Get environment variables with defaults
PORT = int(os.getenv("PORT"))
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
# Retrieve backend host and port; provide defaults if they are not set
backend_uri = os.getenv("BACKEND_URI")
backend_port = os.getenv("BACKEND_PORT")

# ----- LOGGER SETUP -----
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- CONFIGURATION CLASS ----------
class StrategyConfig:
    def __init__(self, SYMBOL, TIMEFRAME):
        self.EXCHANGE = 'binance'
        self.SYMBOL = SYMBOL
        self.TIMEFRAME = TIMEFRAME

        # Indicators
        self.RSI_PERIOD = 14
        self.CCI_PERIOD = 20
        self.EMA_PERIOD = 50
        self.SMA_PERIOD = 50
        self.ATR_PERIOD = 14
        self.ADX_PERIOD = 14
        self.WT_CHANNEL_LENGTH = 10
        self.WT_ATR_LENGTH = 21
        self.EMA_LONG = 200
        self.SMA_SHORT = 50
        self.LORENTZIAN_FEATURES = ['close', 'volume', 'RSI', 'CCI', 'EMA', 'SMA', 'ATR', 'ADX', 'WT', 'ROC']
        self.VOLATILITY_WINDOW = 200
        self.VOLATILITY_PERCENTILE = 0.80

        # Labeling & AI
        self.Lookahead_window = 100
        self.window_size_AI = 200
        self.LIMIT = 1001  # to fetch data
        self.use_logistic_smoothing = True
        self.random_state = 42

        # Trading
        self.stop_atr_multiplier = 0.75
        self.reward_atr_multiplier = 0.75
        self.reward_to_risk_ratio = self.reward_atr_multiplier / self.stop_atr_multiplier
        self.initial_balance = 1270.0
        self.risk_per_trade = 0.7874 # 1
        self.taker_fee_rate = 0.0005
        self.risk_multiplier = 2

        # Misc: Load from environment variables
        self.mongo_uri = MONGO_URI
        self.db_name = DB_NAME
        self.collection_name = f"{SYMBOL.replace('/', '_')}"
        #self.collection_name = f"{SYMBOL.replace('/', '_')}_{TIMEFRAME}"

# ---------- MARKET DATA FETCHER ----------
class MarketDataFetcher:
    @staticmethod
    def timeframe_to_minutes(tf: str) -> int:
        tf = tf.lower()
        if tf.endswith("m"):
            return int(tf[:-1])
        elif tf.endswith("h"):
            return int(tf[:-1]) * 60
        elif tf.endswith("d"):
            return int(tf[:-1]) * 60 * 24
        else:
            raise ValueError(f"Unrecognized timeframe: {tf}")

    @staticmethod
    def sleep_until_candle_close(tf_minutes: int):
        """
        Sleeps until the next candle is (almost) closed.
        """
        reducedelay = 54
        now_utc = datetime.now(timezone.utc)
        minute = now_utc.minute
        second = now_utc.second

        times_passed = minute // tf_minutes
        next_multiple = (times_passed + 1) * tf_minutes

        delta_min = next_multiple - minute
        if delta_min < 0:
            delta_min += tf_minutes

        remain_sec = 60 - second
        total_sleep = delta_min * 60 + remain_sec - reducedelay
        total_sleep = max(0, total_sleep)

        if total_sleep > 0:
            logger.info("---------------------------------------------------")
            logger.info(f"Sleeping {total_sleep} seconds until next {tf_minutes}m candle close...")
            time.sleep(total_sleep)

    @staticmethod
    def delete_database(db_name: str):
        """
        Deletes the specified database from MongoDB.
        """
        client = MongoClient()
        client.drop_database(db_name)
        logger.info(f"❌ Deleted existing database: {db_name}")

    # @staticmethod
    # def fetch_binance_futures_ohlcv(symbol: str, timeframe: str, limit: int,last_known_ts: pd.Timestamp = None) -> Optional[pd.DataFrame]:
    #     """
    #     Fetches OHLCV data from Binance Futures with retry logic.
    #     Retries up to 3 times in case of failure.
    #     """
    #     exchange = ccxt.binance({'options': {'defaultType': 'future'}})
    #     max_retries = 2
    #     retry_delay = 15  # seconds

    #     for attempt in range(max_retries):
    #         try:
    #             logger.info(f"Fetching {limit} bars for {symbol} on {timeframe} (Attempt {attempt+1}/{max_retries})...")
    #             ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=None, limit=limit)

    #             if not ohlcv or len(ohlcv) < 2:
    #                 logger.warning("No or insufficient data from Binance.")
    #                 return None

    #             df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    #             df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    #             df.drop_duplicates(subset=['timestamp'], inplace=True)
    #             df.sort_values('timestamp', inplace=True)
    #             df.reset_index(drop=True, inplace=True)

    #             # remove last row => incomplete candle
    #             if len(df) > 0:
    #                 last_candle_time = df.iloc[-1]['timestamp']
    #                 logger.info(f"Dropping the last row to ensure we skip the unfinished candle. Time: {last_candle_time}")
    #                 df = df.iloc[:-1]  # drop final row

    #             logger.info(f"✅ Successfully fetched {len(df)} fully closed bars.")
    #             return df

    #         except Exception as e:
    #             logger.error(f"Error fetching data: {e}")
    #             if attempt < max_retries - 1:
    #                 logger.info(f"Retrying in {retry_delay} seconds...")
    #                 time.sleep(retry_delay)
    #             else:
    #                 logger.error("❌ Maximum retries reached. Skipping this iteration.")
    #                 return None

####

    @staticmethod
    def fetch_binance_futures_ohlcv(symbol: str, timeframe: str, limit: int, last_known_ts: pd.Timestamp = None) -> Optional[pd.DataFrame]:
        """
        Fetches OHLCV data from Bybit Futures (modified for Bybit)
        """
        exchange = ccxt.bybit({
            'options': {
                'defaultType': 'linear'  # For USDT perpetual contracts
            }
        })

        # Convert symbol to Bybit futures format (BTC/USDT → BTCUSDT)
        if "/" in symbol:
            base, quote = symbol.split("/")
            futures_symbol = f"{base}{quote}"  # BTCUSDT
        else:
            futures_symbol = symbol
            
        max_retries = 2
        retry_delay = 15  # seconds

        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching {limit} bars for {symbol} on {timeframe} (Attempt {attempt+1}/{max_retries})...")
                ohlcv = exchange.fetch_ohlcv(futures_symbol, timeframe, since=None, limit=limit)

                # Rest of the code remains unchanged
                if not ohlcv or len(ohlcv) < 2:
                    logger.warning("No or insufficient data from Binance.")
                    return None

                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.drop_duplicates(subset=['timestamp'], inplace=True)
                df.sort_values('timestamp', inplace=True)
                df.reset_index(drop=True, inplace=True)

                if len(df) > 0:
                    last_candle_time = df.iloc[-1]['timestamp']
                    logger.info(f"Dropping the last row to ensure we skip the unfinished candle. Time: {last_candle_time}")
                    df = df.iloc[:-1]

                logger.info(f"✅ Successfully fetched {len(df)} fully closed bars.")
                return df

            except Exception as e:
                logger.error(f"Error fetching data: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error("❌ Maximum retries reached. Skipping this iteration.")
                    return None

####
# ---------- TECHNICAL INDICATORS ----------
class TechnicalIndicators:
    @staticmethod
    def calculate_indicators(df: pd.DataFrame, config: StrategyConfig) -> pd.DataFrame:
        logger.info("Calculating technical indicators...")

        # RSI
        if 'RSI' not in df.columns:
            delta = df["close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=config.RSI_PERIOD).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=config.RSI_PERIOD).mean()
            rs = gain / loss
            df["RSI"] = 100 - (100 / (1 + rs))

        # CCI
        if 'CCI' not in df.columns:
            tp = (df["high"] + df["low"] + df["close"]) / 3
            cci_mean = tp.rolling(window=config.CCI_PERIOD).mean()
            mean_dev = (tp - cci_mean).abs().rolling(window=config.CCI_PERIOD).mean()
            df["CCI"] = (tp - cci_mean) / (0.015 * mean_dev)

        # EMA, SMA
        if 'EMA' not in df.columns:
            df["EMA"] = df["close"].ewm(span=config.EMA_PERIOD, adjust=False).mean()
        if 'SMA' not in df.columns:
            df["SMA"] = df["close"].rolling(window=config.SMA_PERIOD).mean()

        # ATR
        if 'ATR' not in df.columns:
            df["ATR"] = (df["high"] - df["low"]).rolling(window=config.ATR_PERIOD).mean()

        # ADX
        if 'ADX' not in df.columns:
            adx_len = config.ADX_PERIOD
            di_len = config.ADX_PERIOD
            df["TR"] = np.maximum(
                df["high"] - df["low"],
                np.maximum(
                    abs(df["high"] - df["close"].shift(1)),
                    abs(df["low"] - df["close"].shift(1))
                )
            )
            up_move = df["high"].diff()
            down_move = -df["low"].diff()
            df["+DM"] = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
            df["-DM"] = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

            df["+DI"] = 100 * (df["+DM"].rolling(window=di_len).mean() / df["TR"].rolling(window=di_len).mean())
            df["-DI"] = 100 * (df["-DM"].rolling(window=di_len).mean() / df["TR"].rolling(window=di_len).mean())

            df["DX"] = 100 * (abs(df["+DI"] - df["-DI"]) / (df["+DI"] + df["-DI"]))
            df["ADX"] = df["DX"].rolling(window=adx_len).mean()

            df.drop(columns=["TR", "+DM", "-DM", "+DI", "-DI", "DX"], inplace=True)

        # WaveTrend
        if 'WT' not in df.columns:
            hlc3 = (df["high"] + df["low"] + df["close"]) / 3
            esa = hlc3.ewm(span=config.WT_CHANNEL_LENGTH, adjust=False).mean()
            d = abs(hlc3 - esa).ewm(span=config.WT_ATR_LENGTH, adjust=False).mean()
            df["WT"] = (hlc3 - esa) / (0.015 * d)

        df.dropna(inplace=True)
        logger.info("Indicators calculated.")
        return df

# ---------- DERIVED FEATURES ----------
class DerivedFeatures:
    @staticmethod
    def calculate_features(df: pd.DataFrame, config: StrategyConfig) -> pd.DataFrame:
        logger.info("Calculating derived features...")

        # Ensure needed columns
        df["EMA_LONG"] = df["close"].ewm(span=config.EMA_LONG, adjust=False).mean()
        df["SMA_SHORT"] = df["close"].rolling(window=config.SMA_SHORT).mean()

        # Market Regime
        df["Market_Regime"] = df["SMA_SHORT"] / df["EMA_LONG"]
        df["Regime_Gradient"] = df["Market_Regime"].diff()
        std_dev = df["Regime_Gradient"].rolling(window=config.SMA_SHORT).std()

        df["Regime_Label"] = np.where(
            df["Regime_Gradient"] > std_dev, "Uptrend",
            np.where(df["Regime_Gradient"] < -std_dev, "Downtrend", "Ranging")
        )

        # Volatility Filter
        df["Volatility_Filter"] = df["ATR"] / df["close"]
        percentile_80 = df["Volatility_Filter"].rolling(window=config.VOLATILITY_WINDOW).quantile(config.VOLATILITY_PERCENTILE)
        df["High_Volatility"] = df["Volatility_Filter"] > percentile_80

        df.dropna(inplace=True)
        df.drop(columns=["Market_Regime", "Regime_Gradient", "Volatility_Filter"], inplace=True, errors='ignore')
        logger.info("Derived features calculated.")
        return df

# ---------- LABELING FEATURES ----------
class LabelingFeature:
    @staticmethod
    def compute_lookahead_period(df: pd.DataFrame, config: StrategyConfig) -> pd.DataFrame:
        logger.info("Computing lookahead period (ATR-based)...")
        window = config.Lookahead_window

        df['ATR_Percentile'] = df['ATR'].rolling(window=window).rank(pct=True)
        df.dropna(subset=['ATR_Percentile'], inplace=True)
        df['Lookahead_Period'] = np.clip(((df['ATR_Percentile'] * 7) + 7).round(), 7, 14).astype(int)
        df.drop(columns=['ATR_Percentile'], inplace=True)
        return df

    @staticmethod
    def compute_market_structure(df: pd.DataFrame, config: StrategyConfig) -> pd.DataFrame:
        logger.info("Computing market structure (Support/Resistance)...")
        window = config.Lookahead_window

        df['Rolling_High'] = df['high'].rolling(window=window).max()
        df['Rolling_Low'] = df['low'].rolling(window=window).min()

        df['Support_Level'] = df['Rolling_Low'].rolling(window=window).mean()
        df['Resistance_Level'] = df['Rolling_High'].rolling(window=window).mean()

        df['Breakout_Confirm'] = np.where(
            df['close'] > df['Resistance_Level'], 1,
            np.where(df['close'] < df['Support_Level'], -1, 0)
        )

        df.drop(columns=['Rolling_High', 'Rolling_Low'], inplace=True)
        df.dropna(inplace=True)
        return df

    # @staticmethod
    # def compute_momentum_features(df: pd.DataFrame, config: StrategyConfig) -> pd.DataFrame:
    #     logger.info("Computing momentum-based features...")
    #     window = config.Lookahead_window

    #     df['ROC'] = df['close'].pct_change(periods=window) * 100
    #     df['Momentum_Percentile'] = df['ROC'].rolling(window=window).rank(pct=True)

    #     df['Momentum_Confirm'] = np.where(
    #         df['Momentum_Percentile'] >= 0.80, 1,
    #         np.where(df['Momentum_Percentile'] <= 0.20, -1,
    #                  np.where((df['Momentum_Percentile'] >= 0.40) & (df['Momentum_Percentile'] <= 0.60), 0, np.nan))
    #     )
    #     df.drop(columns=['Momentum_Percentile'], inplace=True, errors='ignore')
    #     df.dropna(inplace=True)
    #     return df

###

    @staticmethod
    def compute_momentum_features(df: pd.DataFrame, config: StrategyConfig) -> pd.DataFrame:
        logger.info("Computing momentum-based features...")
        window = config.Lookahead_window

        # 1. Preserve original ROC calculation
        df['ROC'] = df['close'].pct_change(periods=window) * 100  # No fillna
        
        # 2. Keep original rolling rank logic
        df['Momentum_Percentile'] = df['ROC'].rolling(window=window).rank(pct=True)
        
        # 3. Maintain condition structure but eliminate NaNs
        df['Momentum_Confirm'] = np.where(
            df['Momentum_Percentile'] >= 0.80, 1,
            np.where(df['Momentum_Percentile'] <= 0.20, -1,
                    np.where((df['Momentum_Percentile'] >= 0.40) & 
                            (df['Momentum_Percentile'] <= 0.60), 0, 0))
        )
        
        # 4. Targeted cleanup
        df.drop(columns=['Momentum_Percentile'], inplace=True, errors='ignore')
        df.dropna(subset=['ROC'], inplace=True) 
        
        return df

###

    @staticmethod
    def compute_lorentzian_distance(df: pd.DataFrame, config: StrategyConfig) -> pd.DataFrame:
        logger.info("Computing Lorentzian distance...")
        if 'Lorentzian_Distance' not in df.columns:
            feat_cols = config.LORENTZIAN_FEATURES
            df['Lorentzian_Distance'] = np.log(1 + np.abs(df[feat_cols].diff())).sum(axis=1)
        df.dropna(inplace=True)
        return df

# ---------- CANDLE LABELING ----------
class CandelLabeling:
    @staticmethod
    def label_candles(df: pd.DataFrame, config: StrategyConfig) -> pd.DataFrame:
        logger.info("Applying candle labeling...")
        df['Candle_Label'] = 0

        # Condition 1
        df.loc[
            (df['close'] > df['Support_Level']) &
            (df['EMA_LONG'] < df['SMA_SHORT']) &
            (df['ADX'] > 25),
            'Candle_Label'
        ] = 1

        df.loc[
            (df['close'] < df['Resistance_Level']) &
            (df['EMA_LONG'] > df['SMA_SHORT']) &
            (df['ADX'] > 25),
            'Candle_Label'
        ] = -1

        # Condition 2
        neutral_mask = (
            df['close'].between(df['Support_Level'], df['Resistance_Level']) &
            (df['Momentum_Confirm'] == 0)
        )
        df.loc[neutral_mask, 'Candle_Label'] = 0

        # Condition 3
        df.loc[
            (df['Breakout_Confirm'] == 1) &
            (df['ROC'] > 0) &
            (df['Momentum_Confirm'] == 1),
            'Candle_Label'
        ] = 1

        df.loc[
            (df['Breakout_Confirm'] == -1) &
            (df['ROC'] < 0) &
            (df['Momentum_Confirm'] == -1),
            'Candle_Label'
        ] = -1

        # Condition 4
        df.loc[
            (df['close'] < df['Support_Level']) &
            (df['Momentum_Confirm'] == 1),
            'Candle_Label'
        ] = 1
        df.loc[
            (df['close'] > df['Resistance_Level']) &
            (df['Momentum_Confirm'] == -1),
            'Candle_Label'
        ] = -1

        # Condition 5: Lorentzian outliers
        extreme_dist = df['Lorentzian_Distance'] > df['Lorentzian_Distance'].quantile(0.80)
        df.loc[extreme_dist & (df['Breakout_Confirm'] == 1), 'Candle_Label'] = 1
        df.loc[extreme_dist & (df['Breakout_Confirm'] == -1), 'Candle_Label'] = -1

        # Meta: if confidence is low => 0
        low_conf = (df['Momentum_Confirm'].abs() < 0.5) | (df['ADX'] < 20)
        df.loc[low_conf, 'Candle_Label'] = 0

        return df

# ---------- AI MODEL ----------
class AIModel:
    def __init__(self, config: StrategyConfig):
        self.config = config
        self.client = MongoClient(self.config.mongo_uri)
        self.db = self.client[self.config.db_name]
        self.collection = self.db[self.config.collection_name]

        self.use_logistic_smoothing = self.config.use_logistic_smoothing

        self.knn = KNeighborsClassifier()
        self.lr = LogisticRegression(random_state=self.config.random_state)
        self.scaler = StandardScaler()

    def train_and_predict(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Training on the last window_size_AI candles & predicting the next candle...")

        features = ['close', 'volume', 'RSI', 'CCI', 'EMA', 'SMA', 'ATR', 'ADX', 'WT', 'ROC', 'Lorentzian_Distance']
        needed_cols = features + ['Candle_Label', 'Lookahead_Period']
        
        df.dropna(subset=needed_cols, inplace=True)

        window_size = self.config.window_size_AI
        if len(df) < (window_size + 1):
            logger.warning(f"Not enough data to train with window_size={window_size}. Need at least {window_size+1} rows.")
            df['prediction'] = np.nan
            return df
        
        # Training on the last window_size candles (excluding the final row)
        train_data = df.iloc[-(window_size+1):-1].copy()  
        test_data  = df.iloc[-1:].copy()   

        X_train = train_data[features].values
        y_train = train_data['Candle_Label'].values
        X_test  = test_data[features].values
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled  = self.scaler.transform(X_test)

        # Dynamic k for KNN based on Lookahead_Period
        k_neighbors = int(train_data['Lookahead_Period'].mean())
        if k_neighbors < 1:
            k_neighbors = 1
        self.knn.set_params(n_neighbors=k_neighbors)
        self.knn.fit(X_train_scaled, y_train)

        # Optional Logistic Smoothing
        if self.use_logistic_smoothing:
            knn_proba_train = self.knn.predict_proba(X_train_scaled)
            X_train_smooth  = np.concatenate([X_train_scaled, knn_proba_train], axis=1)
            self.lr.fit(X_train_smooth, y_train)

            knn_proba_test = self.knn.predict_proba(X_test_scaled)
            X_test_smooth  = np.concatenate([X_test_scaled, knn_proba_test], axis=1)
            final_pred = self.lr.predict(X_test_smooth)[0]
        else:
            final_pred = self.knn.predict(X_test_scaled)[0]

        df['prediction'] = np.nan
        df.loc[df.index[-1], 'prediction'] = final_pred
        return df

# ---------- Api Calls  ----------

def user_trade_open(trade_data):
    """
    Sends selected trade data to the backend when a trade is opened.
    """
    # Construct the endpoints using the environment variables
    open_trade_endpoint = f"http://{backend_uri}:{backend_port}/opentrades/open_trade"

    # Extract only the required fields and convert to standard Python types
    payload = {
        "symbol": str(trade_data["symbol"]),
        "direction": str(trade_data["direction"]),
        "stop_loss": float(trade_data["stop_loss"]),
        "take_profit": float(trade_data["take_profit"]),
        "investment_per_trade": float(trade_data["investment_per_trade"]),
        "amount_multiplier": float(trade_data["amount_multiplier"]), 
    }

    # Send POST request with JSON body
    response = requests.post(open_trade_endpoint, json=payload)

    # Handle the response
    if response.status_code == 200:
        data = response.json()

        print("####################")
        print(data["message"])
        print("####################")
        
        
    else:
        print(f"Error: {response.status_code}, {response.text}")


def user_trade_close(symbol, direction,reason):
    # Construct the endpoint using the environment variables
    close_trade_endpoint = f"http://{backend_uri}:{backend_port}/closetrades/close_trade"
    
    # Prepare the payload with symbol and direction
    payload = {
        "symbol": symbol,
        "direction": direction,
        "reason": reason
    }
    
    # Send the POST request with JSON data
    response = requests.post(close_trade_endpoint, json=payload)
    data = response.json()

    print("###############################")
    print(data["message"])
    print("###############################")


# ---------- TRADING SIMULATION ----------
class TradingSimulation:
    def __init__(self, config: StrategyConfig):
        self.config = config
        self.client = MongoClient(self.config.mongo_uri)
        self.db = self.client[self.config.db_name]
        self.trades_collection = self.db[self.config.collection_name]

        self.symbol = self.config.SYMBOL
        self.initial_balance = self.config.initial_balance
        self.current_risk_percent = self.config.risk_per_trade

        self._resume_risk_from_last_trade()

    def filter_signal(self, row) -> bool:
        return True

    def _resume_risk_from_last_trade(self):
        last_closed_trade = self.trades_collection.find_one(
            {"status": {"$in": ["TP", "SL"]}},
            sort=[("exit_time", -1)]
        )

        if last_closed_trade:
            last_trade_status = last_closed_trade["status"]
            last_investment = last_closed_trade.get("investment_per_trade", self.config.risk_per_trade)
            if last_trade_status == "SL":
                self.current_investment_per_trade = last_investment * 2
            elif last_trade_status == "TP":
                self.current_investment_per_trade = self.config.risk_per_trade
        else:
            self.current_investment_per_trade = self.config.risk_per_trade

    def update_investment_per_trade(self, last_trade_status: str):
        if last_trade_status in ["SL"]:
            self.current_risk_percent *= self.config.risk_multiplier  
        elif last_trade_status in ["TP"]:
            self.current_risk_percent = self.config.risk_per_trade

    def calculate_risk_amount(self, entry_price, exit_price):
        if entry_price == 0:
            return 0, 0
        price_diff_percent = abs((exit_price - entry_price) / entry_price) * 100
        if price_diff_percent == 0:
            return 0, 0
        amount_multiplier = 100 / price_diff_percent
        risk_amount = (self.current_risk_percent / 100.0) * self.initial_balance * amount_multiplier
        return risk_amount, amount_multiplier

    def calculate_quantity(self, entry_price, exit_price):
        risk_amount, amount_multiplier = self.calculate_risk_amount(entry_price, exit_price)
        if entry_price == 0:
            return 0, amount_multiplier
        quantity = risk_amount / entry_price
        return quantity, amount_multiplier

    def calculate_pnl(self, entry_price, exit_price, direction: str):
        quantity, amount_multiplier = self.calculate_quantity(entry_price, exit_price)
        if direction.upper() == "LONG":
            profit = (exit_price - entry_price) * quantity
        else:
            profit = (entry_price - exit_price) * quantity
        fee_entry = quantity * entry_price * self.config.taker_fee_rate
        fee_exit  = quantity * exit_price  * self.config.taker_fee_rate
        total_fee = fee_entry + fee_exit
        net_pnl = profit - total_fee
        return profit, net_pnl, total_fee, amount_multiplier

    def get_open_trade(self):
        return self.trades_collection.find_one({"status": "OPEN"})

    def open_trade(self, row):
        direction_str = "LONG" if row["prediction"] == 1 else "SHORT"
        entry_price = row["close"]
        atr = row["ATR"]

        if direction_str == "LONG":
            stop_loss = entry_price - (self.config.stop_atr_multiplier * atr)
            take_profit = entry_price + (self.config.reward_atr_multiplier * atr)
            approximate_exit_for_risk = stop_loss
        else:
            stop_loss = entry_price + (self.config.stop_atr_multiplier * atr)
            take_profit = entry_price - (self.config.reward_atr_multiplier * atr)
            approximate_exit_for_risk = stop_loss

        risk_amount, amount_multiplier = self.calculate_risk_amount(entry_price, approximate_exit_for_risk)

        trade_data = {
            "symbol": self.symbol,
            "direction": direction_str,
            "entry_time": row["timestamp"],
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "status": "OPEN",
            "exit_time": None,
            "exit_price": None,
            "investment_per_trade": self.current_risk_percent,
            "amount_multiplier": amount_multiplier,
            "total_fees": 0,
            "pnl": 0,
            "net_pnl": 0
        }

        self.trades_collection.insert_one(trade_data)
        logger.info(
            f"Opened {direction_str} trade @ {entry_price:.2f} | SL={stop_loss:.2f}, TP={take_profit:.2f}, risk%={self.current_risk_percent}"
        )

        # Call the dummy user trade open function
        user_trade_open(trade_data)

    def close_trade(self, open_trade, reason: str, row, forced_exit_price=None):
        if forced_exit_price is not None:
            exit_price = forced_exit_price
        else:
            exit_price = row["close"]
        symbol=open_trade["symbol"]
        direction = open_trade["direction"]
        entry_price = open_trade["entry_price"]
        profit, net_pnl, total_fee, final_amount_multiplier = self.calculate_pnl(entry_price, exit_price, direction)

        update_data = {
            "exit_time": row["timestamp"],
            "exit_price": exit_price,
            "status": reason,
            "pnl": profit,
            "net_pnl": net_pnl,
            "total_fees": total_fee,
            "amount_multiplier": final_amount_multiplier
        }
        self.trades_collection.update_one({"_id": open_trade["_id"]}, {"$set": update_data})

        logger.info(
            f"Closed trade OF {symbol} -> {direction}  with status={reason} @ {exit_price:.2f}. PNL={profit:.2f}, NetPNL={net_pnl:.2f}, Fees={total_fee:.2f}"
        )

        # Call the dummy user trade close function
        user_trade_close(symbol,direction,reason)
        self.update_investment_per_trade(reason)
        trade_analysis = TradeAnalysys(self.db, self.config)
        trade_analysis.analyze_and_store()

    def check_sl_tp(self, open_trade, row):
        direction = open_trade["direction"]
        sl = open_trade["stop_loss"]
        tp = open_trade["take_profit"]
        current_low = row["low"]
        current_high = row["high"]
        time=row["timestamp"]

        print("---------------------------")
        print("time: ",time)
        print("direction: ",direction)

        if direction == "LONG":
            print("----------")
            print("Low: ",current_low," <= SL ",sl)
            print("---")
            print("High: ",current_high," >= TP ",tp)
            print("----------")
            if current_low <= sl:
                logger.info("----------")
                logger.info(current_low)
                logger.info("SL HIT")
                self.close_trade(open_trade, reason="SL", row=row, forced_exit_price=sl)
                return True
            elif current_high >= tp:
                logger.info("----------")
                logger.info(current_high)
                logger.info("TP HIT")
                self.close_trade(open_trade, reason="TP", row=row, forced_exit_price=tp)
                return True
            logger.info("TP or SL not HIT.")
            return False
        else:
            print("----------")
            print("High: ",current_high," >= SL ",sl)
            print("---")
            print("Low: ",current_low," <= TP ",tp)
            print("----------")
            if current_high >= sl:
                logger.info("----------")
                logger.info(current_high)
                logger.info("SL HIT")
                self.close_trade(open_trade, reason="SL", row=row, forced_exit_price=sl)
                return True
            elif current_low <= tp:
                logger.info("----------")
                logger.info(current_low)
                logger.info("TP HIT")
                self.close_trade(open_trade, reason="TP", row=row, forced_exit_price=tp)
                return True
            logger.info("TP or SL not HIT.")
            return False

    def handle_signal(self, row):
        open_trade = self.get_open_trade()
        trade_closed = False

        if open_trade:
            logger.info("Checking if open trade hit TP or SL.")
            trade_closed = self.check_sl_tp(open_trade, row)

        if not self.filter_signal(row):
            logger.info("Signal is skipped.")
            return

        if not open_trade or trade_closed:
            logger.info("No open trade or the trade was just closed. Opening a new trade.")
            self.open_trade(row)
        else:
            current_dir = open_trade["direction"]
            new_dir = "LONG" if row["prediction"] == 1 else "SHORT"

            if current_dir == new_dir:
                logger.info(f"Signal is {new_dir}, but we already have OPEN {current_dir}. Skipping.")
            else:
                logger.info(f"Signal is {new_dir}, but open trade is {current_dir}. Reversing...")
                exit_price = row["close"]
                entry_price = open_trade["entry_price"]
                if current_dir == "LONG":
                    close_reason = "TP" if exit_price > entry_price else "SL"
                else:
                    close_reason = "TP" if exit_price < entry_price else "SL"
                self.close_trade(open_trade, reason=close_reason, row=row)
                self.open_trade(row)

# ---------- TRADE ANALYSIS ----------
class TradeAnalysys:
    def __init__(self, db, config: StrategyConfig):
        self.db = db
        self.config = config
        self.trades_collection = db[self.config.collection_name]
        self.analysis_collection = db[f"Analysis_{self.config.collection_name}"]

    def analyze_and_store(self):
        closed_trades_cursor = self.trades_collection.find(
            {"status": {"$ne": "OPEN"}}
        ).sort("exit_time", 1)
        closed_trades = list(closed_trades_cursor)

        if not closed_trades:
            logger.info("No closed trades yet. Skipping analysis.")
            return

        total_trades = len(closed_trades)
        winners = [t for t in closed_trades if t["status"] == "TP"]
        losers  = [t for t in closed_trades if t["status"] == "SL"]

        winning_trades = len(winners)
        losing_trades  = len(losers)

        max_winning_streak = 0
        max_losing_streak  = 0
        current_win_streak = 0
        current_loss_streak = 0

        for trade in closed_trades:
            if trade["status"] == "TP":
                current_win_streak += 1
                max_winning_streak = max(max_winning_streak, current_win_streak)
                current_loss_streak = 0
            elif trade["status"] == "SL":
                current_loss_streak += 1
                max_losing_streak = max(max_losing_streak, current_loss_streak)
                current_win_streak = 0
            else:
                current_win_streak = 0
                current_loss_streak = 0

        sum_net_pnl = sum(t.get("net_pnl", 0) for t in closed_trades)
        sum_profit  = sum(t.get("pnl", 0) for t in closed_trades)
        avg_profit = np.mean([t["net_pnl"] for t in winners]) if winning_trades > 0 else 0.0
        avg_loss   = np.mean([t["net_pnl"] for t in losers]) if losing_trades > 0 else 0.0
        total_fees_paid = sum(t.get("total_fees", 0) for t in closed_trades)
        break_even_win_rate = 100 * (1 / (1 + self.config.reward_to_risk_ratio))
        win_rate = (winning_trades / total_trades) * 100.0

        initial_balance = self.config.initial_balance
        net_balance = initial_balance + sum_net_pnl
        balance     = initial_balance + sum_profit
        roi         = ((net_balance - initial_balance) / initial_balance) * 100.0

        analysis_result = {
            "timestamp": datetime.now(),
            "Total Trades": total_trades,
            "Winning Trades": winning_trades,
            "Losing Trades": losing_trades,
            "Max Winning Streak": int(max_winning_streak),
            "Max Losing Streak": int(max_losing_streak),
            "Avg Profit Per Trade": float(avg_profit),
            "Avg Loss Per Trade": float(avg_loss),
            "Total Fees Paid": float(total_fees_paid),
            "Break-even Win Rate (%)": float(break_even_win_rate),
            "Win Rate (%)": float(win_rate),
            "ROI (%)": float(roi),
            "NET Final Balance": float(net_balance),
            "Final Balance": float(balance)
        }

        self.analysis_collection.update_one(
            {"analysis_id": 1},
            {"$set": analysis_result},
            upsert=True
        )
        #logger.info(f"Trade Analysis stored: {analysis_result}")

# ---------- LIVE TRADING LOOP ----------
def run_live_trading(config: StrategyConfig):
    # Optional: Delete existing database if needed
    # MarketDataFetcher.delete_database(config.db_name)

    ai_model = AIModel(config)
    trading_sim = TradingSimulation(config)
    tf_minutes = MarketDataFetcher.timeframe_to_minutes(config.TIMEFRAME)
    last_processed_ts = None
    while True:
        MarketDataFetcher.sleep_until_candle_close(tf_minutes)

        df = MarketDataFetcher.fetch_binance_futures_ohlcv(
            symbol=config.SYMBOL,
            timeframe=config.TIMEFRAME,
            limit=config.LIMIT,
            last_known_ts=last_processed_ts
        )

        if df is None or df.empty:
            logger.warning("No data fetched. Skipping iteration.")
            continue

        last_processed_ts = df.iloc[-1]["timestamp"]
        #logger.info(f"New data up to: {last_processed_ts}")

        # Pipeline: Calculate indicators and features
        df = TechnicalIndicators.calculate_indicators(df, config)
        df = DerivedFeatures.calculate_features(df, config)
        df = LabelingFeature.compute_lookahead_period(df, config)
        df = LabelingFeature.compute_market_structure(df, config)
        df = LabelingFeature.compute_momentum_features(df, config)
        #logger.info(f"After compute_lookahead_period ({len(df)} rows). Last ts: {df.iloc[-1]['timestamp']}")
        df = LabelingFeature.compute_lorentzian_distance(df, config)
        df = CandelLabeling.label_candles(df, config)
        df = ai_model.train_and_predict(df)

        latest_row = df.iloc[-1]

        logger.info(f"[{config.SYMBOL} {config.TIMEFRAME}] Latest candle prediction => {latest_row.get('prediction', np.nan)}")
        print("Latest row ",latest_row["timestamp"])
        trading_sim.handle_signal(latest_row)

# ---------- HEALTH CHECK ENDPOINT USING FLASK ----------
app = Flask(__name__)

@app.route("/")
def health_check():
    return "Bot is Running!", 200

# ---------- MAIN ----------
if __name__ == "__main__":
    # Define the list of coin/timeframe configurations
    configs = [
        StrategyConfig(SYMBOL='BTC/USDT', TIMEFRAME='1m')
        # StrategyConfig(SYMBOL='ETH/USDT', TIMEFRAME='5m'),
        # StrategyConfig(SYMBOL='BNB/USDT', TIMEFRAME='5m'),
        # StrategyConfig(SYMBOL='SOL/USDT', TIMEFRAME='5m'),
        # StrategyConfig(SYMBOL='1000PEPE/USDT', TIMEFRAME='5m')
    ]

    # Start trading bot threads for each configuration (set as daemon threads)
    trading_threads = []
    for conf in configs:
        t = threading.Thread(target=run_live_trading, args=(conf,), daemon=True)
        t.start()
        trading_threads.append(t)

    # Run the Flask app for the health-check endpoint
    app.run(host="0.0.0.0", port=PORT)
