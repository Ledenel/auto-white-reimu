def number_list(int_string: str, split=','):
    return [int(float(x))
            if int(float(x)) == float(x)
            else float(x)
            for x in int_string.split(split)]
