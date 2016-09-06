#!/usr/bin/python
# -*- coding: utf8 -*-

import socket


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
    HW_MSG_TXRSVD = '     '
    HW_MSG_DLGRSVD = '    '
    HW_HB_CONTENT = 'HBHB'


class MsgInfo(object):
    def __init__(self):
        self.cmd = ''
        self.service = ''
        self.snLogin = 0
        self.dlgCtrl = 0
        self.txCtrl = 0
        self.sequence = 0

    def set_value(self, strCmd, strService, nLogin, dlgCtrl, ntxCtrl, nSequence):
        if len(strCmd) == 0 or len(strService) == 0 or len(strService) > 8:
            return False
        self.cmd = strCmd
        self.service = strService + ' ' * (8 - len(strService))
        self.snLogin = nLogin
        self.dlgCtrl = dlgCtrl
        self.txCtrl = ntxCtrl
        self.sequence = nSequence


class MMLOperation(object):
    user_name = 'jiake'
    password = 'Jiake_aaa1'
    mml_cmd = 'QUERY C280 USER:LOGINNAME="yd18724403231@-1"'

    def __init__(self):
        self.nlogin = False
        self.nRadiusMsg = MsgInfo()
        self.webclient = WebClient()

    def login(self):
        if self.nlogin:
            self.OnLogin(True)
        if not self.webclient.connect():
            self.OnLogin(False)
            return
        strService = "SRVM"
        strLogin = 'login:user="' + MMLOperation.user_name + '",pswd="' + MMLOperation.password + '"'
        self.nRadiusMsg.set_value(strLogin, strService, 8, 0, 0, 1)
        send_buf, send_len = self.encode_msg(self.nRadiusMsg, 0)
        print 'login, send_buf=', send_buf
        if send_buf == '':
            self.OnLogin(False)
        sent = self.webclient.send_msg(send_buf, send_len)
        if sent > 0:
            recv_buffer = self.webclient.recv_msg()
            print 'recv login msg:', recv_buffer
            if recv_buffer.find('RETN=0') > 0:
                self.OnLogin(True)
            else:
                self.OnLogin(False)
        else:
            self.OnLogin(False)

    def OnLogin(self, result=True):
        if result:
            self.nlogin = result
            self.send_mml_cmd()
        else:
            print 'login failed!'

    def send_mml_cmd(self):
        strService = "C280"
        self.nRadiusMsg.set_value(MMLOperation.mml_cmd, strService, 8, 2, 0, 2)
        send_buf, send_len = self.encode_msg(self.nRadiusMsg, 0)
        print 'mml send_buf:', send_buf
        if send_len > 0:
            sent = self.webclient.send_msg(send_buf, send_len)
            if sent > 0:
                recv_buffer = self.webclient.recv_msg()
                print 'receive mml msg:', recv_buffer

    def encode_msg(self, send_msg, send_type):
        send_len = 0
        if send_type == 1:
            send_buffer = MMLContants.HW_MSG_STARTTAG
            send_buffer += self.int2hex(MMLContants.HW_HB_MSG_LEN)
            send_buffer += MMLContants.HW_HB_CONTENT
            temp_len = MMLContants.HW_MSG_STARTTAG_LEN + MMLContants.HW_MAX_HB_MSG_LEN
            send_buffer += ''.join(self.get_checksum(send_buffer[temp_len:],MMLContants.HW_MAX_HB_MSG_LEN))
        else:
            pTx = ("TXBEG","TXCON","TXCAN","TXEND")
            pDlg = ("DLGLGN","DLGBEG" ,"DLGCON","DLGEND")
            cmdLen = len(send_msg.cmd)
            msgLen = MMLContants.HW_MAX_HEAD_LEN + cmdLen
            _len = 4 - msgLen % 4
            msgLen += _len
            send_len = msgLen + MMLContants.HW_MSG_COMM_LEN

            send_buffer = MMLContants.HW_MSG_STARTTAG
            send_buffer += self.int2hex(msgLen)
            assert len(send_buffer) == 8

            send_buffer += MMLContants.HW_MSG_VERSION
            send_buffer += MMLContants.HW_MSG_TERMINAL
            send_buffer += send_msg.service
            assert len(send_buffer) == 28

            send_buffer += self.long2hex(send_msg.snLogin)
            send_buffer += pDlg[send_msg.dlgCtrl]
            send_buffer += MMLContants.HW_MSG_DLGRSVD
            assert len(send_buffer) == 46

            send_buffer += self.long2hex(send_msg.sequence)
            send_buffer += pTx[send_msg.txCtrl]
            send_buffer += MMLContants.HW_MSG_TXRSVD
            assert len(send_buffer) == 64

            send_buffer += send_msg.cmd + _len * ' '
            _len = MMLContants.HW_MSG_STARTTAG_LEN + MMLContants.HW_MSG_INFOLEN_LEN
            send_buffer += ''.join(self.get_checksum(send_buffer[_len:], msgLen))

        return send_buffer, send_len

    def decode_msg(self, recv_msg):
        pass

    def int2hex(self, _number):
        strTable = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'A', 'B', 'C', 'D', 'E', 'F']
        strTemp = ['0'] * 4
        nMid = _number % 16
        _number /= 16
        strCovert = ''
        while _number:
            strCovert += str(strTable[nMid])
            nMid = _number % 16
            _number /= 16
        strCovert += str(strTable[nMid])
        nIndex = len(strCovert) - 1
        strHex = ''
        while nIndex >= 0:
            strHex += strCovert[nIndex]
            nIndex -= 1
        nPos = 4 - len(strHex)
        if nPos < 0 or nPos > 3:
            return ''
        strTemp[nPos:] = strHex
        strHex = ''
        nCnt = 0
        while nCnt < 4:
            _value = self._get_hex(strTemp[nCnt])
            if _value:
                strHex += _value
            else:
                pass
            nCnt += 1
        return strHex

    def long2hex(self, _number):
        strTable = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'A', 'B', 'C', 'D', 'E', 'F']
        strTemp = ['0'] * 8
        nMid = _number % 16
        _number /= 16
        strCovert = ''
        while _number:
            strCovert += str(strTable[nMid])
            nMid = _number % 16
            _number /= 16
        strCovert += str(strTable[nMid])
        nIndex = len(strCovert) - 1
        strHex = ''
        while nIndex >= 0:
            strHex += strCovert[nIndex]
            nIndex -= 1
        nPos = 8 - len(strHex)
        if nPos < 0 or nPos > 7:
            return ''
        strTemp[nPos:] = strHex
        strHex = ''
        nCnt = 0
        while nCnt < 8:
            _value = self._get_hex(strTemp[nCnt])
            if _value:
                strHex += _value
            else:
                pass
            nCnt += 1
        return strHex

    def _get_hex(self, _ch):
        strTable = ['\x30', '\x31', '\x32', '\x33', '\x34', '\x35', '\x36', '\x37', '\x38', '\x39', '\x40',
                    '\x41', '\x42', '\x43', '\x44', '\x45', '\x46']
        if '\x30' <= _ch <= '\x39':
            code = ord(_ch) - 0x30
        else:
            code = ord(_ch) - 0x41 + 11
        if 0 <= code < 17 and code != 10:
            return strTable[code]
        else:
            return ''

    def get_checksum(self, buf, _len):
        res = [0, 0, 0, 0, 0, 0, 0, 0]
        i = 0
        while i < _len:
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


class WebClient(object):
    server_addr = '10.110.211.6'
    server_port = 19999

    def __init__(self):
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._con = False

    def connect(self):
        try:
            self._s.connect((WebClient.server_addr, WebClient.server_port))
            self._con = True
            print 'connect OK'
        except Exception as ex:
            print 'connect failed, ', Exception, ":", ex
            return False
        return True

    def send_msg(self, send_buf, send_len):
        if not self._con:
            return -1
        total_send = 0
        while total_send < send_len:
            sent = self._s.send(send_buf[total_send:])
            if sent == 0:
                break
            elif sent < 0:
                raise RuntimeError("socket connection broken")
            total_send += sent
        return total_send

    def recv_msg(self):
        if not self._con:
            return ''
        recv_buf = self._s.recv(10240)
        if recv_buf == '':
            raise RuntimeError("socket connection broken")
        return recv_buf

if __name__ == '__main__':
    mml_op = MMLOperation()
    mml_op.login()

