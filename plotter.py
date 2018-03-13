"""Class abstracts the pen plotter.  Handles startup and shutdown boilerplate,
and takes care of sending to the serial port."""
import logging
import time
import serial

class Plotter():

    def __init__(self, verbose=False, baudrate=9600, addr=5, gpib=True,
                 paper_size="US-A", mock=False,
                 device="/dev/tty.usbserial-PX1ULOFL"):

        self.verbose = verbose
        self.mock = mock

        if mock is False:
            self.serial = serial.Serial(device)
            logging.info("Opened serial port {}".format(self.serial.name))
        else:
            self.serial = {}
            logging.info("Not sending commands to serial port")

        # This command is for the Prologix GPIB controller.
        # addr should be set equal to the GPIB number of the device
        if gpib is True:
            self._send_raw("++addr {}".format(addr))

        # Paper size can be "A" (8.5x11 in) or "B" (11x17 in). Depending on
        # the paper size the plotter has different coordinate
        #
        # For A/A4 paper:  Origin is bottom left, and the paper is landscape
        # For B/A3 paper:  Origin is top left, and the paper is portrait
        self.xmin = self.ymin = 0
        self.paper_size = paper_size
        if paper_size == "US-A":
            self.xmax = 10365
            self.ymax = 7962
        elif paper_size == "US-B":
            self.xmax = 16640
            self.ymax = 10365
        elif paper_size == "MET-A4":
            self.xmax = 11040
            self.ymax = 7721
        elif paper_size == "MET-A3":
            self.xmax = 16158
            self.ymax = 11040
        else:
            raise ValueError("Invalid paper size selected")

        logging.info("[{}] Set xmin and xmax to [{}, {}]".format(
            paper_size, self.xmin, self.xmax))
        logging.info("[{}] Set ymin and ymax to [{}, {}]".format(
            paper_size, self.ymin, self.ymax))

    def __enter__(self):
        """When you enter the context manager, send the commands that start the
        datastream and select pen 1
        """
        self._send_raw("IN;")
        self._send_raw("SP1;")
        return self

    def __exit__(self, *args):
        """When you exit the context manager, send a command to put the pen away
        because neatness is important
        """
        self._send_raw("SP0;")

    def _send_raw(self, string):
        """Convert whatever is in string to bytes and send it to the serial port
        """
        logging.debug("[SEND-TO-PORT]: {}".format(string))

        if self.mock is False:
            time.sleep(0.3)
            self.serial.write(string+"\r")

    def write_segment(self, segment):
        point_from = segment[0]
        point_to = segment[1]
        self._send_raw("PU{},{};".format(int(point_from[0]), int(point_from[1])))
        self._send_raw("PD{},{};".format(int(point_to[0]), int(point_to[1])))
