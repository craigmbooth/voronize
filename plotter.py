"""Class abstracts the pen plotter.  Handles startup and shutdown boilerplate,
and takes care of sending to the serial port."""
import serial

class Plotter():

    def __init__(self, verbose=False):
        self.verbose = verbose
        #self.serial = serial.Serial('/dev/ttyUSB0')
        if self.verbose is True:
            print "Opened serial port {}".format(self.serial.name)

    def __enter__(self):
        """When you enter the contect manager, send the commands that start the
        datastream and select pen 1"""
        self._send_raw("IN;")
        self._send_raw("SP1;")
        return self

    def __exit__(self, *args):
        """When you exit the context manager, send a command to pick up the pen
        so it doesn't sit ont he paper and leak through."""
        self._send_raw("PU;")

    def _send_raw(self, string):
        """Convert whatever is in string to bytes and send it to the serial port
        """
        if self.verbose is True:
            print "\tSENDING: {}".format(string)
        #self.serial.write(string.encode('ASCII'))

    def write_segment(self, segment):
        pass
