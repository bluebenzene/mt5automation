from flask import Flask, request, jsonify,abort
import logging
import MetaTrader5 as mt5
import configparser

ALLOWED_IPS = ['52.89.214.238', '34.212.75.30','54.218.53.128','52.32.178.7','127.0.0.1','103.76.210.196','10.211.55.2']

# Configure logging
logging.basicConfig(filename='serverlog.txt', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')
deviation = 20
app = Flask(__name__)
accounts = []
for section in config.sections():
    accounts.append({
        "id": config[section]['id'],
        "password": config[section]['password'],
        "server": config[section]['server'],
        "path": config[section]['path'],
    })


def initialize_mt5_connections():
    for account in accounts:
        if not mt5.initialize(path=account['path']):
            logger.error(f"Failed to initialize MT5 for account {account['id']}, error code = {mt5.last_error()}")
            continue

        # Convert account ID to integer
        account_id = int(account['id'])

        authorized = mt5.login(account_id, account['password'], account['server'])
        if authorized:
            logger.info(f"Connected to account #{account_id} successfully")
        else:
            logger.error(f"Failed to connect at account #{account_id}, error code: {mt5.last_error()}")

        mt5.shutdown()

def close_positions(account, symbol):
    # Initialize MT5 for the specific account
    if not mt5.initialize(path=account['path']):
        logger.error(f"initialize() failed for account {account['id']}, error code: {mt5.last_error()}")
        return  # Exit if initialization fails

    # Login to the account
    if not mt5.login(int(account['id']), account['password'], account['server']):
        logger.error(f"Failed to login to account {account['id']}, error code: {mt5.last_error()}")
        mt5.shutdown()
        return  # Exit if login fails

    mt5.symbol_select(symbol, True)
    # Get all open positions
    positions = mt5.positions_get(symbol=symbol)
    if positions is None:
        logger.info(f"No positions to close for symbol {symbol} in account {account['id']}")
    else:
        # Close all positions for the specified symbol
        for position in positions:
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": position.volume,
                "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                "position": position.ticket,
                "price": mt5.symbol_info_tick(symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).ask,
                "deviation": 20,
                "magic": 0,
                "comment": "Close position via webhook",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            result = mt5.order_send(close_request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Failed to close position {position.ticket} for account {account['id']}, retcode: {result.retcode}")
            else:
                logger.info(f"Position {position.ticket} closed for account {account['id']}")

    mt5.shutdown()

def place_order(account_id, symbol, lot, order_type=mt5.ORDER_TYPE_BUY):
    # Fetch the account details
    account = next(acc for acc in accounts if acc['id'] == account_id)

    # Reinitialize MT5 for the specific account with the path to its terminal
    if not mt5.initialize(path=account['path']):
        logger.error("initialize() failed, error code =", mt5.last_error())
        return False

    # Login to the specified account
    if not mt5.login(int(account['id']), account['password'], account['server']):
        logger.error(f"Failed to login to account {account_id}, error code: {mt5.last_error()}")
        mt5.shutdown()
        return False

    # Ensure the symbol is selected to retrieve current price
    mt5.symbol_select(symbol,True)

    # Prepare and send the order
    if order_type == mt5.ORDER_TYPE_BUY:
        price = mt5.symbol_info_tick(symbol).ask  # Use 'ask' price for buy orders
    else:
        price = mt5.symbol_info_tick(symbol).bid  # Use 'bid' price for sell orders

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)

    # Check the execution result
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logger.error(f"Order_send failed for account {account_id}, retcode={result.retcode}")
        mt5.shutdown()
        return False
    else:
        logger.info(f"Order_send done for account {account_id}, {result}")
        mt5.shutdown()
        return True
    
@app.route('/webhook', methods=['POST'])
def webhook():
    requester_ip = request.remote_addr
    if requester_ip not in ALLOWED_IPS:
        logger.error(f"Unauthorized access from IP: {requester_ip}")
        abort(403)
    data = request.json
    message = data[0]
    
    logger.info(f"Received message: {message}")

    symbol = message.get('symbol')
    side = message.get('side')
    order_type = mt5.ORDER_TYPE_BUY if side == 'buy' else mt5.ORDER_TYPE_SELL

    for account in accounts:
        lot_key = f"{account['id']}lot"
        lot_size = message.get(lot_key)
        if lot_size:
            # Convert the lot size to float and proceed only if it is positive
            lot_size = float(lot_size)
            if lot_size > 0:
                logger.info(f"Processing {side} order for account {account['id']} with lot size {lot_size}")

                # Close all positions for this account and symbol
                close_positions(account, symbol)

                # Place the new order
                success = place_order(account['id'], symbol, lot_size, order_type=order_type)
                if success:
                    logger.info(f"Order placed successfully for account {account['id']}")
                else:
                    logger.error(f"Failed to place order for account {account['id']}")

    return jsonify({"message": "Orders processed"}), 200


if __name__ == '__main__':
    initialize_mt5_connections()  # Initialize MT5 connections
    print("server is running check log file for more info")
    app.run(debug=False, host='0.0.0.0', port=80)
