# Wetterstation

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
                                                                                                     
            initramfs initramfs-linux.img followkernel
                                                                                            
            device_tree_param=spi=on                                                        
                                                                                                                  
            # i2c für Drucksensor BMP180         
            dtparam=i2c1=on                                              
            dtparam=i2c_arm=on
        
 Anpassung unter Arch Linux für I²C:
 
        nano /etc/modules-load.d/raspberrypi.conf
    
        snd-bcm2835
        i2c-bcm2708
        i2c-dev

