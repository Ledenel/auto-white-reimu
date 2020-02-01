# auto-white-reimu

[![PyPI version](https://badge.fury.io/py/auto-white-reimu.svg)](https://badge.fury.io/py/auto-white-reimu)
[![Build Status](https://travis-ci.com/Ledenel/auto-white-reimu.svg?branch=master)](https://travis-ci.com/Ledenel/auto-white-reimu)
[![Coverage Status](https://coveralls.io/repos/github/Ledenel/auto-white-reimu/badge.svg?branch=master)](https://coveralls.io/github/Ledenel/auto-white-reimu?branch=master)

A mahjong library aimed to implement mahjong AIs by imitating white reimu -- a excellent mahjong player.

**Requires Python 3.7 or later.**

## Installation

## Pre-built

If you only want the features, there are pre-built binaries for each feature:
[release](https://github.com/Ledenel/auto-white-reimu/releases)

.exe is for Windows and binary with no extention is for Mac OS.

> Running first time is usually slower (due to some intitalization in PyInstaller). 

## For Developers

Install python 3.7 or later, then just use pip:

`pip install auto-white-reimu`

Alternatively, you can install from source by 

`python setup.py install`

in the project root directory.

## Features

### win-rate-demo

A demo for estimating win rate of a hand (using Monte Carlo method).

**After installation**, you can run the tools by

`mahjong-win-rate`.

A example of input hand should be like this:

`2345678p2345777s`


### tenhou-record-check

This tools helps you to check your wining-efficiency(牌効率) during a play.


**After installation**, you can run the tools with

`tenhou-check`

then type your tenhou.net log url (like`http://tenhou.net/0/?log=2019012600gm-0089-0000-100908f0&tw=0`) and 
follow the hint.

it will generate a html report for easy checking.

You could also use it programmatically:

```python
from mahjong.record.checker import TenhouChecker
filename, results = TenhouChecker().parse(
    "http://tenhou.net/0/?log=2018111815gm-00a9-0000-504304e3", 
    player_index=1,
    timeout=15,
    generate_filename=True
)
with open(filename, "w", encoding='utf-8') as f:
    f.write(results)
```

## universe-paifu-convert

This converter extract paifus as a universal format, to csv files for easy analysis.

**After installation**, you can run the tools with

`paifu-extract`

Now support tenhou.net only.

**IT IS JUST A DEMO TO SHOW THE CONCEPTS, TRANSLATED COMMANDS AND STATES ARE NEITHER COMPLETE NOR CORRECT YET!**

Type your tenhou.net log url (like`http://tenhou.net/0/?log=2019012600gm-0089-0000-100908f0&tw=0`).

For APIs, see [code here](https://github.com/Ledenel/auto-white-reimu/blob/master/mahjong/universe_paifu_convert.py). 

Extra APIs are provided to analyse the csv with usage examples below:
```python
import pandas as pd
from mahjong.record.universe.command import GameCommand
df = pd.read_csv("command_list.csv")
# clean up df, make states as python value
df = df.apply(GameCommand.pandas_columns_clean, axis="columns")
# extract all state changes to columns
df_state = df.pivot(columns="property", values="state")
# fill in all state to get exact state for each command executed.
df_state = df_state.ffill()
```

### Extending universal paifu format

See pull request [here](https://github.com/Ledenel/auto-white-reimu/pull/45) for more details.

# Testing

you could run test by executing `pip install .[test]` at root dir, this would install all dependence for you.

and run `pytest` in the root directory.

For PyCharm users, we provide some shared configuration in 
`runConfigurations.zip`. 

Unzip these .xml settings and put them in your project 
`.idea/runConfigurations/` directory. Then you would see it in PyCharm menu
`Run -> Edit Configurations`. You may need to adjust Python Interpreter to your own environment in these settings.



**PLEASE DON'T TRACK THESE .XML SETTING IN VERSION CONTROL.**

# ACKNOWLEDGEMENT

Thanks for tile image provided by **Void**.

Using mahjong image in this project is fine.
For other usage, please concat him via QQ: 1246465300

