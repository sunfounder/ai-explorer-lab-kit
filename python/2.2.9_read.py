# SDA - CS
# SCK - SCK
# MOSI - MOSI
# MISO - MISO
# IRQ - /
# RST - BSY

from fusion_hat import RC522
import time
rc = RC522()
rc.Pcd_start()
print("Reading...Please place the card...")


try:
    uid,message = rc.read(2)
    print("UID:", uid)    
    print("Successfully retrieved data block:", message)
    input("Press enter to exit...")
except KeyboardInterrupt:
    print("Exiting...")
