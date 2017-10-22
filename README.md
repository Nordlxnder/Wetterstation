# Wetterstation

    |------------------------------|              |------------------------------|
    | beliebiger PC im Netzwerk    |              | Raspberry Zero mit Sensoren  |
    |  als Client                  |              |    als Wetterstation         |
    |                              |              |                              |
    |  client_wetter.py            |--------------|  wetterserver.py             |
    |                              |              |                              |
    |                              |              |  Sensoren:                   |
    |------------------------------|              |   DHT22  -> Luftfechte       |
                                                  |             Temperatur       |
                                                  |   BMP180 -> Luftdruck        |
                                                  |             Temperatur       |
                                                  |             Höhe             |
                                                  |------------------------------|


 Installation

    cd /
    sudo git clone https://github.com/Nordlxnder/Wetterstation.git
    # BenutzerXY  bitte ersetzen durch deinen Benutzer
    sudo chown --recursiv BenutzerXY:users /Wetterstation


 wetterserver.py


     Funktion Wetterstation:
        - auslesen der Temperatur und Luftfeuchte
        - Server um die Werte im Netzwerk bereit zustellen

    Hardwarevoraussetzungen:
        Raspberry zero über WLAN mit dem Netzwerk verbunden
        Sensor  DHT 22  mit Pin 4 verbunden
            Pinbelegung:
                Sensor          Raspi
            VCC    1   ----   PIN 17 3.3 V
            Data   2   ----   PIN 11 GPIO 17   (nicht verwechseln mit PIN 17;)
            NC     3
            GND    4   ----   PIN 14 

        Sensor  BMP180
            Pinbelegung
                Sensor          Raspi
            VCC        ----   PIN 1  3.3 V
            SDA        ----   PIN 3  SDA  
            SCL        ----   PIN 5  SCL                
            GND        ----   PIN 6  GND 
     

    Softwarevoraussetzungen:
        Treiber für Sensor installiert Adafruit_Python_DHT
        Python 3.6 installiert
        i2c-tools


 client_wetter.py
 
    Funktion:
        - sendet Schlüsselwörter wie DATEN um Daten anzufordern oder AB um die Verbindung zubeenden


 Einstellung für I²C in /boot/config.txt:
             
        sudo nano /boot/config.txt
                                                                                                
            initramfs initramfs-linux.img followkernel
            device_tree_param=spi=on
            # i2c für Drucksensor BMP180
            dtparam=i2c1=on
            dtparam=i2c_arm=on
        
 Anpassung unter Arch Linux für I²C:
 
        sudo nano /etc/modules-load.d/raspberrypi.conf
    
        snd-bcm2835
        i2c-bcm2708
        i2c-dev

 Schnittstellenunterstützung I²C für BMP180 imstallieren

    sudo pacman -S i2c-tools

 Treiber für DHT22 installieren

    git clone https://github.com/adafruit/Adafruit_Python_DHT.git

    cd Adafruit_Python_DHT

    sudo python setup.py install

    und wieder ins Projektverzeichnis wechseln

 Pythonskript als systemd Service starten unter Arch Linux (als root ausführen)

    cd /usr/bin

    nano wetterstationstart.sh


        #!/bin/bash
        # Pfad zum Skript angeben
        python /home/BenutzerXY/Wetterstation/wetterserver.py
        echo "Start der Wetterstation: $(date)" >> /var/log/wetterstation.log


    nano wetterstationstop.sh


        #!/bin/bash
        echo "Stopp der Wetterstation: $(date)" >> /var/log/wetterstation.log


    chmod 755 wetterstation*.sh

    cd /etc/systemd/system

    nano wetterstation.service


            #########################################################################
            #
            # wetterstation.service
            # systemd service: aktivieren der Wetterstation beim Start des PCs
            #
            #########################################################################

            [Unit]
            Description=Wetterstation
            #After=network.target
            After=netctl@Rheinblick3.service

            [Service]
            Type=simple
            User=root
            ExecStart=/usr/bin/wetterstationstart.sh &
            ExecStop=/usr/bin/wetterstationstop.sh
            Restart=on-abort

            [Install]
            WantedBy=multi-user.target

            # EOF

    chmod 644 wetterstation.service
    systemctl start wetterstation.service
    systemctl enable wetterstation.service


