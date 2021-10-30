import unittest

import datetime
from random import randint
from sbd import next_bd, gap_str

class TestBd(unittest.TestCase):
    def test_next_bd(self):
        for m, t, o in (
            ('1231', '2021-12-30', '2021-12-31'),
            ('1231', '2021-12-31', '2021-12-31'),
            ('1231', '2022-01-01', '2022-12-31'),
            ('0501', '2021-04-30', '2021-05-01'),
            ('0501', '2021-05-01', '2021-05-01'),
            ('0501', '2021-05-02', '2022-05-01'),
            ('0229', '2020-02-28', '2020-02-29'),
            ('0229', '2020-02-29', '2020-02-29'),
            ('0229', '2020-03-01', '2024-02-29'),
            ('0229', '2021-01-01', '2024-02-29'),
        ):
            now_ = datetime.datetime.fromisoformat(f'{t} {randint(0, 23):02}')
            self.assertEqual(
                next_bd(int(m[:2]), int(m[2:]), now_),
                datetime.datetime.fromisoformat(o),
                f'{m} + {t} -> {o}'
            )

    def test_gap_str(self):
        for i, o in (
            (datetime.timedelta(1,0), '1D'),
            (datetime.timedelta(0,10*3600), '10H'),
            (datetime.timedelta(1,23*3600+1900), '2D'),
            (datetime.timedelta(0,23*3600+1900), '1D'),
            (datetime.timedelta(1,23*3600+1700), '1D23H'),
            (datetime.timedelta(0,23*3600+1700), '23H'),
            (datetime.timedelta(3,22*3600), '3D22H'),
        ):
            self.assertEqual(gap_str(i), o, f'{i} -> {o}')
