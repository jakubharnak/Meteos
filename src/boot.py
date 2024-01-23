import esp
import sys
import uos
import gc
from binascii import hexlify
from machine import freq, unique_id
from time import sleep_ms


try:
    import esp32
    teplota = (esp32.raw_temperature() - 32) / 1.8
except:
    teplota = None

esp.osdebug(None)
hardver = "{} @ {:.0f} MHz".format(sys.platform.upper(), freq() / 1_000_000)
if teplota:
    hardver += " ({:.0f} °C)".format(teplota)
print("\n\x1b[33mHARDWARE: {}, {:.0f} MiB flash, ID: \x1b[30;43m {} \x1b[0m".format(
     hardver,
     esp.flash_size() / 1048576,
     hexlify(unique_id(), "-").decode().upper(),
     ))
hardver = uos.uname().machine
if "-" in hardver or "module" not in hardver:
    print("\x1b[33m          {}\x1b[0m".format(hardver))
del teplota, hardver

dodatok = uos.uname().version
dodatok_pos = dodatok.find(" on ")
if dodatok_pos >= 0:
    dodatok = " (" + dodatok[dodatok_pos+4:] + ")"
else:
    dodatok = ""
print("\x1b[33mSOFTWARE: {} v{}{} ~ Python {}\x1b[0m".format(
     sys.implementation.name,
     ".".join(map(str, sys.implementation.version)),
     dodatok,
     sys.version,
     ), end="")
del dodatok, dodatok_pos