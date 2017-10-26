#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Funktion clientprogramm
        - sendet Schlüsselwörter wie DATEN um Daten anzufordern oder AB um die Verbindung zubeenden
'''

import socket

class messdaten_abfragen():

    def __init__(self):
        HOST = '192.168.2.135'  # Zielrechner
        PORT = 55252  # Port des Servers für
        #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.netzwerkschnittstelle:
        self.netzwerkschnittstelle=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.netzwerkschnittstelle.connect((HOST, PORT))

    def messdaten(self):
        # Begrüßung empfangen
        daten_empfangen = self.netzwerkschnittstelle.recv(1024)
        print(daten_empfangen.decode('utf-8'))

        # Messdaten anfordern
        daten_anfordern="MESSDATEN"
        self.netzwerkschnittstelle.sendall(str.encode(daten_anfordern))
        daten_empfangen = self.netzwerkschnittstelle.recv(1024)
        print("Empfangene Daten:\t", daten_empfangen.decode('utf-8'))

        # Verbindung beenden bzw abbrechen
        daten_senden = "AB"
        self.netzwerkschnittstelle.sendall(str.encode(daten_senden))
        daten_empfangen = self.netzwerkschnittstelle.recv(1024)
        print("Abschlußmeldung:\t", daten_empfangen.decode('utf-8'))

if __name__ == "__main__":
    try:
        #client_starten()
        messdaten_abfragen().messdaten()
    except ConnectionRefusedError as e:
        print("Fehlermeldung",e)
pass