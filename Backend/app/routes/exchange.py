from flask import Blueprint, request, jsonify
import requests
import hmac
import hashlib
import base64
from datetime import datetime, UTC
from urllib.parse import urljoin

exchange_bp = Blueprint('exchange', __name__)

class OKXClient:
    def __init__(self, api_key, api_secret, passphrase):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.base_url = "https://www.okx.com"
        self.is_demo = True  # Only allow demo trading

    def _get_timestamp(self):
        return datetime.now(UTC).isoformat(timespec='milliseconds').replace("+00:00", "Z")

    def _sign(self, timestamp, method, request_path, body=''):
        message = str(timestamp) + method.upper() + request_path + str(body)
        mac = hmac.new(
            bytes(self.api_secret, 'utf-8'), 
            bytes(message, 'utf-8'), 
            hashlib.sha256
        )
        return base64.b64encode(mac.digest()).decode('utf-8')

    def test_connection(self):
        method = 'GET'
        request_path = '/api/v5/account/balance'
        url = urljoin(self.base_url, request_path)
        
        timestamp = self._get_timestamp()
        signature = self._sign(timestamp, method, request_path)
        
        headers = {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
        
        if self.is_demo:
            headers['x-simulated-trading'] = '1'  # Ensure demo trading is enforced
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data['code'] == '0':
                return True
            return False
        except:
            return False

@exchange_bp.route('/TestConnection', methods=['POST'])
def balance():
    data = request.get_json()
    if not data or not all(k in data for k in ('api_key', 'api_secret', 'passphrase')):
        return jsonify({'error': 'Missing required API credentials'}), 400
    
    client = OKXClient(
        api_key=data['api_key'],
        api_secret=data['api_secret'],
        passphrase=data['passphrase']
    )
    
    try:
        if client.test_connection():
            return jsonify({'success': True})
        else:
            return jsonify({'success': False})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
