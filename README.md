# Get Alert from Tradingview and place order on MetaTrader 5 
this program can place orders in Metatrader 5 terminal automatically when receive message from Tradingview . 

## Install 
`pip install -r requirements.txt`
open port 80 




## multiple account place order in mt5 
it can run multiple accounts for that you need to clone the folder again that installed in the program files. Only runs in windows. 


`1a = account number of first`
`2a = account number of second`
`3a =account number of third`

# sample config.ini
```
[Account1]
id = 116121298
password = !A&njsdq8XW
server = Exness-MT5Trial6
path = C:\\Program Files\\MetaTrader 5 EXNESSuser1\\terminal64.exe

[Account2]
id = 1244123
password = j6KiffsdU!
server = Exness-MT5Trial7
path = C:\\Program Files\\MetaTrader 5 EXNESSuser2\\terminal64.exe

[Account3]
id = 88521219
password = Tiiojioi23d
server = Exness-MT5Real15
path = C:\\Program Files\\MetaTrader 5 EXNESS\\terminal64.exe
```

## messages to buy 
`[{"symbol":"GBPUSD","side":"buy","1alot":"1","2alot":"2","3alot":"3"}]`

## message to close 
`[{"symbol":"BTCUSDm","account":"116437666","close":"all"}]`

## package
`pyinstaller --onefile --hidden-import=MetaTrader5 --hidden-import=flask --hidden-import=numpy server.py`