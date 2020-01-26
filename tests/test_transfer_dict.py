from mahjong.record.utils.builder import TransferDict


def test_set():
    trans = TransferDict({
        'a': {
            '1': 'z'
        },
        'b': {
            '2': {
                '3': 'y'
            }
        },
    })
    trans_2 = trans['a'].set('1', 'x')
    assert trans['a']['1'] == 'z'
    assert trans['b']['2']['3'] == 'y'

    assert trans_2['a']['1'] == 'x'
    assert trans_2['b']['2']['3'] == 'y'


def test_set_same_dict():
    trans = TransferDict({
        'a': {
            '1': 'z'
        },
        'b': {
            '2': {
                '3': 'y'
            }
        },
    })
    trans_2 = trans['a'].set('2', 'p')
    trans_3 = trans_2['a'].set('3', 'c')
    assert trans['a']['1'] == 'z'
    assert trans['b']['2']['3'] == 'y'

    assert trans_2['a']['1'] == 'z'
    assert trans_2['b']['2']['3'] == 'y'
    assert trans_2['a']['2'] == 'p'

    assert trans_3['a']['1'] == 'z'
    assert trans_3['b']['2']['3'] == 'y'
    assert trans_3['a']['2'] == 'p'
    assert trans_3['a']['3'] == 'c'


def test_trans_differ():
    trans = TransferDict({
        'a': {
            '1': 'x'
        },
        'b': {
            '2': 'y'
        },
    })
    trans_2 = trans['a'].set('3', 'p')
    trans_3 = trans_2['b'].set('4', 'q')

    assert trans['a']['1'] == 'x'
    assert trans['b']['2'] == 'y'

    assert trans_2['a']['1'] == 'x'
    assert trans_2['b']['2'] == 'y'
    assert trans_2['a']['3'] == 'p'

    assert trans_3['a']['1'] == 'x'
    assert trans_3['b']['2'] == 'y'
    assert trans_3['a']['3'] == 'p'
    assert trans_3['b']['4'] == 'q'
