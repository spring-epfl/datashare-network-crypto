"""
Hash utilities for cuckoo filters to generate fingerprints.

Generate FNV64 hash based on http://isthe.com/chongo/tech/comp/fnv/
"""


HASH_CODE_OFFSET = 8


def _int_to_bytes(x):
    return x.to_bytes((x.bit_length() + 7) // 8, byteorder='big')


def _bytes_to_int(x):
    return int.from_bytes(x, byteorder='big')


def fingerprint(data, size):
    """
    Get fingerprint of a string using FNV 64-bit hash and truncate it to
    'size' bytes.

    :param data: Data to get fingerprint for
    :param size: Size in bytes to truncate the fingerprint
    :return: fingerprint of 'size' bytes
    """
    return _bytes_to_int(data[:size])


def hash_code(data):
    """Generate hash code using builtin hash() function.

    :param data: Data to generate hash code for
    """
    return _bytes_to_int(data[HASH_CODE_OFFSET:HASH_CODE_OFFSET+4])
