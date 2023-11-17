class WiFi:
    ver = "1.5.4"
    siete = None
    w = None
    bolo_pripojene = False
    hostname = None

    def __init__(self, hostname=None, zapni=True, info=True):
        from sys import platform
        import network
        from gc import collect
        import wifi_config
        self.siete = wifi_config.siete

        # deaktivuj sieťové rozhrania (na ESP8266 je default aktívne AP a zostáva aktívne STA)
        network.WLAN(network.AP_IF).active(False)

        # ak nie je definovaný hostname, použije názov platformy a ID
        # ak začína medzerou, pomlčkou alebo dvojbodkou, názov platformy dá na začiatok
        # ak končí medzerou, na koniec pridá názov platformy do zátvorky
        if not hostname:
            from binascii import hexlify
            from machine import unique_id
            ID = hexlify(unique_id()).decode()
            hostname = platform.upper() + "-" + ID
        elif hostname[0] in (" ", "-", ":"):
            hostname = platform.upper() + hostname
        elif hostname[-1] == " ":
            hostname += "(" + platform.upper() + ")"
        self.hostname = hostname

        self.w = network.WLAN(network.STA_IF)
        self.Aktivuj()            
        self.w.config(dhcp_hostname = hostname)
        if info: print("\n\x1b[97mOBSLUHA WI-FI v{}\x1b[0m".format(self.ver))
        if zapni:
            self.Zapni(info)
        else:
            self.Aktivuj(False)
        collect()
      
    def Aktivuj(self, active=True):
        from time import sleep
        self.w.active(active)
        while True:
            sleep(0.1)
            if self.w.active() == active: break
        return active

    def Pripoj(self, ssid, heslo, skryta=False, info=True):
        self.Odpoj(False)
        self.Aktivuj()
        if info:
            print("Hľadám skrytú" if skryta else "Pripájam na", end="")
            print(" Wi-Fi <\x1b[97m{}\x1b[0m>: ".format(ssid), end="")
        try:
            self.w.connect(ssid, heslo)
        except:
            if info: print("CHYBA")
            return False
        return self.CakajPripojenie(30, info)

    def Obnov(self, info=True):
        if self.w.isconnected():
            self.bolo_pripojene = True
            self.NastavCas()
            return True
        self.Vypni(False)
        if not self.bolo_pripojene: return False
        self.bolo_pripojene = False
        self.Aktivuj()            
        if info: print("Obnovujem Wi-Fi spojenie: ", end="")
        try:  # niekedy zlyhá s OSError: Wifi Internal Error
            self.w.connect()
        except:
            if info: print("CHYBA")
            return False
        if not self.CakajPripojenie(10, info):
            return False
        self.NastavCas()
        return True

    def Zapni(self, info=True):
        if self.Obnov(info): return True
        if info: print("Vyhľadávam Wi-Fi siete: ", end="")
        self.Aktivuj()            
        try:
            scan1 = self.w.scan()
            if info: print("OK ({})".format(len(scan1)))
        except:
            if info: print("nenašiel som")
            scan1 = []
            
        scan = {}
        for s in scan1:
            if s[0] not in scan:
                scan[s[0]] = 0
            scan[s[0]] |= 1 if s[4] == 0 else 2  # 1=otvorená, 2=heslo, 3=oboje
        del scan1
        for ssid, heslo in self.siete:
            skryta = (ssid[0] == "!")
            if skryta:
                ssid = ssid[1:]
            ssid_e = ssid.encode()
            if skryta or ssid_e in scan and (heslo and scan[ssid_e] & 2 or not heslo and scan[ssid_e] & 1):
                if self.Pripoj(ssid, heslo, skryta, info): break
            
        if self.w.isconnected():
            self.NastavCas()
            return True
        else:
            return self.Aktivuj(False)

    def Odpoj(self, info=True):
        if not self.w.active(): return
        from time import sleep
        if info: print("Odpájam z Wi-Fi: ..", end="")
        self.w.disconnect()
        for i in range(50):  # poistka - niekedy sa zacyklí
            if not self.w.isconnected(): break
            if info: print(".", end="")
            sleep(0.1)
        else:
            print("\n\x1b[97;41m CHYBA: Nepodarilo sa odpojiť z Wi-Fi, reštartujem... \x1b[0m")
            sleep(1)
            from machine import reset
            reset()
        if info: print(" OK")

    def Vypni(self, info=True):
        if not self.w.active(): return
        self.Odpoj(info)
        self.Aktivuj(False)

    def CakajPripojenie(self, kroky, info=True):
        from time import sleep
        for i in range(kroky):  # poistka - inak sa zacyklí
            import network
            if self.w.status() != network.STAT_CONNECTING: break  # nefunguje dobre pri neúspešnom spájaní
            if info: print(".", end="")
            sleep(0.3)
        if self.w.isconnected():
            if info:
                print(" \x1b[97;42m OK \x1b[0m")
                print("Pripojené s adresou a menom: {}, {}".format(self.w.ifconfig()[0], self.hostname))
            self.bolo_pripojene = True
            return True
        else:
            if info: print(" \x1b[97;41m nepodarilo sa \x1b[0m")
            return self.Aktivuj(False)

    def JePripojene(self):
        return self.w.isconnected()

    def NastavCas(self):
        from time import time, mktime, gmtime
        import ntptime

        try: teraz = ntptime.time()
        except: teraz = time()
        rok = gmtime(teraz)[0]
        letny = list(gmtime(mktime((rok, 3, 31, 1, 0, 0, 0, 0))))
        letny[2] -= (letny[6] + 1) % 7
        letny = mktime(letny)
        zimny = list(gmtime(mktime((rok, 10, 31, 1, 0, 0, 0, 0))))
        zimny[2] -= (zimny[6] + 1) % 7
        zimny = mktime(zimny)
        if (letny < teraz and teraz < zimny):
            ntptime.NTP_DELTA = 3155673600 - 7200
        else:
            ntptime.NTP_DELTA = 3155673600 - 3600
        
        try: ntptime.settime()
        except: return False
        return True