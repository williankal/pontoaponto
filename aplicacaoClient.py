from enlace import *
import numpy as np
import time
from functions_client import *
from functions_server import *


#Comando para abrir port:   sudo chmod 777 /dev/ttyACM<numero da porta>
#Declarar porta utilizada aqui
serialName = "/dev/ttyACM0"          

def main():
    try:
        iniciador = input("Começa envio: S/N")
        if iniciador.upper() == "S":
            imagem = bytearray(open("./imgs/image.png", "rb").read())
            tIm = len(imagem)
            qIm = math.ceil(tIm/114)
            com1, start_time = ligaCom(serialName)
            print("Enviando Handshake")
            handshakeInt = [0, 0, 255, 255]
            handshakeByte = int_1_byte(handshakeInt)
            makePacoteHead(handshakeByte, com1, 1, qIm)
            headHandshake, lenteste = com1.getData(10)
            print(headHandshake)
            payloadHandshake, lenteste  = com1.getData(4)
            print(payloadHandshake)
            eopHandshake, lenteste = com1.getData(4)
            print(eopHandshake)
            print("Handshake recebido: ", (headHandshake+payloadHandshake+eopHandshake))

            if  payloadHandshake == b'\x00\x00\xff\xff' and headHandshake[0] == 2:
                print("----------------")
                print("Confirmado")
            else: 
                print("FALHA EM HANDSHAKE")
                quit()
            
            imageR = "./imgs/image.png"

            print("Carregando imagem para transmissão")
            print(".{}".format(imageR))
            print("---------------------------")
            print("Imagem Transformada em bytes")
            makePacoteClient(imagem, com1, 3, 0)
                
            desligaCom(com1,start_time)
        else:
            quit()
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
