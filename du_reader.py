import serial
import time
import threading

from du_utils import (
    calculate_crc16,
    calculate_little_endian,
)
from decrypt_utils import decrypt_hex_block   # <-- your Decrypt(receivedData)
from gpio_control import turn_BL_Detect_Low, turn_BL_Detect_High

# Set this from the UI / main app
isEncryptionEnable = False
encryptedKeyIndex = (85, 117)   # SAME as JS
KEY_FOR_ENCRYPTION = None


class DUReader:
    def __init__(self, serial_port, baud, callback_status, callback_error, callback_success):
        self.serial_port = serial_port
        self.baud = baud

        self.received_hex = ""              # EXACTLY like JS receivedData
        self.buffer = b""                   # bytes from hex
        self.callback_status = callback_status
        self.callback_error = callback_error
        self.callback_success = callback_success

    def start(self):
        threading.Thread(target=self.read_loop, daemon=True).start()

    def read_loop(self):

        turn_BL_Detect_High()
        self.callback_status("Waiting for DU...")

        try:
            ser = serial.Serial(self.serial_port, self.baud, timeout=0.5)
        except Exception as e:
            self.callback_error(f"Serial open error: {e}")
            turn_BL_Detect_Low()
            return

        start_time = time.time()

        while True:

            # Timeout like JS: 10 seconds without data
            if time.time() - start_time > 10:
                turn_BL_Detect_Low()
                self.callback_error("E31 - No Data Received during Handshake")
                ser.close()
                return

            try:
                data = ser.read(256)  # read chunk
            except Exception as e:
                turn_BL_Detect_Low()
                self.callback_error(f"E14 - Serial Port Error: {e}")
                ser.close()
                return

            if not data:
                continue

            # Convert to hex string EXACTLY LIKE JS
            chunk_hex = data.hex()
            self.received_hex += chunk_hex

            # Debug
            print("HEX += ", chunk_hex)
            print("LEN:", len(self.received_hex))

            # JS waits until >= 1024 hex chars (512 bytes)
            if len(self.received_hex) < 1024:
                continue

            # Now convert full hex string to bytes (same as Buffer.from(hex,'hex'))
            try:
                self.buffer = bytes.fromhex(self.received_hex[:1024])
            except Exception as e:
                self.callback_error("Invalid HEX stream")
                ser.close()
                return

            sop = f"{self.buffer[0]:02x}"
            eop = f"{self.buffer[509]:02x}"

            firmware1 = self.buffer[393]
            firmware2 = self.buffer[394]

            # -----------------------------
            # STEP 1 — UNENCRYPTED DATA?
            # -----------------------------
            if sop == "2a" and eop == "3c":
                print("UNENCRYPTED DATA detected")

                # CRC CHECK
                crc_calc = calculate_crc16(self.buffer[:510])
                little_end = calculate_little_endian(crc_calc)
                crc_recv = self.buffer[510:512].hex()

                if little_end != crc_recv:
                    self.callback_error("E52-Invalid Data Received")
                    ser.close()
                    return

                global isEncryptionEnable
                isEncryptionEnable = self.get_encryption_flag(firmware1, firmware2)

            else:
                # -----------------------------
                # STEP 2 — ENCRYPTED DATA
                # -----------------------------
                print("ENCRYPTED DATA detected, decrypting...")

                decrypted_hex = decrypt_hex_block(self.received_hex[:1024])
                self.buffer = bytes.fromhex(decrypted_hex)

                sop = f"{self.buffer[0]:02x}"
                eop = f"{self.buffer[509]:02x}"

                if sop != "2a" or eop != "3c":
                    self.callback_error("E52-Invalid Data Received")
                    ser.close()
                    return

                crc_calc = calculate_crc16(self.buffer[:510])
                little_end = calculate_little_endian(crc_calc)
                crc_recv = self.buffer[510:512].hex()

                if little_end != crc_recv:
                    self.callback_error("E52-Invalid Data Received")
                    ser.close()
                    return

                isEncryptionEnable = self.get_encryption_flag(firmware1, firmware2)

            # ----------------------------------------
            # At this point, data is validated
            # ----------------------------------------

            # Extract DU and Display Numbers
            duNumber = int(self.received_hex[4:20], 16)
            displayNumber = int(self.received_hex[20:36], 16)

            print("DU:", duNumber, "Display:", displayNumber)

            ser.close()
            turn_BL_Detect_Low()

            # SUCCESS callback with DU + Display
            self.callback_success({
                "duNumber": duNumber,
                "displayNumber": displayNumber,
                "isEncryptionEnable": isEncryptionEnable
            })
            return

    # Same logic as JS
    def get_encryption_flag(self, fw1, fw2):
        if fw1 >= 11 and fw2 >= 8:
            return True
        return False
