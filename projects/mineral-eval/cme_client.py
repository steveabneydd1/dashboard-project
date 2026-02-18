"""
CME WebSocket client to fetch real-time WTI and Henry Hub forward curves.
Handles authentication, price fetching, cap/floor logic, and year 4 flat perpetuity.
"""

import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from cme_config import load_cme_credentials

try:
    import websocket
except ImportError:
    websocket = None


class CMEClient:
    """
    Connect to CME WebSocket API to fetch WTI (CL) and Henry Hub (NG) forward curves.
    """
    
    def __init__(self):
        self.credentials = load_cme_credentials()
        self.ws = None
        self.prices = {}  # {contract: {date: (gas_price, oil_price)}}
        self.lock = threading.Lock()
        self.authenticated = False
        self.connected = False
    
    def connect(self):
        """Connect to CME WebSocket and authenticate."""
        if websocket is None:
            raise ImportError("websocket-client not installed. Run: pip install websocket-client")
        
        try:
            endpoint = self.credentials['endpoint']
            self.ws = websocket.WebSocketApp(
                endpoint,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
            )
            
            # Run in background thread
            self.thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            self.thread.start()
            
            # Wait for connection
            max_retries = 30
            for i in range(max_retries):
                if self.connected:
                    break
                time.sleep(0.1)
            
            if not self.connected:
                raise Exception("Failed to connect to CME WebSocket")
            
        except Exception as e:
            raise RuntimeError(f"CME connection failed: {e}")
    
    def _on_open(self, ws):
        """Authenticate after connection opens."""
        self.connected = True
        auth_msg = {
            "user": self.credentials['username'],
            "password": self.credentials['password'],
        }
        ws.send(json.dumps(auth_msg))
    
    def _on_message(self, ws, message):
        """Process incoming market data."""
        try:
            data = json.loads(message)
            
            # Check for authentication response
            if "authenticated" in data:
                self.authenticated = data["authenticated"]
                if self.authenticated:
                    self._request_contracts()
                return
            
            # Process price data
            with self.lock:
                if "contract" in data and "prices" in data:
                    contract = data["contract"]
                    self.prices[contract] = data["prices"]
        
        except json.JSONDecodeError:
            pass
    
    def _on_error(self, ws, error):
        """Handle connection errors."""
        print(f"CME WebSocket error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle connection close."""
        self.connected = False
        self.authenticated = False
    
    def _request_contracts(self):
        """Request WTI (CL) and Henry Hub (NG) contracts."""
        if self.ws:
            request = {
                "action": "subscribe",
                "contracts": ["CL", "NG"],  # WTI Crude, Henry Hub Natural Gas
            }
            self.ws.send(json.dumps(request))
    
    def get_forward_curve(self) -> Dict[str, Dict]:
        """
        Get forward curve for WTI and NG.
        Returns: {
            'WTI': {'2026-02': price_per_bbl, ...},
            'NG': {'2026-02': price_per_mcf, ...},
        }
        """
        if not self.authenticated:
            raise RuntimeError("Not authenticated with CME")
        
        with self.lock:
            curve = {
                'WTI': self.prices.get('CL', {}),
                'NG': self.prices.get('NG', {}),
            }
        
        return curve
    
    def close(self):
        """Close WebSocket connection."""
        if self.ws:
            self.ws.close()
            self.connected = False
            self.authenticated = False


def fetch_cme_prices() -> Dict[str, Dict[str, float]]:
    """
    Fetch real-time CME prices for WTI and Henry Hub.
    Returns: {'WTI': {date: price}, 'NG': {date: price}}
    """
    client = CMEClient()
    try:
        client.connect()
        time.sleep(2)  # Wait for data to arrive
        return client.get_forward_curve()
    finally:
        client.close()


def build_monthly_price_deck(
    gas_prices: Dict[str, float],
    oil_prices: Dict[str, float],
    cap_gas: Optional[float] = None,
    floor_gas: Optional[float] = None,
    cap_oil: Optional[float] = None,
    floor_oil: Optional[float] = None,
    year4_flat: bool = False,
) -> Dict[Tuple[int, int], Tuple[float, float]]:
    """
    Build monthly price deck from forward curves with cap/floor logic.
    
    Args:
        gas_prices: Dict[date_str, price] for Henry Hub ($/MMBtu)
        oil_prices: Dict[date_str, price] for WTI ($/Bbl)
        cap_gas: Maximum gas price ($/MMBtu)
        floor_gas: Minimum gas price ($/MMBtu)
        cap_oil: Maximum oil price ($/Bbl)
        floor_oil: Minimum oil price ($/Bbl)
        year4_flat: If True, average year 4 and hold flat in perpetuity
    
    Returns:
        Dict[Tuple[year, month], Tuple[gas_price, oil_price]]
    """
    
    deck = {}
    
    # Parse and sort prices by date
    gas_sorted = sorted([(k, v) for k, v in gas_prices.items()])
    oil_sorted = sorted([(k, v) for k, v in oil_prices.items()])
    
    # Extract year 4 values (months 37-48) if needed
    year4_gas = None
    year4_oil = None
    
    if year4_flat:
        y4_gas_vals = []
        y4_oil_vals = []
        month = 1
        for (gas_date, gas_price), (oil_date, oil_price) in zip(gas_sorted, oil_sorted):
            if 37 <= month <= 48:  # Year 4 is months 37-48
                y4_gas_vals.append(gas_price)
                y4_oil_vals.append(oil_price)
            month += 1
        
        if y4_gas_vals:
            year4_gas = sum(y4_gas_vals) / len(y4_gas_vals)
        if y4_oil_vals:
            year4_oil = sum(y4_oil_vals) / len(y4_oil_vals)
    
    # Build deck
    month = 1
    for (gas_date, gas_price), (oil_date, oil_price) in zip(gas_sorted, oil_sorted):
        # Apply year 4 flat
        if year4_flat and month > 48 and year4_gas and year4_oil:
            gas_price = year4_gas
            oil_price = year4_oil
        
        # Apply caps and floors
        if cap_gas is not None:
            gas_price = min(gas_price, cap_gas)
        if floor_gas is not None:
            gas_price = max(gas_price, floor_gas)
        if cap_oil is not None:
            oil_price = min(oil_price, cap_oil)
        if floor_oil is not None:
            oil_price = max(oil_price, floor_oil)
        
        # Parse year/month from date string (e.g., "2026-02")
        try:
            year, month_str = gas_date.split("-")
            year = int(year)
            month = int(month_str)
            deck[(year, month)] = (gas_price, oil_price)
        except:
            pass
    
    return deck


if __name__ == "__main__":
    # Test: Fetch prices
    try:
        prices = fetch_cme_prices()
        print("✅ CME prices fetched successfully")
        print(f"WTI samples: {list(prices['WTI'].items())[:3]}")
        print(f"NG samples: {list(prices['NG'].items())[:3]}")
    except Exception as e:
        print(f"❌ Error: {e}")
