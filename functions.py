from enlace import *
import numpy as np
import math

def ligaCom(serialName):
    com1 = enlace(serialName)
    start_time = time.time()
    com1.enable()
    if com1.enable() == True:
        print("Comunicação Aberta")

    return com1, start_time


def desligaCom(com1, start_time):
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com1.disable()


    print("--- {:.4f} seconds ---".format(time.time() - start_time))


def int_1_byte(data):
    entireData = bytearray()
    for i in data:
        intByte = (i).to_bytes(1, byteorder ='big')
        entireData.append(intByte[0])
    return entireData


def makeHead(arquivo, tipo):
    """Se tipo = 0 é handshake se tipo != 0 é parte do arquivo"""
    tamanhoBytes = len(arquivo)
    print(f"O arquivo tem {tamanhoBytes} bytes" )
    qtdPayloads = math.ceil(tamanhoBytes/114)
    print(f"Quantidade de Pacotes: {qtdPayloads}")
    tamUltimoPacote = tamanhoBytes - 114*(qtdPayloads-1)
    print(f"Tamanho do último pacote: {tamUltimoPacote}")
    pacoteAtual = 0

    heads = [0, tamanhoBytes, qtdPayloads, tamUltimoPacote,pacoteAtual,0, 0, 255, 0, 0]

    
    return heads
    


def makePacote(arquivo,com1):
    headInt = makeHead(arquivo,1)
    eopInt = [0,255,0,0]
    eopByte = int_1_byte(eopInt)
    time.sleep(2)
    for i in range(0, headInt[2]):
        payload = arquivo[:114]
        del arquivo[:114]
        print("Payload feito")
        headInt[1] = len(payload)

        print("-------------------------")
        print("número do pacote: {}".format(headInt[4]))
        time.sleep(0.5)
        if headInt[2] == headInt[4]+1:
            headInt[5] = headInt[3]
        else:
            headInt[5] = 114
        headByte = int_1_byte(headInt)
        print(headInt)
        headInt[4] += 1
        print(headByte)
        pacote = headByte + payload + eopByte
        print(pacote)
        com1.sendData(pacote)

        print("-----------------")
        print("Pacote enviado: ", len(pacote))
        print("-----------------")


def recebePacotes(arquivo, com1):
    i = 0
    while True:
        head, lenHead = com1.getData(10)
        print("......")
        print("head recebido: ", head[4])
        print(head[5])
        if head[4] != i:
            print("Erro enviar de novo pacote: ", i)
        payload, lenPayload = com1.getData(head[5])
        print(payload)
        arquivo += payload
        eop, lenEOP = com1.getData(4)
        i += 1
        if head[2] == head[4]+1:
            break
    
    return arquivo