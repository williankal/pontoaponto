from re import X
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

def byte_int(data):
    int_val = int.from_bytes(data, "little")
    return int_val


def makeHead(arquivo, tipoMensagem):
    """Se tipo = 0 é handshake se tipo != 0 é parte do arquivo"""
    tamanhoArquivo = len(arquivo)
    print(f"O arquivo tem {tamanhoArquivo} bytes" )
    qtdPacotes = math.ceil(tamanhoArquivo/114)
    print(f"Quantidade de Pacotes: {qtdPacotes}")
    tamUltimoPacote = tamanhoArquivo - 114 * (qtdPacotes-1)
    pacoteAtual = 1
    tamanhoPacoteAtual = 0
    numeroErrro = 0
    ultimoSucesso = 0
    idServidor = 11
    confirma4 = 0
    if tipoMensagem == 1:
        #Handshake
        heads = [tipoMensagem, 0, idServidor, qtdPacotes ,pacoteAtual,tamanhoPacoteAtual, numeroErrro, ultimoSucesso, 0, 0]
    elif tipoMensagem == 2:
        #Confirmação Handshake
        heads = [tipoMensagem, 0, tamUltimoPacote, qtdPacotes ,pacoteAtual,tamanhoPacoteAtual, numeroErrro, ultimoSucesso, 0, 0]
    elif tipoMensagem == 3:
        #Dados
        heads = [tipoMensagem, 0, tamUltimoPacote, qtdPacotes ,pacoteAtual,tamanhoPacoteAtual, numeroErrro, ultimoSucesso, 0, 0]
    elif tipoMensagem == 4:
        #Confirmação de dados
        heads = [tipoMensagem, 0, confirma4, qtdPacotes ,pacoteAtual,tamanhoPacoteAtual, numeroErrro, ultimoSucesso, 0, 0]
    elif tipoMensagem == 5:
        #TimeOut
        heads = [tipoMensagem, 0, tamUltimoPacote, qtdPacotes ,pacoteAtual,tamanhoPacoteAtual, numeroErrro, ultimoSucesso, 0, 0]
    elif tipoMensagem == 6:
        #Erro
        heads = [tipoMensagem, 0, tamUltimoPacote, qtdPacotes ,pacoteAtual,tamanhoPacoteAtual, numeroErrro, ultimoSucesso, 0, 0]

    
    return heads
    


def makePacoteServer(arquivo, com1, tipo):
    headInt = makeHead(arquivo, tipo)
    eopInt = [170,187,204,221]
    eopByte = int_1_byte(eopInt)
    time.sleep(2)
    for i in range(0, headInt[3]):
        print("Payload feito")
        headInt[1] = 0

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
        pacote = headByte + eopByte
        print("-----------------")
        print(pacote)
        print("|||||||||")
        com1.sendData(pacote)
        
        print("-----------------")
        print("Pacote enviado: ", len(pacote))
        print("-----------------")

def makePacoteHead(arquivo, com1, tipo):
    headInt = makeHead(arquivo, tipo)
    headInt[5] = 4
    eopInt = [170,187,204,221]
    eopByte = int_1_byte(eopInt)
    time.sleep(2)
    headByte = int_1_byte(headInt)
    print(headInt)
    payload = arquivo[:114]
    print(headByte)
    pacote = headByte + payload + eopByte
    com1.sendData(pacote)

def recebePacotesHandshake(arquivo, com1):
    i = 0
    while True:
        head, lenHead = com1.getData(10)
        print("......")
        print("tipo mensagem: ", head[0])
        if head[0] == 1:
            payload, lenPayload = com1.getData(head[5])
            print("Tamanho pacote: ", head[5])
            arquivo += payload
            print("ARQUIVO: ", arquivo)
            eop, lenEOP = com1.getData(4)
            print("EOP: ", eop)

            return arquivo, head[2]

        else: 
            break

def recebePacotes(com1, ocioso):
    contador = 1
    x = [170,187,204,221]
    byte1 = int_1_byte(x)
    imagemRece = bytearray()
    envio = True
    while envio == True:
        head, lenHead = com1.getData(10)
        print("......")
        print("tipo mensagem: ", head[0])
        print(head[5])
        time1 = time.time()
        time2 = time.time()
        if head[0] == 3:
            payload, lenPayload = com1.getData(head[5])
            print("Ultimo pacote: ",head[2])
            print("Tamanho pacote: ", head[5])
            print("Numero do pacote: ", head[4])
            print("Quantidades de pacotes: ", head[3])
            print("Contador:", contador)
            print("-------------------------------------")
            eop, lenEOP = com1.getData(4)
            if len(payload) == head[5] and contador <= head[3]:
                print("Contador:", contador)
                makePacoteServer(byte1, com1, 4)
                imagemRece += payload
                print(payload)
                if contador == head[3]:
                    ocioso = False
                    print(imagemRece)
                    return imagemRece, ocioso
                    break
                contador += 1


            else:
                makePacoteServer(byte1, com1, 6)
        else: 
            time.sleep(1)
            if time.time() - time2 > 20:
                ocioso = True
                makePacoteServer(byte1, com1, 5)
                return imagemRece, ocioso

            else:
                if time.time() - time1 > 2:
                    makePacoteServer(byte1, com1, 4)  
                    time1 = time.time() 

    return imagemRece

def write_log(envioRecebido, package, tipo_log, ServerClient):
    tipo_log_string = str(tipo_log)
    arquivo = "a"
    arquivo = ServerClient + tipo_log_string + ".txt"
    with open(arquivo, "a+") as file:
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