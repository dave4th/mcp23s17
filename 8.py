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
# Il display e` diviso in due aree di 64x64
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
# Memorie di posizione (predispongo 0)
MemoriaPaginaX = 0
MemoriaColonnaY = 0
MemoriaLineaZ = 0
MemoriaSettore = 4  # 4 sinistra, 8 destra, 12 entrambe (ma questa variabile non sara` mai 'entrambe')

# Configuro GPIOA/B tutti i bit come uscite (0=uscita 1=ingresso)
# IODIRA
mcp23s17.writebytes([Indirizzo,IODIRA,0x00])
# IODIRB
mcp23s17.writebytes([Indirizzo,IODIRB,0x00])


# Reset display ???
# Teoricamente questa funzione dovrebbe resettare i registri e
# riportare il display alla posizione 0,0
# I registri non mi e` sembrato vengano azzerati, e nenche la
# posizione e` resettata.
def DisplayReset():
  # abbasso e rialzo il bit di reset (5)
  mcp23s17.writebytes([Indirizzo,GPIOA,0x00])
  time.sleep(0.05)
  mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_RST])


# Funzione generica per inviare un comando al display
# Settore puo`/deve essere:
# 4 per sinsitra
# 8 per destra
# 12 per entrambi
def DisplayInvioComando(Valore,Settore):
  mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_EN+GPIOA_RST+Settore])
  mcp23s17.writebytes([Indirizzo,GPIOB,Valore])
  mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_RST+Settore])

# Funzione generica per inviare un dato al display
# Settore puo`/deve essere:
# 4 per sinsitra
# 8 per destra
# 12 per entrambi
def DisplayInvioDato(Valore,Settore):
  mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_EN+GPIOA_DI+GPIOA_RST+Settore])
  mcp23s17.writebytes([Indirizzo,GPIOB,Valore])
  mcp23s17.writebytes([Indirizzo,GPIOA,GPIOA_DI+GPIOA_RST+Settore])
  if Settore != 12:
    DisplayMemoriaDiPosizione() # Ogni volta che invio un dato la colonna si incrementa,
                                # quindi devo andare a ricalcolare la posizione.



# Mi sa che sia da accendere il display
def DisplayOff():
  # 00111110
  DisplayInvioComando(62,12)

def DisplayOn():
  # 00111111
  DisplayInvioComando(63,12)


# Funzione riempimento display con pattern con azzeramento della posizione.
# La colonna (Y) viene incrementata automaticamente, la pagina (X) no!
def DisplayOnePattern(Valore):
  for i in range(0,8):
    DisplayInvioComando(PageX+i,12)
    DisplayInvioComando(AddressY+0,12)
    for i in range(0,64):
      DisplayInvioDato(Valore,12)

# Goto Position #
# Le coordinate sono:
# per X, 0 .. 7 (pagina)
# per Y, 0 .. 63 (colonna)
# per Settore, 4/8 (sinistra/destra) ?
# forse meglio aggiungere il calcolo "automatico" del settore ?
def DisplayVaiAPosizione(PaginaX,ColonnaY,Settore):
  #global MemoriaPaginaX, MemoriaColonnaY, MemoriaLineaZ, MemoriaSettore # Uso le variabili globali
  DisplayInvioComando(PageX+PaginaX,Settore)
  DisplayInvioComando(AddressY+ColonnaY,Settore)
  MemoriaPaginaX = PaginaX
  MemoriaColonnaY = ColonnaY
  MemoriaLineaZ = 0
  MemoriaSettore = Settore

# Ancora non so
# Tendenzialmente incrementa sempre la colonna di 1 e gli altri no, vengono calcolati
#def DisplayMemoriaDiPosizione(IncrementaPaginaX,IncrementaPaginaY,IncrementaLineaZ)
def DisplayMemoriaDiPosizione():
  global MemoriaPaginaX, MemoriaColonnaY, MemoriaLineaZ, MemoriaSettore # Uso le variabili globali
  # Incremento ogni volta ?
  MemoriaColonnaY = MemoriaColonnaY + 1
  # Se ho scritto colonna 63, la devo azzerare e spostare il riquadro
  if MemoriaColonnaY == 63:
    # Se mi trovavo a destra, devo incrementare la pagina e tornare a sinistra
    if MemoriaSettore == 8:
      MemoriaPaginaX = MemoriaPaginaX + 1
        # Se sono andato oltre le pagine, devo ricominciare dall'alto, azzerando la pagina
      if MemoriaPaginaX == 8:
        MemoriaPaginaX = 0
      MemoriaSettore = 4
    else:
      MemoriaSettore = 8
    MemoriaColonnaY = 0
    DisplayVaiAPosizione(MemoriaPaginaX,MemoriaColonnaY,MemoriaSettore)
    #print (MemoriaPaginaX,MemoriaColonnaY,MemoriaSettore)


# Spengo
DisplayOff()
time.sleep(1)
# Sbianco
DisplayOnePattern(0x00)  # 0 o 255, oppure 0x00 o 0xFF
# Riaccendo
DisplayOn()

## Prova dizionario (non l'ho mai usato)
# Non sono neanche sicuro che ...
DizionarioCaratteri = {}
DizionarioCaratteri[' '] = ['0x00', '0x00', '0x00', '0x00', '0x00']
DizionarioCaratteri['space'] = ['0x00', '0x00', '0x00', '0x00', '0x00']
DizionarioCaratteri['!'] = ['0x00', '0x00', '0x2F', '0x00', '0x00']
DizionarioCaratteri['"'] = ['0x00', '0x07', '0x00', '0x07', '0x00']
DizionarioCaratteri['#'] = ['0x14', '0x7F', '0x14', '0x7F', '0x14']
DizionarioCaratteri['$'] = ['0x24', '0x2A', '0x7F', '0x2A', '0x12']
DizionarioCaratteri['%'] = ['0x23', '0x13', '0x08', '0x64', '0x62']
DizionarioCaratteri['&'] = ['0x36', '0x49', '0x55', '0x22', '0x50']
DizionarioCaratteri['\''] = ['0x00', '0x05', '0x03', '0x00', '0x00']
DizionarioCaratteri['('] = ['0x00', '0x1C', '0x22', '0x41', '0x00']
DizionarioCaratteri[')'] = ['0x00', '0x41', '0x22', '0x1C', '0x00']
DizionarioCaratteri['*'] = ['0x14', '0x08', '0x3E', '0x08', '0x14']
DizionarioCaratteri['+'] = ['0x08', '0x08', '0x3E', '0x08', '0x08']
DizionarioCaratteri[','] = ['0x00', '0x50', '0x30', '0x00', '0x00']
DizionarioCaratteri['-'] = ['0x08', '0x08', '0x08', '0x08', '0x08']
DizionarioCaratteri['.'] = ['0x00', '0x30', '0x30', '0x00', '0x00']
DizionarioCaratteri['/'] = ['0x20', '0x10', '0x08', '0x04', '0x02']

DizionarioCaratteri['0'] = ['0x3E', '0x51', '0x49', '0x45', '0x3E']
DizionarioCaratteri['1'] = ['0x00', '0x42', '0x7F', '0x40', '0x00']
DizionarioCaratteri['2'] = ['0x42', '0x61', '0x51', '0x49', '0x46']
DizionarioCaratteri['3'] = ['0x21', '0x41', '0x45', '0x4B', '0x31']
DizionarioCaratteri['4'] = ['0x18', '0x14', '0x12', '0x7F', '0x10']
DizionarioCaratteri['5'] = ['0x27', '0x45', '0x45', '0x45', '0x39']
DizionarioCaratteri['6'] = ['0x3C', '0x4A', '0x49', '0x49', '0x30']
DizionarioCaratteri['7'] = ['0x01', '0x71', '0x09', '0x05', '0x03']
DizionarioCaratteri['8'] = ['0x36', '0x49', '0x49', '0x49', '0x36']
DizionarioCaratteri['9'] = ['0x06', '0x49', '0x49', '0x29', '0x1E']

DizionarioCaratteri[':'] = ['0x00', '0x36', '0x36', '0x00', '0x00']
DizionarioCaratteri[';'] = ['0x00', '0x56', '0x36', '0x00', '0x00']
DizionarioCaratteri['<'] = ['0x08', '0x14', '0x22', '0x41', '0x00']
DizionarioCaratteri['='] = ['0x14', '0x14', '0x14', '0x14', '0x14']
DizionarioCaratteri['>'] = ['0x00', '0x41', '0x22', '0x14', '0x08']
DizionarioCaratteri['?'] = ['0x02', '0x01', '0x51', '0x09', '0x06']
DizionarioCaratteri['@'] = ['0x32', '0x49', '0x79', '0x41', '0x3E']

DizionarioCaratteri['A'] = ['0x7E', '0x11', '0x11', '0x11', '0x7E']
DizionarioCaratteri['B'] = ['0x7F', '0x49', '0x49', '0x49', '0x36']
DizionarioCaratteri['C'] = ['0x3E', '0x41', '0x41', '0x41', '0x22']
DizionarioCaratteri['D'] = ['0x7F', '0x41', '0x41', '0x22', '0x1C']
DizionarioCaratteri['E'] = ['0x7F', '0x49', '0x49', '0x49', '0x41']
DizionarioCaratteri['F'] = ['0x7F', '0x09', '0x09', '0x09', '0x01']
DizionarioCaratteri['G'] = ['0x3E', '0x41', '0x49', '0x49', '0x7A']
DizionarioCaratteri['H'] = ['0x7F', '0x08', '0x08', '0x08', '0x7F']
DizionarioCaratteri['I'] = ['0x00', '0x41', '0x7F', '0x41', '0x00']
DizionarioCaratteri['J'] = ['0x20', '0x40', '0x41', '0x3F', '0x01']
DizionarioCaratteri['K'] = ['0x7F', '0x08', '0x14', '0x22', '0x41']
DizionarioCaratteri['L'] = ['0x7F', '0x40', '0x40', '0x40', '0x40']
DizionarioCaratteri['M'] = ['0x7F', '0x02', '0x0C', '0x02', '0x7F']
DizionarioCaratteri['N'] = ['0x7F', '0x04', '0x08', '0x10', '0x7F']
DizionarioCaratteri['O'] = ['0x3E', '0x41', '0x41', '0x41', '0x3E']
DizionarioCaratteri['P'] = ['0x3F', '0x09', '0x09', '0x09', '0x06']
DizionarioCaratteri['Q'] = ['0x3E', '0x41', '0x51', '0x21', '0x5E']
DizionarioCaratteri['R'] = ['0x7F', '0x09', '0x19', '0x29', '0x46']
DizionarioCaratteri['S'] = ['0x46', '0x49', '0x49', '0x49', '0x31']
DizionarioCaratteri['T'] = ['0x01', '0x01', '0x7F', '0x01', '0x01']
DizionarioCaratteri['U'] = ['0x3F', '0x40', '0x40', '0x40', '0x3F']
DizionarioCaratteri['V'] = ['0x1F', '0x20', '0x40', '0x20', '0x1F']
DizionarioCaratteri['W'] = ['0x3F', '0x40', '0x30', '0x40', '0x3F']
DizionarioCaratteri['X'] = ['0x63', '0x14', '0x08', '0x14', '0x63']
DizionarioCaratteri['Y'] = ['0x07', '0x08', '0x70', '0x08', '0x07']
DizionarioCaratteri['Z'] = ['0x61', '0x51', '0x49', '0x45', '0x43']

DizionarioCaratteri['\['] = ['0x00', '0x7F', '0x41', '0x41', '0x00']
DizionarioCaratteri['\\'] = ['0x02', '0x04', '0x08', '0x10', '0x20']
DizionarioCaratteri[']'] = ['0x00', '0x41', '0x41', '0x7F', '0x00']
DizionarioCaratteri['^'] = ['0x04', '0x02', '0x01', '0x02', '0x04']
DizionarioCaratteri['_'] = ['0x40', '0x40', '0x40', '0x40', '0x40']
DizionarioCaratteri['`'] = ['0x00', '0x01', '0x02', '0x04', '0x00']

DizionarioCaratteri['a'] = ['0x20', '0x54', '0x54', '0x54', '0x78']
DizionarioCaratteri['b'] = ['0x7F', '0x50', '0x48', '0x48', '0x30']
DizionarioCaratteri['c'] = ['0x38', '0x44', '0x44', '0x44', '0x20']
DizionarioCaratteri['d'] = ['0x38', '0x44', '0x44', '0x48', '0x7F']
DizionarioCaratteri['e'] = ['0x38', '0x54', '0x54', '0x54', '0x18']
DizionarioCaratteri['f'] = ['0x08', '0x7E', '0x09', '0x01', '0x02']
DizionarioCaratteri['g'] = ['0x0C', '0x52', '0x52', '0x52', '0x3E']
DizionarioCaratteri['h'] = ['0x7F', '0x08', '0x04', '0x04', '0x78']
DizionarioCaratteri['i'] = ['0x00', '0x44', '0x7D', '0x40', '0x00']
DizionarioCaratteri['j'] = ['0x20', '0x40', '0x44', '0x3D', '0x00']
DizionarioCaratteri['k'] = ['0x7F', '0x10', '0x28', '0x44', '0x00']
DizionarioCaratteri['l'] = ['0x00', '0x41', '0x7F', '0x40', '0x00']
DizionarioCaratteri['m'] = ['0x7C', '0x04', '0x18', '0x04', '0x78']
DizionarioCaratteri['n'] = ['0x7C', '0x08', '0x04', '0x04', '0x78']
DizionarioCaratteri['o'] = ['0x38', '0x44', '0x44', '0x44', '0x38']
DizionarioCaratteri['p'] = ['0x7C', '0x14', '0x14', '0x14', '0x08']
DizionarioCaratteri['q'] = ['0x08', '0x14', '0x14', '0x08', '0x7C']
DizionarioCaratteri['r'] = ['0x7C', '0x08', '0x04', '0x04', '0x08']
DizionarioCaratteri['s'] = ['0x48', '0x54', '0x54', '0x54', '0x20']
DizionarioCaratteri['t'] = ['0x04', '0x3F', '0x44', '0x40', '0x20']
DizionarioCaratteri['u'] = ['0x3C', '0x40', '0x40', '0x20', '0x7C']
DizionarioCaratteri['v'] = ['0x1C', '0x20', '0x40', '0x20', '0x1C']
DizionarioCaratteri['w'] = ['0x3C', '0x40', '0x30', '0x40', '0x3C']
DizionarioCaratteri['x'] = ['0x44', '0x28', '0x10', '0x28', '0x44']
DizionarioCaratteri['y'] = ['0x0C', '0x50', '0x50', '0x50', '0x3C']
DizionarioCaratteri['z'] = ['0x44', '0x64', '0x54', '0x4C', '0x44']

DizionarioCaratteri['{'] = ['0x00', '0x08', '0x36', '0x41', '0x00']
DizionarioCaratteri['|'] = ['0x00', '0x00', '0x7F', '0x00', '0x00']
DizionarioCaratteri['}'] = ['0x00', '0x41', '0x36', '0x08', '0x00']
DizionarioCaratteri['~'] = ['0x30', '0x08', '0x10', '0x20', '0x18']
DizionarioCaratteri[' '] = ['0x7F', '0x55', '0x49', '0x55', '0x7F']
# ----- Fine elenco caratteri -----

time.sleep(1)
DisplayVaiAPosizione(0,0,4)
#Merda = input("Ferma il programma!!! .. CTRL+C")


# Parola da stampare
Parola="+ Prova Display 128x64 + "
# Tempo di ritardo dello "scroll"
#TimeScroll=.3

# Prova del Programma
# Per ogni lettera contenuta nella Parola (frase)
for Lettera in Parola:
  # Ho dovuto identificare lo spazio, aggiungendo una parola al dizionario
  if Lettera == ' ':
    Lettera = 'space'
  # Calcolo lunghezza lettera
  Lunghezza = len(DizionarioCaratteri[Lettera])
  # Per ogni valore, invio il dato al display
  for i in range(0,Lunghezza):
    # Ho dovuto dirgli che e` un esadecimale "int(val,16)"
    DisplayInvioDato(int(DizionarioCaratteri[Lettera][i],16),MemoriaSettore)
  DisplayInvioDato(0,MemoriaSettore) # Colonna vuota

Merda = input("Ferma il programma!!! .. CTRL+C")



# Prova/e 1

#DisplayVaiAPosizione(1,63,4)
DisplayInvioDato(0xF1,4)
DisplayReset() #Come volevasi dimostrare, non cancella i dati, forse azzera la posizione ?
DisplayInvioDato(0xF2,4) # No, non azzera niente, il dato viene scritto nella colonna successiva
DisplayOn()
Merda = input("Il dato scrive alla terza colonna seconda riga (pagina) .. CTRL+C")
# Ho messo l'input per interrompere qua il programma.

print DizionarioCaratteri['A'][1]
print DizionarioCaratteri['B']
print DizionarioCaratteri['I'][0]
print len(DizionarioCaratteri['I'])
print len(DizionarioCaratteri['B'])

Merda = input("Il dato scrive alla terza colonna seconda riga (pagina) .. CTRL+C")



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

