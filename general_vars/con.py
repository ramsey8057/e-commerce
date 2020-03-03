con = None


def set_con(new_con):
    global con
    con = new_con
    return con


def get_con():
    global con
    return con
