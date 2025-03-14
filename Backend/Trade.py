import requests
import time
import hmac
import hashlib
import json
import math

# --------------------------------------------------------------------------------
# Utility functions (These remain exactly the same in logic as the original code).
# --------------------------------------------------------------------------------

def get_server_timestamp(base_url: str) -> int:
    """
    Retrieve the server timestamp in milliseconds.
    If unable to fetch from the server, use local time.
    """
    try:
        response = requests.get(f"{base_url}/v5/market/time")
        if response.status_code == 200:
            data = response.json()
            time_nano = int(data["result"]["timeNano"])
            return time_nano // 1_000_000
        else:
            return int(time.time() * 1000)
    except Exception as e:
        print(f"Error fetching server time: {e}")
        return int(time.time() * 1000)

def sign_payload(api_secret: str, timestamp: str, api_key: str, recv_window: str, json_payload: str) -> str:
    """
    Create a signature for the payload using HMAC SHA256.
    """
    signature_payload = f"{timestamp}{api_key}{recv_window}{json_payload}"
    signature = hmac.new(
        api_secret.encode("utf-8"),
        signature_payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return signature

def send_post_request(
    base_url: str,
    endpoint: str,
    api_key: str,
    api_secret: str,
    recv_window: str,
    params: dict
) -> requests.Response:
    """
    Send a POST request with proper headers and HMAC signature.
    """
    timestamp = str(get_server_timestamp(base_url))
    sorted_params = dict(sorted(params.items()))
    json_payload = json.dumps(sorted_params, separators=(',', ':'))
    signature = sign_payload(api_secret, timestamp, api_key, recv_window, json_payload)

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "X-BAPI-SIGN": signature,
        "Content-Type": "application/json"
    }
    return requests.post(f"{base_url}{endpoint}", data=json_payload, headers=headers)

def get_current_price(base_url: str, symbol: str) -> float:
    """
    Retrieve the current market price for the given symbol.
    """
    endpoint = "/v5/market/tickers"
    params = {"category": "linear", "symbol": symbol}
    try:
        response = requests.get(f"{base_url}{endpoint}", params=params)
        if response.status_code == 200:
            data = response.json()
            return float(data['result']['list'][0]['lastPrice'])
        return None
    except Exception as e:
        print(f"Price fetch error: {e}")
        return None

def get_instrument_info(base_url: str, symbol: str) -> dict:
    """
    Retrieve full instrument info (including leverage and lot size filters).
    """
    endpoint = "/v5/market/instruments-info"
    params = {"category": "linear", "symbol": symbol}
    try:
        response = requests.get(f"{base_url}{endpoint}", params=params)
        if response.status_code == 200:
            data = response.json()
            if data['retCode'] == 0 and data['result']['list']:
                return data['result']['list'][0]
        return None
    except Exception as e:
        print(f"Instrument info error: {e}")
        return None

def get_symbol_info(base_url: str, symbol: str) -> dict:
    """
    Retrieve the lot size filters for the given symbol.
    """
    info = get_instrument_info(base_url, symbol)
    if info and "lotSizeFilter" in info:
        return info["lotSizeFilter"]
    return None

def get_max_allowed_leverage(base_url: str, symbol: str) -> str:
    """
    Retrieve the maximum leverage allowed by the exchange for the given symbol.
    If unavailable, return a default max leverage value of '50'.
    """
    info = get_instrument_info(base_url, symbol)
    if info and "leverageFilter" in info and "maxLeverage" in info["leverageFilter"]:
        return info["leverageFilter"]["maxLeverage"]
    return "50"  # Fallback if not found

def format_quantity(qty: float, step: float) -> str:
    """
    Format quantity based on the step size.
    """
    decimals = int(round(-math.log(step, 10))) if step < 1 else 0
    formatted = f"{qty:.{decimals}f}"
    if '.' in formatted:
        return formatted.rstrip('0').rstrip('.')
    return formatted

def validate_direction(direction: str) -> None:
    """
    Validate direction to be either 'long' or 'short'. Raise ValueError otherwise.
    """
    if direction.lower() not in ["long", "short"]:
        raise ValueError("Direction must be 'long' or 'short'")

def compute_usdt_amount(
    amount_allocated: float,
    investment_per_trade: float,
    amount_multiplier: float
) -> float:
    """
    Calculate dynamic USDT amount based on allocated capital,
    trade percentage, and multiplier.
    """
    return (amount_allocated * (investment_per_trade / 100)) * amount_multiplier

def set_leverage_action(
    base_url: str,
    api_key: str,
    api_secret: str,
    recv_window: str,
    symbol: str,
    desired_max_leverage: str = None
) -> requests.Response:
    """
    Set leverage for the symbol using the exchange's max allowed leverage if none provided.
    """
    if not desired_max_leverage:
        desired_max_leverage = get_max_allowed_leverage(base_url, symbol)
    params = {
        "category": "linear",
        "symbol": symbol,
        "buyLeverage": desired_max_leverage,
        "sellLeverage": desired_max_leverage
    }
    response = send_post_request(
        base_url=base_url,
        endpoint="/v5/position/set-leverage",
        api_key=api_key,
        api_secret=api_secret,
        recv_window=recv_window,
        params=params
    )
    print("Leverage Response:", response.json())
    return response

def calculate_order_quantity(
    base_url: str,
    symbol: str,
    usdt_amount: float
) -> str:
    """
    Calculate the order quantity with validation against lot size and notional constraints.
    """
    lot_size_filter = get_symbol_info(base_url, symbol)
    if not lot_size_filter:
        return None
        
    qty_step = float(lot_size_filter['qtyStep'])
    min_qty = float(lot_size_filter['minOrderQty'])
    current_price = get_current_price(base_url, symbol)
    
    if not current_price or current_price <= 0:
        return None
        
    raw_qty = usdt_amount / current_price
    adjusted_qty = max(round(raw_qty / qty_step) * qty_step, min_qty)
    
    # Check for a minimum notional value (assumed to be 20 USDT for example)
    if (adjusted_qty * current_price) < 20:
        return None
        
    return format_quantity(adjusted_qty, qty_step)

def create_market_order_action(
    base_url: str,
    api_key: str,
    api_secret: str,
    recv_window: str,
    symbol: str,
    direction: str,
    stop_loss: float,
    take_profit: float,
    usdt_amount: float,
    position_idx: int = 0
) -> requests.Response:
    """
    Place a market order with optional take profit and stop loss.
    """
    formatted_qty = calculate_order_quantity(base_url, symbol, usdt_amount)
    if not formatted_qty:
        print("Invalid quantity calculation")
        return None

    order_params = {
        "category": "linear",
        "symbol": symbol,
        "side": "Buy" if direction.lower() == "long" else "Sell",
        "orderType": "Market",
        "qty": formatted_qty,
        "positionIdx": position_idx
    }
    
    if take_profit:
        order_params["takeProfit"] = str(take_profit)
    if stop_loss:
        order_params["stopLoss"] = str(stop_loss)
    
    response = send_post_request(
        base_url=base_url,
        endpoint="/v5/order/create",
        api_key=api_key,
        api_secret=api_secret,
        recv_window=recv_window,
        params=order_params
    )
    print("Order Response:", response.json())
    return response

# --------------------------------------------------------------------------------
# Main script usage example (same logic flow, no class usage, but uses the 
# exchange's maximum offered leverage by default).
# --------------------------------------------------------------------------------

def main():
    api_key = "FVxJssLNFyUgq5OTyt"
    api_secret = "3PstkL6fJ6vkyTOPCPR0jIGOaoeQQdBv6sDl"
    base_url = "https://api-demo.bybit.com"
    symbol = "BTCUSDT"
    direction = "long"
    stop_loss = 83000
    take_profit = 85000
    investment_per_trade = 0.7874
    amount_multiplier = 50
    amount_allocated = 1000
    recv_window = "5000"
    desired_max_leverage = None  

    validate_direction(direction)
    usdt_amount = compute_usdt_amount(amount_allocated, investment_per_trade, amount_multiplier)

    # ✅ Set Leverage
    set_leverage_action(
        base_url=base_url,
        api_key=api_key,
        api_secret=api_secret,
        recv_window=recv_window,
        symbol=symbol,
        desired_max_leverage=desired_max_leverage
    )

    # ✅ Place Market Order
    create_market_order_action(
        base_url=base_url,
        api_key=api_key,
        api_secret=api_secret,
        recv_window=recv_window,
        symbol=symbol,
        direction=direction,
        stop_loss=stop_loss,
        take_profit=take_profit,
        usdt_amount=usdt_amount,
        position_idx=0
    )

if __name__ == "__main__":
    main()
