import time
import threading
import wx
from pymodbus.client import ModbusTcpClient

class ModbusWorker(threading.Thread):
    def __init__(self, host, port, slave_id, start_address, count, update_callback, error_callback):
        super().__init__()

        self.host = host
        self.port = port
        self.slave_id = slave_id
        self.start_address = start_address
        self.count = count

        # callback for GUI update
        self.update_callback = update_callback
        self.error_callback = error_callback

        self.client = None
        self._running = False
        self.daemon = True # Thread automatically stop when main app closed

    def run(self):
        self._running = True
        self.client = ModbusTcpClient(self.host, port=self.port)

        if not self.client.connect():
            wx.CallAfter(self.error_callback, "Failed Connect to PLC!")
            self._running = False
            return

        wx.CallAfter(self.update_callback, None, "Connected to PLC")

        while self._running:
            try:
                # Read Holding Register
                response = self.client.read_holding_registers(
                    address=self.start_address,
                    count=self.count,
                    slave=self.slave_id
                )

                if response.isError():
                    wx.CallAfter(self.error_callback, f"Modbus Error: {response}")
                else:
                    # Send data registers to GUI as thread-safe
                    wx.CallAfter(self.update_callback, response.registers, "OK")

            except Exception as e:
                wx.CallAfter(self.error_callback, f"Connection closed / Error: {str(e)}")
                break

            # Delay polling rate
            time.sleep(1.0)

            # Disconnect when loop stop
            self.client.close()
            wx.CallAfter(self.update_callback, None, "Disconnected from PLC")

    def stop(self):
        """Stop thread safe"""
        self._running = False