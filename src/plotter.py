"""Class abstracts the pen plotter.  Handles startup and shutdown boilerplate,
and takes care of sending to the serial port."""
import logging
import time
import serial

class Plotter():

    def __init__(self, verbose=False, baudrate=9600, addr=5, gpib=True,
                 paper_size="MET-A4", dryrun=False,
                 device="/dev/ttyUSB0"):

        self.verbose = verbose
        self.dryrun = dryrun

        self.current_x = None
        self.current_y = None

        if dryrun is False:
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

        self.scale_ratio = 1.0

        logging.info("[{}] Set xmin and xmax to [{}, {}]".format(
            paper_size, self.xmin, self.xmax))
        logging.info("[{}] Set ymin and ymax to [{}, {}]".format(
            paper_size, self.ymin, self.ymax))

    def __enter__(self):
        """When you enter the context manager, send the commands that start the
        datastream and select pen 1
        """
        self._send_raw("IN;")
        model = self._send_raw("OI;", read=True)
        resolution = self._send_raw("OF;", read=True)
        logging.debug("{} plotter has plotting resolution {}".format(
            model, resolution))

        self._send_raw("SP1;")
        return self

    def __exit__(self, *args):
        """When you exit the context manager, send a command to put the pen away
        because neatness is important
        """
        self._send_raw("SP0;")

    def _send_raw(self, string, read=False):
        """Convert whatever is in string to bytes and send it to the serial port
        """
        logging.debug("[SEND-TO-PORT]: {}".format(string))
        if self.dryrun is True:
            return

        # Check if the plotter is ready for input
        while True:
            self.serial.write(b"OS;"+b"\r")
            status = self.serial.readline().rstrip(b"\r\n")
            status_bin = "{0:b}".format(int(status))
            ready = status_bin[-5]
            if ready == "1":
                # We're good... a 1 in the 16 value (position 4) part of this
                # binary number means "Send me data"
                break
            logging.warning("Buffer full.  Plotter asked for more time...")
            time.sleep(0.01)

        # The actual send
        self.serial.write(bytes(string, "utf-8")+b"\r")

        if read is True:
            return self.serial.readline().rstrip(b"\r\n")

    def set_image_scale(self, img_size):

        ratio_x = float(self.xmax) / img_size[0]
        ratio_y = float(self.ymax) / img_size[1]
        self.scale_ratio = min([ratio_x, ratio_y])
        logging.debug("Image scale ratio: {}".format(self.scale_ratio))


    def write_segment(self, segment):
        point_from = segment[0]*self.scale_ratio
        point_to = segment[1]*self.scale_ratio

        if not (self.current_x == point_from[0] and
                self.current_y == point_from[1]):
            self._send_raw("PU{},{};".format(int(point_from[0]),
                                            int(point_from[1])))

        self._send_raw("PD{},{};".format(int(point_to[0]),
                                         int(point_to[1])))
        self.current_x = point_to[0]
        self.current_y = point_to[1]

    def write_circle(self, center, radius):
        self._send_raw("PA{},{};".format(int(center[0]),
                                            int(center[1])))
        self._send_raw("CI{},45;".format(radius))

    def write_square(self, center, size):
        self._send_raw("PU{},{};".format(int(center[0]-size/2.0),
                                        int(center[1]-size/2.0)))
        self._send_raw("PD{},{};".format(int(center[0]-size/2.0),
                                        int(center[1]+size/2.0)))
        self._send_raw("PD{},{};".format(int(center[0]+size/2.0),
                                        int(center[1]+size/2.0)))
        self._send_raw("PD{},{};".format(int(center[0]+size/2.0),
                                        int(center[1]-size/2.0)))
        self._send_raw("PD{},{};".format(int(center[0]-size/2.0),
                                        int(center[1]-size/2.0)))
