# auto-white-reimu

[![PyPI version](https://badge.fury.io/py/auto-white-reimu.svg)](https://badge.fury.io/py/auto-white-reimu)
[![Build Status](https://travis-ci.com/Ledenel/auto-white-reimu.svg?branch=master)](https://travis-ci.com/Ledenel/auto-white-reimu)
[![Coverage Status](https://coveralls.io/repos/github/Ledenel/auto-white-reimu/badge.svg?branch=master)](https://coveralls.io/github/Ledenel/auto-white-reimu?branch=master)

A mahjong library aimed to implement mahjong AIs by imitating white reimu -- a excellent mahjong player.

**Requires Python 3.7 or later.**

## Installation

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

## Testing

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

