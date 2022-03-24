from enlace import *
import numpy as np
import time

from functions import *

#Comando para abrir port:   sudo chmod 777 /dev/ttyACM<numero da porta>
#Declarar porta utilizada aqui
serialName = "/dev/ttyACM0"   
#serialName = "ACM0"                  # Windows(variacao de)


def main():
    try:
        com1, start_time = ligaCom(serialName)


        while com1.rx.getIsEmpty():
            print("------------")
            print("Esperando.....")
            time.sleep(0.2)


        recebeHandshake = bytearray()
        recebeHandshake = recebePacotes(recebeHandshake, com1)
            


        if recebeHandshake == b'\x00\x00\xff\xff':
            print("Devolvendo Handshake")
            handshakeInt = [0,0,255, 255]
            handshakeByte = int_1_byte(handshakeInt)
            primeiro = makePacote(handshakeByte, com1)
            com1.sendData(primeiro)

        else: 
            print("Erro no Handshake")
            handshakeInt = [255, 255, 0, 0]
            handshakeByte = int_1_byte(handshakeInt)
            primeiro = makePacote(handshakeByte, com1)
            com1.sendData(primeiro)

        #finalmente vamos transmitir os tados. Para isso usamos a funçao sendData que é um método da camada enlace.
        #faça um print para avisar que a transmissão vai começar.
        #tente entender como o método send funciona!
        #Cuidado! Apenas trasmitimos arrays de bytes! Nao listas!
        imagemRecebida = bytearray()
        imagemRecebida = recebePacotes(imagemRecebida, com1)
            
        imagemW = "./imgs/recebida.png"
        print("Salvando dados no arquivo")
        print("- {}".format(imagemW))
        f = open(imagemW, 'wb')
        f.write(imagemRecebida)
        f.close()


            


        print(imagemRecebida)
        # Encerra comunicação
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        print("--- {:.4f} seconds ---".format(time.time() - start_time))
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
