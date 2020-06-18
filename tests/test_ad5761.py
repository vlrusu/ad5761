#!/usr/bin/env python

"""Tests for `ad5761` package."""


import unittest
import sys
from ad5761 import ad5761


class TestAd5761(unittest.TestCase):
    """Tests for `ad5761` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""


    def test_write(self):
        l = ad5761.ad5761(0, 0)
        l._max_speed_hz = 100000
        l.open()

        l._ad5761_read_cr()
        print '[{}]'.format(', '.join(hex(x) for x in l._rawdata))                
        l._print()

        l._ad5761_write_cr()        
        l._ad5761_write_dac(1000)
        l._ad5761_read_dac()
        
#         l._ad5761_spi_write(0xc,0)
#

#         l._ad5761_spi_write(0xc,0)
#         print '[{}]'.format(', '.join(hex(x) for x in l._rawdata))        


# #        l._ad5761_spi_write(0x4,0)
# #        print '[{}]'.format(', '.join(hex(x) for x in l._rawdata))        
        

#         l._ad5761_spi_write(0xc,0)
#         print '[{}]'.format(', '.join(hex(x) for x in l._rawdata))        

#         l._ad5761_spi_write(0xc,0)
#         print '[{}]'.format(', '.join(hex(x) for x in l._rawdata))        
        

        
        l.close()
