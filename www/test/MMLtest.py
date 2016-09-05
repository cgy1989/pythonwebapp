#!/usr/bin/python
# -*- coding: utf8 -*-


class MMLContants(object):
    HW_MAX_LEN_VERSION = 4
    HW_MAX_LEN_TERMINAL = 8
    HW_MAX_LEN_SERVNAME = 8
    HW_MAX_LEN_DLGCTRL = 6
    HW_MAX_LEN_TXID = 8
    HW_MAX_LEN_TXCTRL = 6
    HW_MAX_LEN_TXRSVD = 4
    HW_MAX_MSG_LEN = 65536
    HW_MAX_HEAD_LEN = 56
    HW_MSG_STARTTAG_LEN = 4
    HW_MSG_INFOLEN_LEN = 4
    HW_MSG_CHKSUM_LEN = 8  # for IIN
    HW_MSG_COMM_LEN = 16
    HW_MAX_HB_MSG_LEN = 4
    HW_MAX_HB_CONTENT_LEN = 4
    HW_MAX_HB_CHECKSUM = 4
    HW_HB_MSG_LEN = 16
    HW_MAX_LEN_DLGID = 8
    HW_MAX_LEN_DLGRSVD = 4
    HW_MSG_STARTTAG = '\x60\x53\x43\x60'  # for IIN
    HW_MSG_VERSION = '1.00'
    HW_MSG_TERMINAL = 'internal'
    HW_MSG_TXRSVD = '    '
    HW_MSG_DLGRSVD = '    '
    HW_HB_CONTENT = 'HBHB'


class MsgInfo(object):
    def __init__(self):
        self.cmd = ''
        self.service = ''
        self.login = 0
        self.dlgCtrl = 0
        self.txCtrl = 0
        self.sequence = 0

    def reset(self, strCmd, strService, nLogin, dlgCtrl, ntxCtrl, nSequence):
        if len(strCmd) == 0 or len(strService) == 0 or len(strService) > 8:
            return False
        self.cmd = strCmd
        self.service = strService + ' ' * (8 - len(strService))
        self.login = nLogin
        self.dlgCtrl = dlgCtrl
        self.txCtrl = ntxCtrl
        self.sequence = nSequence


class MMLOperation(object):
    def encode_msg(self, send_msg, sendLen, send_type):
        if send_type == 1:
            send_buffer = MMLContants.HW_MSG_STARTTAG
            send_buffer += hex(MMLContants.HW_HB_MSG_LEN)
            send_buffer += MMLContants.HW_HB_CONTENT
            send_buffer += ','.join(self.get_checksum(MMLContants.HW_MAX_HB_MSG_LEN)).replace(',', '')

    def decode_msg(self, ):
        pass

    def get_checksum(self, buf, len):
        res = [0, 0, 0, 0, 0, 0, 0, 0]
        i = 0
        while i < len:
            res[0] ^= ord(buf[i + 0:i + 1])
            res[1] ^= ord(buf[i + 1:i + 2])
            res[2] ^= ord(buf[i + 2:i + 3])
            res[3] ^= ord(buf[i + 3:i + 4])
            i += 4
        res[0] = ~res[0]
        res[1] = ~res[1]
        res[2] = ~res[2]
        res[3] = ~res[3]

        i = 7
        while i >= 0:
            if i % 2:
                res[i] = (res[i / 2] & 0X0F) + ord('0')
            else:
                res[i] = ((res[i / 2] >> 4) & 0X0F) + ord('0')
            if res[i] > ord('9'):
                    res[i] = res[i] + ord('A') - ord('0') - 10
            i -= 1

        res_c = [chr(x) for x in res]
        return res_c


if __name__ == '__main__':
    print MMLOperation().get_checksum('HBHB', 4)
    pass
