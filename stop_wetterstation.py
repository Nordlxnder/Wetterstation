#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

    Funktion Stop Wetterstation
        dieses Skript dient zum Beenden des laufenden Skripts für die Wetterstation.
        Hintergrund ist das wenn das Skript Wetterstation.py als Service gestartet wird,
        läuft es weiter auch wenn der Service gestoppt wurde. Damit das Skripot auch beendet wird,
        wird ein Stopptbefehl an die Netzwerkadresse gesendet.

        Dieses Script  wird dann in der Shell für den Stop des Services mit aufgerufen damit alle Prozesse
        sauber beendet werden.


'''

import socket ,subprocess, re

def stop_server():
    #HOST = '192.168.2.135'  # Zielrechner
    PORT = 55252  # Port des Servers für

    # aktuelle IP adresse ermittel
    ausgabe = subprocess.check_output("ip -f inet addr show dev wlan0| awk -F ' *|:' '/inet/'", shell=True)
    #ausgabe = subprocess.check_output("ip -f inet addr show dev enp2s0| awk -F ' *|:' '/inet/'", shell=True)
    suchfilter = r'.*?inet\ (.*?)/'
    HOST_IP = re.findall(suchfilter, ausgabe.decode())

    print(HOST_IP)

    # sendet der Befehls zum Stoppen
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as netzwerkschnittstelle:

            netzwerkschnittstelle.connect((str(HOST_IP[0]), PORT))
            # Stop
            stop_wetterstation = "Stop"
            netzwerkschnittstelle.sendall(str.encode(stop_wetterstation))
            print("Die Wetterstation wurde beendet durch das Skript stop_wetterstation.py")
    except OSError as error:
        print("Dienst Wetterstation ist schon beendet!")
        print(error)

    pass


if __name__ == "__main__":
    try:
        stop_server()
    except ConnectionRefusedError as e:
        print("Fehlermeldung",e)
