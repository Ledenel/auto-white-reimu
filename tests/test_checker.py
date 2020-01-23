from mahjong.record.checker import TenhouChecker
from bs4 import BeautifulSoup


def test_parse():
    html_report = TenhouChecker().parse("http://tenhou.net/0/?log=2018111815gm-00a9-0000-504304e3", 1)
    soup = BeautifulSoup(html_report, "html.parser")
    assert hasattr(soup, 'html')
