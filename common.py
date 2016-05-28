from struct import calcsize, pack

# variables shared between the server and the poll
POLL_PORT = 48101
BOX_PORT = 48102
BUF_SIZE = 4096
CODE_NAME_LOC_NUM_ENCODING = '!I30s20sB'
CODE_ENCODING = '!I'
SNACK_ENCODING = '20sB'
SNACK_SIZE = calcsize(SNACK_ENCODING)
HEADER_SIZE = calcsize(CODE_NAME_LOC_NUM_ENCODING)

def combine_structs(s1, s2):
    """
    Combines two structs into one.
    :param s1: first struct we want to combine
    :param s2: second struct we want to combine
    :return: combination of the two 's1s2'
    """
    combine_encoding = '%ds%ds' % (len(s1), len(s2))
    combined = pack(combine_encoding, s1, s2)
    return combined
