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


def makeHead(arquivo, tipoMensagem, qtdPacotes, original):
    """Se tipo = 0 é handshake se tipo != 0 é parte do arquivo"""
    tamanhoArquivo = original
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
    


def makePacoteHead(arquivo,com1, tipo, tIm):
    headInt = makeHead(arquivo,tipo, 0, tIm)
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
    print(pacote)    
    print("-----------------")
    print("Pacote enviado: ", len(pacote))
    print("-----------------")
    print("primeiro enviado")
    time.sleep(5)
    inicio = time.time()
    print("------------------------------")
    while com1.rx.getIsEmpty():#Comando para abrir port :sudo chmod 777 /dev/ttyACM<numero da porta>
        if time.time() - inicio >= 5:
            resposta = str(input("Servidor inativo, deseja tentar novamente? S/N : "))
            if resposta.upper() == "S":
                com1.sendData(pacote)
                print("enviado novamente")
                inicio = time.time()
                pass
            else:
                desligaCom(com1, inicio)
                exit()

def makePacoteClient(arquivo,com1, tipo, qtdPacotes):
    tIm = len(arquivo)
    print("tim: ",tIm)
    qtdPacotes = math.ceil(tIm/114)
    eopInt = [170,187,204,221]
    eopByte = int_1_byte(eopInt)
    i = 0
    while i < qtdPacotes:
        headInt = makeHead(arquivo, tipo, 0, tIm)
        payload = arquivo[:114]
        headInt[4] += i
        print("----------", headInt[3])
        print("----------", headInt[4])
        if headInt[3] == headInt[4]:
            print("--------------------entrou")
            headInt[5] = headInt[2]
        else:
            headInt[5] = 114
        print(f"Tamanho do arquivo {i+1} é {headInt[5]}")
        
        print("Head atual: ", headInt)
        headByte = int_1_byte(headInt)
        print(headByte)
        pacote = headByte + payload + eopByte
        print(pacote)
        com1.sendData(pacote)
        
        print("-----------------")
        print("Pacote enviado: ", len(pacote))
        print("-----------------")
        confirma4, tipo4 = com1.getData(14)
        print("PAYLOAD RECEBIDO: ", confirma4)
        if confirma4[0] == 4:
            print("TIPO DE MENSAGEM: ", confirma4[0]  )
            del arquivo[:114]
            headInt[1] = len(payload)
            print("-------------------------")
            i +=1
        else:
            break

            


def recebePacotes(arquivo, com1):
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
    
    return arquivo