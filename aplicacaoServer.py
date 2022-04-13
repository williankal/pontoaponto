from enlace import *
import numpy as np
import time

from functions_client import *
from functions_server import *

#Comando para abrir port:   sudo chmod 777 /dev/ttyACM<numero da porta>
#Declarar porta utilizada aqui
serialName = "/dev/ttyACM0"   
#serialName = "ACM0"                  # Windows(variacao de)


def main():
    try:
        com1, start_time = ligaCom(serialName)
        espera(com1)
        ocioso = True
        timeout = True
        while ocioso == True:
            while com1.rx.getIsEmpty():
                print("------------")
                print("Esperando.....")
            time.sleep(0.2)
            recebeHandshake = bytearray()
            recebeHandshake, idHand = recebePacotesHandshake(recebeHandshake, com1)
            
            
            print("---------------------------------")
            print("HandShake RECEBIDO")
            print("---------------------------------")
            if idHand == 11:
                if recebeHandshake == b'\x00\x00\xff\xff':
                    print("Devolvendo Handshake")
                    handshakeInt = [0, 0, 255, 255]
                    handshakeByte = int_1_byte(handshakeInt)
                    primeiro = makePacoteHead(handshakeByte, com1, 2)
                    print("----------")
                    print("Escutando")
                    ocioso = False
                else: 
                    print("Erro no Handshake")
                    ocioso = True
                    time.sleep(1)
            else: 
                print("Erro no Handshake")
                ocioso = True
                time.sleep(1)

        
            imagemRecebida, ocioso, timeout = recebePacotes(com1, ocioso, timeout)
        
        if timeout == False:
            print("------------")
            print("Tempo de time out atingido")
            print("Finalizando coms")
            quit()
                
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