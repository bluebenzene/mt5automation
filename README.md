# multiple account place order in mt5 

## messages to buy 
`[{"symbol":"GBPUSD","side":"buy","1alot":"1","2alot":"2","3alot":"3"}]`

## message to close 
`[{"symbol":"BTCUSDm","close":"all"}]`

## package
`pyinstaller --onefile --hidden-import=MetaTrader5 --hidden-import=flask --hidden-import=numpy server.py`