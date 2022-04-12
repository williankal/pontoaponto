from enlace import *
import numpy as np
import math
from functions_client import *
import datetime

def espera(com1):
    while com1.rx.getIsEmpty():
        print("------------")
        print("Esperando.....")
        time.sleep(0.2)

def int_1_byte(data):
    entireData = bytearray()
    for i in data:
        intByte = (i).to_bytes(1, byteorder ='big')
        entireData.append(intByte[0])
    return entireData

def makeHead(arquivo, tipoMensagem):
    """Se tipo = 0 é handshake se tipo != 0 é parte do arquivo"""
    tamanhoArquivo = len(arquivo)
    print(f"O arquivo tem {tamanhoArquivo} bytes" )
    qtdPacotes = math.ceil(tamanhoArquivo/114)
    print(f"Quantidade de Pacotes: {qtdPacotes}")
    tamUltimoPacote = tamanhoArquivo - 114*(qtdPacotes-1)
    print(f"Tamanho do último pacote: {tamUltimoPacote}")
    pacoteAtual = 1
    tamanhoPacoteAtual = 0
    numeroErrro = 0
    ultimoSucesso = 0
    idServidor = 11
    confirma4 = 0
    if tipoMensagem == 1:
        #Handshake
        heads = [tipoMensagem, tamanhoArquivo, idServidor, qtdPacotes ,pacoteAtual,tamanhoPacoteAtual, numeroErrro, ultimoSucesso, 0, 0]
    elif tipoMensagem == 2:
        #Confirmação Handshake
        heads = [tipoMensagem, tamanhoArquivo, tamUltimoPacote, qtdPacotes ,pacoteAtual,tamanhoPacoteAtual, numeroErrro, ultimoSucesso, 0, 0]
    elif tipoMensagem == 3:
        #Dados
        heads = [tipoMensagem, tamanhoArquivo, tamUltimoPacote, qtdPacotes ,pacoteAtual,tamanhoPacoteAtual, numeroErrro, ultimoSucesso, 0, 0]
    elif tipoMensagem == 4:
        #Confirmação de dados
        heads = [tipoMensagem, tamanhoArquivo, confirma4, qtdPacotes ,pacoteAtual,tamanhoPacoteAtual, numeroErrro, ultimoSucesso, 0, 0]
    elif tipoMensagem == 5:
        #TimeOut
        heads = [tipoMensagem, tamanhoArquivo, tamUltimoPacote, qtdPacotes ,pacoteAtual,tamanhoPacoteAtual, numeroErrro, ultimoSucesso, 0, 0]
    elif tipoMensagem == 6:
        #Erro
        heads = [tipoMensagem, tamanhoArquivo, tamUltimoPacote, qtdPacotes ,pacoteAtual,tamanhoPacoteAtual, numeroErrro, ultimoSucesso, 0, 0]

    
    return heads
    


def makePacoteServer(arquivo,com1, tipo):
    headInt = makeHead(arquivo,tipo)
    eopInt = [170,187,204,221]
    eopByte = int_1_byte(eopInt)
    time.sleep(2)
    for i in range(0, headInt[3]):
        payload = arquivo[:114]
        del arquivo[:114]
        print("Payload feito")
        headInt[1] = len(payload)

        print("-------------------------")
        print("número do pacote: {}".format(headInt[4]))
        time.sleep(0.5)
        if headInt[3] == headInt[4]:
            headInt[5] = headInt[2]
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
    i = 1
    while True:
        head, lenHead = com1.getData(10)
        print("......")
        print("head recebido: ", head[4])
        print(head[5])
        payload, lenPayload = com1.getData(head[5])
        print(payload)
        arquivo += payload
        eop, lenEOP = com1.getData(4)
        confirmaInt = [0, 0, 255, 255]
        confirmaByte = int_1_byte(confirmaInt)
        primeiro = makePacoteClient(confirmaByte, com1, 4, 0)
        com1.sendData()
        i += 1
        if head[3] == head[4]:
            break
            return arquivo
def recebePacotesHandshake(arquivo, com1):
    i = 0
    while True:
        head, lenHead = com1.getData(10)
        print("......")
        print("head recebido: ", head[4])
        print(head[5])
        payload, lenPayload = com1.getData(head[5])
        print(payload)
        arquivo += payload
        eop, lenEOP = com1.getData(4)
        i += 1
        if head[3] == head[4]:
            break
    
    return arquivo, head[2]

def write_log(envioRecebido, package):
    with open("Server3.txt", "a+") as file:
        file.write("\n")
        file.write("{}".format(datetime.datetime.now()))
        file.write("\n")
        file.write(" /")
        file.write(envioRecebido)
        file.write(" /")
        file.write(package[0])
        file.write(" /")
        file.write("{}".format(len(package)))
        if package[0] == 3:
            file.write(" /")
            file.write(package[4])
            file.write(" /")
            file.write(package[3])

