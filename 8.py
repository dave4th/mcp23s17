#!/usr/bin/python

# Questo script nasce con l'intento di comandare un display grafico 128x64
# tramite "spi"

# Carico le librerie da utilizzare
import spidev
import time

# Collegamento alla 'porta' SPI "0"
# Integrato MCP23S17, lo chiamo col suo nome 
mcp23s17=spidev.SpiDev(0,0)

# Indirizzo di default dell'integrato SPI 0x40
# E` possibile cambiarlo modificando i ponticelli "A0, A1, A2"
# e settando una variabile nel REGISTER ADDRESS "IOCON"
# al momento non sara` utilizzato.
Indirizzo = 0x40 # Indirizzo default dell'integrato

# Indirizzi REGISTER ADDRESS che controllano la configurazione
# Input / Output
IODIRA = 0x00
IODIRB = 0x01

# REGISTER ADDRESS che controllano i GPIO
GPIOA = 0x12
GPIOB = 0x13

# Serviranno riferimenti ?
#GPIOA_EN = 0x80 # Enable
#GPIOA_RW = 0x40 # Read/Write
#GPIOA_DI = 0x20 # Data/Instruction
#GPIOA_RST = 0x10    # ~Reset
#GPIOA_CS2 = 0x08    # Riquadro destro
#GPIOA_CS1 = 0x04    # Riquadro sinistro
# Forse queste ultime e` meglio specificarle diversamente ?
#       E R/W D/I RST CS2 CS1 x x
# bit   |  |   |   |   |   |  | |
#       7  6   5   4   3   2  1 0
# int('________',2)
#
# Provo ad utilizzare i decimali anche per i bit di comando, sembra piu` comodo per le operazioni.
GPIOA_EN = 128 # Enable
GPIOA_RW = 64 # Read/Write
GPIOA_DI = 32 # Data/Instruction
GPIOA_RST = 16    # ~Reset
GPIOA_CS2 = 8    # Riquadro destro
GPIOA_CS1 = 4    # Riquadro sinistro
# Per l'istruzione: EN+RST+CS1[+CS2]
#   poi si toglie l'enable: RST+CS1[+CS2] e i dati vengono trasferiti
# Per il dato: EN+DI+RST+CS1[+CS2]
#   poi si toglie l'enable: DI+RST+CS1[+CS2] e i dati vengono trasferiti
# Per la lettura: EN+RW+RST+CS1[+CS2]
#   quando si toglie l'enable: RW+RST+CS1[+CS2] non e` piu` possibile leggere
# Per la lettura: EN+RW+DI+RST+CS1[+CS2]
#   quando si toglie l'enable: RW+DI+RST+CS1[+CS2] non e` piu` possibile leggere
# LA LETTURA E` DA PROVARE !!!

# Posizione
# I valori inseriti sono relativi al set dei bit nel byte dato da trasferire
# sono il riferimento per riconoscere il tipo di dato trasferito, sono da sommare
# al valore della posizione richiesta, sto` usando i decimali per comodita` di calcolo.
AddressY = 64 # Colonna 0-63, es. per colonna 15: AddressY+15 (attenzione allo 0)
PageX = 184 # Pagina 0-7, es. per pagina 2: PageX+2 (attenzione allo 0)
LineZ = 192 # Linea di start, probabilmente utile per lo scroll verticale ? DA PROVARE

# Configuro GPIOA/B tutti i bit come uscite (0=uscita 1=ingresso)
# IODIRA
mcp23s17.writebytes([Indirizzo,IODIRA,0x00])
# IODIRB
mcp23s17.writebytes([Indirizzo,IODIRB,0x00])

# Reset display
# abbasso e rialzo il bit di reset (5)
mcp23s17.writebytes([Indirizzo,GPIOA,0x00])
time.sleep(1)
mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_RST])
# Che poi, non ho capito cosa resetta, visto che devo "sbiancarlo".

# Funzione generica per inviare un comando al display
# Settore puo`/deve essere:
# 4 per sinsitra
# 8 per destra
# 12 per entrambi
def DisplayComando(Valore,Settore):
  mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_EN+GPIOA_RST+Settore])
  mcp23s17.writebytes([Indirizzo,GPIOB,Valore])
  mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_RST+Settore])

# Funzione generica per inviare un dato al display
# Settore puo`/deve essere:
# 4 per sinsitra
# 8 per destra
# 12 per entrambi
def DisplayDato(Valore,Settore):
  mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_EN+GPIOA_DI+GPIOA_RST+Settore])
  mcp23s17.writebytes([Indirizzo,GPIOB,Valore])
  mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_DI+GPIOA_RST+Settore])


# Mi sa che sia da accendere il display
# provo! non sono sicuro pero` che siano questi i comandi
def DisplayOff():
  # E R/W D/I RST CS2 CS1 x x
  mcp23s17.writebytes([Indirizzo,GPIOA,int('10011100',2)])
  mcp23s17.writebytes([Indirizzo,GPIOB,int('00111110',2)])
  mcp23s17.writebytes([Indirizzo,GPIOA,int('00011100',2)])

def DisplayOn():
  mcp23s17.writebytes([Indirizzo,GPIOA,int('10011100',2)])
  mcp23s17.writebytes([Indirizzo,GPIOB,int('00111111',2)])
  mcp23s17.writebytes([Indirizzo,GPIOA,int('00011100',2)])

# Funzione display, sbianca o scurisce
def DisplayReset(BlackOrWhite):
  # Mentre la colonna viene incrementata automaticamente,
  # la pagina no (?)
  for i in range(0,8):
    mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_EN+GPIOA_RST+GPIOA_CS2+GPIOA_CS1])
    # X 0 (Pagina 0-7)
    mcp23s17.writebytes([Indirizzo,GPIOB,PageX+i])
    mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_RST+GPIOA_CS2+GPIOA_CS1])
    
    mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_EN+GPIOA_RST+GPIOA_CS2+GPIOA_CS1])
    # Y 0 (Colonna 0-63)
    mcp23s17.writebytes([Indirizzo,GPIOB,AddressY+0])
    mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_RST+GPIOA_CS2+GPIOA_CS1])
    for i in range(0,64):
      mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_EN+GPIOA_DI+GPIOA_RST+GPIOA_CS2+GPIOA_CS1])
      mcp23s17.writebytes([Indirizzo,GPIOB,BlackOrWhite])
      mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_DI+GPIOA_RST+GPIOA_CS2+GPIOA_CS1])

#### NON VA BENE, E` DA CORREGGERE
# Goto Position #
# Le ccordinate sono:
# per X, 0 .. 7 (pagina)
# per Y, 0 .. 63 (colonna)
# per Settore, 4/8 (sinistra/destra) ?
def DisplayGotoPosition(PageX,ColumnY,Sector):
  mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_EN+GPIOA_RST+Sector])
  mcp23s17.writebytes([Indirizzo,GPIOB,PageX])
  mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_RST+Sector])
  
  mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_EN+GPIOA_RST+Sector])
  mcp23s17.writebytes([Indirizzo,GPIOB,ColumnY])
  mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_RST+Sector])


DisplayOff()
DisplayReset(0x00)  # 0 o 255, oppure 0x00 o 0xFF
#DisplayResetBlack()
DisplayOn()

#time.sleep(100)

DisplayGotoPosition(1,40,4)

mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_EN+GPIOA_DI+GPIOA_RST+GPIOA_CS2+GPIOA_CS1])
mcp23s17.writebytes([Indirizzo,GPIOB,BlackOrWhite])
mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_DI+GPIOA_RST+GPIOA_CS2+GPIOA_CS1])

################## Prove
# E 8o bit
# RST 5o bit
# CS1 3o bit
print hex(int('10010100',2))
mcp23s17.writebytes([Indirizzo,GPIOA,0x94])
time.sleep(1)

# Y, Colonna 0
print hex(int('01000000',2))
mcp23s17.writebytes([Indirizzo,GPIOB,0x40])
time.sleep(1)
# Tolgo E
print hex(int('00010100',2))
mcp23s17.writebytes([Indirizzo,GPIOA,0x14])
time.sleep(1)

print hex(int('10010100',2))
mcp23s17.writebytes([Indirizzo,GPIOA,0x94])

# X, Pagina 0
print hex(int('10111000',2))
mcp23s17.writebytes([Indirizzo,GPIOB,0xB8])
time.sleep(1)
# Tolgo E
print hex(int('00010100',2))
mcp23s17.writebytes([Indirizzo,GPIOA,0x14])
time.sleep(1)

print 'start'
for i in range(1,9):
# E 8o bit
# D/I 6o pixel
# RST 5o bit
# CS1 3o bit
  print hex(int('10110100',2))
  mcp23s17.writebytes([Indirizzo,GPIOA,0xB4])
  #mcp23s17.writebytes([Indirizzo,GPIOA,int('10110100',2)])

  # Setto il dato 
  print hex(int('00000001',2))
  mcp23s17.writebytes([Indirizzo,GPIOB,0xFF])
  time.sleep(1)
# Tolgo E
  print hex(int('00110100',2))
  mcp23s17.writebytes([Indirizzo,GPIOA,0x34])
