# -*-coding:utf-8-*-



class IDEncryptor(object):
    DEFAULT_KEY = 0x6CFB18E2
    LOW_16_MASK = 0xFFFF
    HALF_SHIFT = 16
    NUM_ROUNDS = 4
    SIGNED_FLAG = 1 << 31
    LARGE_VAL = 1 << 32
    INTEGER_MAX_VALUE = 0x7fffffff

    def __init__(self):
        self.mRoundKeys = [None] * IDEncryptor.NUM_ROUNDS
        self._set_key(IDEncryptor.DEFAULT_KEY)

    def _set_key(self, key):
        self.mRoundKeys[0] = key & IDEncryptor.LOW_16_MASK
        self.mRoundKeys[1] = ~(key & IDEncryptor.LOW_16_MASK)
        self.mRoundKeys[2] = rshift(key, IDEncryptor.HALF_SHIFT)
        self.mRoundKeys[3] = ~(rshift(key, IDEncryptor.HALF_SHIFT))

    def _feistel_round(self, num, round):
        num ^= self.mRoundKeys[round]
        num *= num
        num = truncate_int_like_java(num)
        return (rshift(num, IDEncryptor.HALF_SHIFT)) ^ (num & IDEncryptor.LOW_16_MASK)

    def encipher(self, plain):
        rhs = plain & IDEncryptor.LOW_16_MASK
        lhs = rshift(plain, IDEncryptor.HALF_SHIFT)
        for i in range(len(self.mRoundKeys)):
            if i > 0:
                lhs, rhs = rhs, lhs
            rhs ^= self._feistel_round(lhs, i)
        value = (lhs << IDEncryptor.HALF_SHIFT) + (rhs & IDEncryptor.LOW_16_MASK)
        if value < 0:
            value += IDEncryptor.LARGE_VAL
        return value

    def decipher(self, value):
        if value > IDEncryptor.INTEGER_MAX_VALUE:
            value -= IDEncryptor.LARGE_VAL

        rhs = value & IDEncryptor.LOW_16_MASK
        lhs = rshift(value, IDEncryptor.HALF_SHIFT)
        for i in range(IDEncryptor.NUM_ROUNDS):
            if i > 0:
                lhs, rhs = rhs, lhs
            rhs ^= self._feistel_round(lhs, IDEncryptor.NUM_ROUNDS - 1 - i)
        ret = truncate_int_like_java(lhs << IDEncryptor.HALF_SHIFT) \
              + (rhs & IDEncryptor.LOW_16_MASK)
        return ret

    def encrypt(self, _id):
        try:
            return str(self.encipher(int(_id)))
        except Exception:
            return str(_id)

    def decrypt(self, encrypted):
        return self.decipher(int(encrypted))


def rshift(val, n):
    return val >> n if val >= 0 else (val + 0x100000000) >> n


def truncate_int_like_java(number):
    if number == 0:
        return 0
    if number & 0x80000000 == 0:
        return number & 0x7FFFFFFF
    else:
        return -(~(number & 0x7FFFFFFF) + 1 + 0x80000000)


if __name__ == "__main__":
    id_encryptor = IDEncryptor()
    print(id_encryptor.decrypt(20913209))
