# Arduino Display Stats For RaspberryPi

## What it does?
It's Python3 script for grep info from raspberry pi system (raspbian) and send it to ardruino display


## Algo
1) Grep info from system about: CPU temp and load, Ram used memory
2) Send it to Arduino with specific format (See below)
3) Arduino send it to display LCD 1604

## Format
1) Every field must be int.
2) Every field required symbol ";" after value (except last value).
```
0 - CPU TEMP
1 - GPU TEMP
2 - 0 (Reserved)
3 - 0 (Reserved)
4 - CPU LOAD
5 - GPU LOAD
6 - RAM USE
7 - GPU USE
8 - "E" - flag for end data
```
