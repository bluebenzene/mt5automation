# multiple account place order in mt5 
it can run multiple accounts for that you need to clone the folder again that installed in the program files. Only runs in windows. 


`1a = account number of first`
`2a = account number of second`
`3a =account number of third`

# sample config.ini


## messages to buy 
`[{"symbol":"GBPUSD","side":"buy","1alot":"1","2alot":"2","3alot":"3"}]`

## message to close 
`[{"symbol":"BTCUSDm","close":"all"}]`

## package
`pyinstaller --onefile --hidden-import=MetaTrader5 --hidden-import=flask --hidden-import=numpy server.py`