# auto-white-reimu

A mahjong library aimed to implement mahjong AIs by imitating white reimu -- a excellent mahjong player.

**Requires Python 3.7 or later.**

## features

### win-rate-demo

A demo for estimating win rate of a hand (using Monte Carlo method).



To run the demo, type command `python mahjong/win_rate_demo.py`.

A example of input hand should be like this:

`2345678p2345777s`


### tenhou-record-check

This tools helps you to check your wining-efficiency(牌効率) during a play.

To run, clone the sources and install dependencies by typing

`python setup.py install`

in the root directory.

then, you can run the tools with

`python mahjong/tenhou_record_check.py`

then type your tenhou.net log url (like`http://tenhou.net/0/?log=2019012600gm-0089-0000-100908f0&tw=0`)
and your tenhou.net Playing name(like`Ledenel`, **not the id you used to login tenhou.net and play**)

it will generate a html report for easy checking.