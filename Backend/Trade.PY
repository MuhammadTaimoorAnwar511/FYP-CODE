import requests
import time
import hmac
import hashlib
import json
import math

class BYBITCONFIG:
    def __init__(self, 
                 api_key: str,
                 api_secret: str,
                 base_url: str = "https://api-demo.bybit.com",
                 symbol: str = "None",
                 direction: str = "None",
                 stop_loss: float = None,
                 take_profit: float = None,
                 investment_per_trade: float = 1,
                 amount_multiplier: float = 1,
                 amount_allocated: float = 1,
                 recv_window: str = "5000",
                 max_leverage: str = "50", 
                 cross: bool = True):
        
        # Validate direction
        if direction.lower() not in ["long", "short"]:
            raise ValueError("Direction must be 'long' or 'short'")
        
        # Store API credentials and configuration
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.symbol = symbol
        self.direction = direction.lower()
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.recv_window = recv_window
        self.max_leverage = max_leverage  
        self.cross = cross  
        
        # Calculate dynamic USDT amount based on allocated capital, trade percentage and multiplier
        self.usdt_amount = (amount_allocated * (investment_per_trade / 100)) * amount_multiplier

    def get_server_timestamp(self) -> int:
        """Retrieve the server timestamp in milliseconds."""
        try:
            response = requests.get(f"{self.base_url}/v5/market/time")
            if response.status_code == 200:
                data = response.json()
                time_nano = int(data["result"]["timeNano"])
                return time_nano // 1_000_000
            else:
                return int(time.time() * 1000)
        except Exception as e:
            print(f"Error fetching server time: {e}")
            return int(time.time() * 1000)

    def send_post_request(self, endpoint: str, params: dict) -> requests.Response:
        """Send a POST request with headers and signature."""
        timestamp = str(self.get_server_timestamp())
        sorted_params = dict(sorted(params.items()))
        json_payload = json.dumps(sorted_params, separators=(',', ':'))
        signature_payload = f"{timestamp}{self.api_key}{self.recv_window}{json_payload}"
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            signature_payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            "X-BAPI-API-KEY": self.api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-RECV-WINDOW": self.recv_window,
            "X-BAPI-SIGN": signature,
            "Content-Type": "application/json"
        }
        return requests.post(f"{self.base_url}{endpoint}", data=json_payload, headers=headers)

    def get_current_price(self) -> float:
        """Retrieve current market price."""
        endpoint = "/v5/market/tickers"
        params = {"category": "linear", "symbol": self.symbol}
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params)
            if response.status_code == 200:
                data = response.json()
                return float(data['result']['list'][0]['lastPrice'])
            return None
        except Exception as e:
            print(f"Price fetch error: {e}")
            return None

    def get_instrument_info(self) -> dict:
        """Retrieve full instrument info including leverage and lot size filters."""
        endpoint = "/v5/market/instruments-info"
        params = {"category": "linear", "symbol": self.symbol}
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params)
            if response.status_code == 200:
                data = response.json()
                if data['retCode'] == 0 and data['result']['list']:
                    return data['result']['list'][0]
            return None
        except Exception as e:
            print(f"Instrument info error: {e}")
            return None

    def get_symbol_info(self) -> dict:
        """Retrieve symbol lot size filters."""
        info = self.get_instrument_info()
        if info and "lotSizeFilter" in info:
            return info["lotSizeFilter"]
        return None

    def get_max_allowed_leverage(self) -> str:
        """Retrieve maximum leverage allowed by the exchange from instrument info."""
        info = self.get_instrument_info()
        if info and "leverageFilter" in info and "maxLeverage" in info["leverageFilter"]:
            return info["leverageFilter"]["maxLeverage"]
        return self.max_leverage

    def set_leverage(self, leverage: str = None) -> requests.Response:
        """Set leverage for the symbol using the exchange's max allowed leverage if not provided."""
        if leverage is None:
            leverage = self.get_max_allowed_leverage()
        params = {
            "category": "linear",
            "symbol": self.symbol,
            "buyLeverage": leverage,
            "sellLeverage": leverage
        }
        response = self.send_post_request("/v5/position/set-leverage", params)
        print("Leverage Response:", response.json())
        return response

    def format_quantity(self, qty: float, step: float) -> str:
        """Format quantity based on step size."""
        decimals = int(round(-math.log(step, 10))) if step < 1 else 0
        formatted = f"{qty:.{decimals}f}"
        return formatted.rstrip('0').rstrip('.') if '.' in formatted else formatted

    def calculate_order_quantity(self) -> str:
        """Calculate order quantity with validation."""
        lot_size_filter = self.get_symbol_info()
        if not lot_size_filter:
            return None
            
        qty_step = float(lot_size_filter['qtyStep'])
        min_qty = float(lot_size_filter['minOrderQty'])
        current_price = self.get_current_price()
        
        if not current_price or current_price <= 0:
            return None
            
        raw_qty = self.usdt_amount / current_price
        adjusted_qty = max(round(raw_qty / qty_step) * qty_step, min_qty)
        
        # Check for minimum notional value (assumed to be 20 USDT)
        if (adjusted_qty * current_price) < 20:
            return None
            
        return self.format_quantity(adjusted_qty, qty_step)

    def create_market_order(self, positionIdx: int = 0) -> requests.Response:
        """Place market order with optional TP/SL."""
        formatted_qty = self.calculate_order_quantity()
        if not formatted_qty:
            print("Invalid quantity calculation")
            return None
            
        order_params = {
            "category": "linear",
            "symbol": self.symbol,
            "side": "Buy" if self.direction == "long" else "Sell",
            "orderType": "Market",
            "qty": formatted_qty,
            "positionIdx": positionIdx
        }
        
        # Add optional take profit and stop loss parameters if set
        if self.take_profit:
            order_params["takeProfit"] = str(self.take_profit)
        if self.stop_loss:
            order_params["stopLoss"] = str(self.stop_loss)
        
        response = self.send_post_request("/v5/order/create", order_params)
        print("Order Response:", response.json())
        return response

# Example usage
if __name__ == "__main__":
    
    bot = BYBITCONFIG(
        api_key="FVxJssLNFyUgq5OTyt",
        api_secret="3PstkL6fJ6vkyTOPCPR0jIGOaoeQQdBv6sDl",
        symbol="BNBUSDT",
        direction="short",
        stop_loss=600,
        take_profit=200,
        investment_per_trade=1,
        amount_multiplier=50,
        amount_allocated=1000
    )
    
    bot.set_leverage()
    bot.create_market_order()
