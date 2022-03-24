from enlace import *
import numpy as np
import time
from functions import *


#Comando para abrir port:   sudo chmod 777 /dev/ttyACM<numero da porta>
#Declarar porta utilizada aqui
serialName = "/dev/ttyACM0"          

def main():
    try:

        com1, start_time = ligaCom(serialName)
        print("Enviando Handshake")
        handshakeInt = [0, 0, 255, 255]
        handshakeByte = int_1_byte(handshakeInt)
        primeiro = makePacote(handshakeByte, com1)
        com1.sendData(primeiro)
        inicio = time.time()

        print("------------------------------")

        while com1.rx.getIsEmpty():#Comando para abrir port :sudo chmod 777 /dev/ttyACM<numero da porta>
                if time.time() - inicio >= 5:
                    resposta = str(input("Servidor inativo, deseja tentar novamente? S/N : "))
                    if resposta.upper() == "S":
                        com1.sendData(primeiro)
                        inicio = time.time()
                        pass
                    else:
                        desligaCom(com1, start_time)
                        exit()

        print("Confirmação Recbida")
        headHandshake, lenteste = com1.getData(10)
        print(headHandshake)
        payloadHandshake, lenteste  = com1.getData(4)
        print(payloadHandshake)
        eopHandshake, lenteste = com1.getData(4)
        print(eopHandshake)
        print("Handshake recebido: ", (headHandshake+payloadHandshake+eopHandshake))

        if  payloadHandshake == b'\x00\x00\xff\xff':
            print("----------------")
            print("Confirmado")
        else: 
            print("FALHA EM HANDSHAKE")
            quit()
        
        imageR = "./imgs/image.png"

        print("Carregando imagem para transmissão")
        print(".{}".format(imageR))
        print("---------------------------")
        imagem = bytearray(open("./imgs/image.png", "rb").read())
        print("Imagem Transformada em bytes")
        makePacote(imagem, com1)
            
        desligaCom(com1,start_time)

    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
