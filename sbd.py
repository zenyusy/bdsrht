import binascii
import calendar
import datetime
import os
import sys
import tarfile
from http.client import HTTPSConnection
from io import BytesIO
from random import shuffle
from typing import Optional, Tuple


def next_bd(m: int, d: int, now: datetime.datetime) -> Optional[datetime.datetime]:
    year = now.year
    today = datetime.datetime(year, now.month, now.day)
    for y in range(year, year + 5):
        try:
            r = datetime.datetime(y, m, d)
        except:
            continue
        else:
            if r >= today:
                return r


def gap_str(d: datetime.timedelta) -> str:
    h = round(d.seconds / 3600)
    if h == 24:
        h = 0
        dy = d.days + 1
    else:
        dy = d.days
    r = f'{dy}D' if dy else ''
    return r + (f'{h}H' if h else '')


def get_q(m: int, d: int, now: datetime.datetime) -> str:
    bd = next_bd(m, d, now)
    if bd is None:
        return '?'
    if bd.day == now.day and bd.year == now.year and bd.month == now.month:
        return 'HAPPY BIRTHDAY!'
    return f'{gap_str(bd - now)} until your birthday ({bd.strftime("%Y-%m-%d")})'


def pq(mmdd: str, now: datetime.datetime) -> Tuple[str, str, str]:
    m = int(mmdd[:2])
    d = int(mmdd[2:])
    return 'If your birthday is on', f'{calendar.month_name[m]} {d}', get_q(m, d, now)


# html
def h_line(x, y, z):
    return f"<p>{x} {h_color_size(y, 'green', '24')} : {h_q(z)}</p>"

def h_color_size(w, color, size):
    return f'<span style="color:{color};font-size:{size}px;">{w}</span>'

def h_q(w):
    if w == '?':
        return w
    if w[-1] == '!':
        return h_color_size(w, 'red', 40)
    gap_sep = w.find(' ')
    return ' '.join([h_color_size(w[:gap_sep], 'blue', 28), w[gap_sep:]])

def h_index(bd_list, now, title, h1, p):
    """
    bd_list: ['0102', '0304', ...]
    now: datetime(2050, 1, 2, 3, 4)
    title: 'web title'
    h1: 'page h1'
    p: 'prelude'
    """
    w = ''.join(h_line(*pq(bd, now)) for bd in bd_list)
    return f'<!doctype html><html lang=en><head><meta charset=utf-8><title>{title}</title><body><section class=section><div class=container><h1 class=title>{h1}</h1><p> {p} </p>{w}</div></section>'


# tgz
def get_tgz(content: str) -> bytes:
    io_ret = BytesIO()
    io_in = BytesIO(content.encode())
    tgz = tarfile.open(mode='w:gz', fileobj=io_ret)
    tari = tarfile.TarInfo('index.html')
    tari.size = len(content)
    tgz.addfile(tari, fileobj=io_in)

    tgz.close()
    io_in.close()
    r = io_ret.getvalue() # `seek(0)` before `read()`
    io_ret.close()
    return r


# curl -Fcontent=@s.tar.gz --oauth2-bearer 's' https://pages.sr.ht/publish/user.srht.site
# http
class H:
    D = b'--'
    BOD = binascii.hexlify(os.urandom(16))
    MIME = b'multipart/form-data; boundary=' + BOD

    @classmethod
    def get_body(cls, b: bytes) -> bytes:
        return b'\r\n'.join([
            b'%s%s' % (cls.D, cls.BOD),
            b'Content-Disposition: form-data; name="content"; filename="s.tar.gz"',
            b'Content-Type: application/x-tar',
            b'',
            b,
            b'%s%s%s' % (cls.D, cls.BOD, cls.D),
            b''])

    @classmethod
    def post(cls, tar: bytes, user: str, s: str):
        b = cls.get_body(tar)
        h = HTTPSConnection('pages.sr.ht')
        h.request(
            'POST',
            f'/publish/{user}.srht.site',
            b,
            {
                "Authorization": f"Bearer {s}",
                'content-type': cls.MIME.decode(),
                'content-length': str(len(b)),
            })
        h.getresponse()


def main():
    _, bd_csv, user, sec, title, t = sys.argv
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=int(t))
    h1p = list(range(0x21, 0x30))
    shuffle(h1p)
    H.post(get_tgz(
        h_index(bd_csv.split(','),
                now.replace(minute=0, second=0, microsecond=0),
                title, chr(h1p[0]), chr(h1p[1]))), user, sec)

if __name__ == '__main__':
    main()
