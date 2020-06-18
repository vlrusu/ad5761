"""Main module."""
#!/usr/bin/env python

import spidev
import RPi.GPIO as GPIO
import time


#AD5761_ADDR(addr)             =  ((addr & 0xf) << 16)
AD5761_ADDR_NOOP              =  0x0
AD5761_ADDR_DAC_WRITE         =  0x3
AD5761_ADDR_CTRL_WRITE_REG    =  0x4
AD5761_ADDR_SW_DATA_RESET     =  0x7
AD5761_ADDR_DAC_READ          =  0xb
AD5761_ADDR_CTRL_READ_REG     =  0xc
AD5761_ADDR_SW_FULL_RESET     =  0xf

AD5761_CTRL_USE_INTVREF_BIT       = 5
AD5761_CTRL_ETS_BIT               = 6

AD5761_VOLTAGE_RANGE_M10V_10V = 0
AD5761_VOLTAGE_RANGE_0V_10V = 1
AD5761_VOLTAGE_RANGE_M5V_5V = 2
AD5761_VOLTAGE_RANGE_0V_5V = 3
AD5761_VOLTAGE_RANGE_M2V5_7V5 = 4
AD5761_VOLTAGE_RANGE_M3V_3V = 5 
AD5761_VOLTAGE_RANGE_0V_16V = 6
AD5761_VOLTAGE_RANGE_0V_20V = 7

CR_CV = 9
CR_OVR = 8
CR_B2C = 7
CR_ETS = 6
CR_IRO = 5
CR_PV = 3
CR_RA = 0


DEFAULT_CV = 0
DEFAULT_OVR = 0
DEFAULT_B2C = 0
DEFAULT_ETS = 0
DEFAULT_IRO = 1
DEFAULT_PV = 0
DEFAULT_RA = 3


ad5761_voltage_range = [
        AD5761_VOLTAGE_RANGE_M10V_10V,
        AD5761_VOLTAGE_RANGE_0V_10V,
        AD5761_VOLTAGE_RANGE_M5V_5V,
        AD5761_VOLTAGE_RANGE_0V_5V,
        AD5761_VOLTAGE_RANGE_M2V5_7V5,
        AD5761_VOLTAGE_RANGE_M3V_3V,
        AD5761_VOLTAGE_RANGE_0V_16V,
        AD5761_VOLTAGE_RANGE_0V_20V,
]





class ad5761(object):
    """Documentation for ad5761

    """

    def __init__(self, bus=0, cs=1, clear = 27, reset = 17, ldac= 22,  max_speed_hz=400000):
        """Initialize an SPI device using the SPIdev interface.  Port and device
        identify the device, for example the device /dev/spidev1.0 would be port
        1 and device 0.
        """

        self._bus = bus
        self._cs = cs
        self._spimode = 0b01
        self._clear = clear
        self._reset = reset
        self._ldac = ldac
        self._max_speed_hz = max_speed_hz
        self._rawdata=[]

        self._ad5761_setdefault()
        
        self.isInitialized = False
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._clear, GPIO.OUT)
        GPIO.setup(self._ldac, GPIO.OUT)
        GPIO.setup(self._reset, GPIO.OUT)        

        
    def open(self):

        if self.isInitialized:
            return

        self._spi = spidev.SpiDev()

        self._spi.open(self._bus, self._cs)
        self._spi.mode = self._spimode
        self._spi.max_speed_hz=self._max_speed_hz
        self._print()
        GPIO.output(self._clear, GPIO.HIGH)
        GPIO.output(self._ldac, GPIO.LOW)
        GPIO.output(self._reset, GPIO.HIGH)        

        self.isInitialized = True
 

    def close(self):
        """Closes the SPI connection 
        """
        self._spi.close()
        self.isInitialized = False


    def _ad5761_setdefault(self):
        self._cv = DEFAULT_CV
        self._ovr = DEFAULT_OVR
        self._b2c = DEFAULT_B2C
        self._ets = DEFAULT_ETS
        self._iro = DEFAULT_IRO
        self._pv = DEFAULT_PV
        self._ra = DEFAULT_RA
        


        
    def _ad5761_write_cr(self):
        data = self._cv <<CR_CV | self._ovr <<CR_OVR | self._b2c<<CR_B2C | self._ets<<CR_ETS | self._iro << CR_IRO | self._pv << CR_PV | self._ra << CR_RA
        self._ad5761_spi_write(AD5761_ADDR_CTRL_WRITE_REG,data)
        return 0

    def _ad5761_read_cr(self):
        self._ad5761_spi_write(AD5761_ADDR_CTRL_READ_REG,0)
        self._ad5761_spi_write(AD5761_ADDR_NOOP,0)
        self._ad5761_parse_cr()
        return 0

    def _ad5761_set_cv(self,data):
        if data > 3:
            return 1

        self._cv = data
        self._ad5761_write_cr(cr)
        return 0


    def _print(self):
        print ("CV="+str(self._cv)+"/OVR="+str(self._ovr)+"/B2C="+str(self._b2c)+"/ETS="+str(self._ets)+"/IRO="+str(self._iro)+"/PV="+str(self._pv)+"/RA="+str(self._ra))

    def _ad5761_write_dac(self,data):
        self._ad5761_spi_write(AD5761_ADDR_DAC_WRITE,data)        

    def _ad5761_read_dac(self):
        self._ad5761_spi_write(AD5761_ADDR_DAC_READ,0)
        self._ad5761_spi_write(AD5761_ADDR_NOOP,0)
        val = self._rawdata[1] << 8 | self._rawdata[2]
        print ("DAC DATA = " + str(val))
    
    def _ad5761_parse_cr(self):
        data = self._rawdata[1]<<8 | self._rawdata[2]
#        print hex(self._rawdata[0]),hex(self._rawdata[1]),hex(data)
        self._cv = (data >> CR_CV) & 0x3
        self._ovr = (data >> CR_OVR) & 0x1 
        self._b2c = (data >> CR_B2C) & 0x1
        self._ets = (data >> CR_ETS) & 0x1
        self._iro = (data >> CR_IRO) & 0x1
        self._pv = (data >> CR_PV) & 0x3
        self._ra = (data >> CR_RA) & 0x3
        
    def _ad5761_hard_reset(self):
        GPIO.output(self._reset, GPIO.LOW)
        GPIO.output(self._reset, GPIO.HIGH)
        self._ad5761_setdefault()
        
    def  _ad5761_spi_write(self, address, val):
        command =  ((address & 0xf) << 16) | val
        commandlist = [command >> (8*i) & 0xFF for i in range(23 // 8,-1,-1)]
#        print commandlist
        reply = self._spi.xfer2(commandlist)
        self._rawdata = reply

        return 0
