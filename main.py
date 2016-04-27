# coding: utf-8

import socket

'''
Módulo criado apenas para realizar a leitura e exibição
de informações do usuário.
'''

from leituraUsuario import IOUsuario
import funcoesMenu as func
from servicosFTP import Servicos

IMP_1 = '============================='
MSG_MENU = '\n' + IMP_1 + 'Cliente FTP' + IMP_1

IMP_2 = '++++++++++++++++++'
INF_VALIDA = '\n' + IMP_2 + '\tInforme uma opção válida\t' + IMP_2

PORTA = 21


# Função que cria conexão com o servidor ftp definido pelo usuário.
def abrirConexao(host, porta):
    leitura = IOUsuario()

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        cliente.connect((host, porta))
        func.conteudoMensagem(cliente)
        leitura.enviarMensagem('Conexao estabelecida')
    except Exception, e:
        leitura.enviarMensagem('Conexao não estabelecida')
        cliente = None
    finally:
        leitura.pausarAplicacao()
        return cliente

'''
Função responsável por imprimir as opçoes da aplicação
para o usuário e ler a opção escolhida.
'''


def menu(leitura):
    leitura.enviarMensagem(MSG_MENU)
    leitura.enviarMensagem('\n1 - Login\n2 - Listar os arquivos e' +
                           ' pastas do diretório corrente' +
                           '\n3 - Acessar diretório' +
                           '\n4 - Remover diretório\n5 - Criar diretório' +
                           '\n6 - Fazer download de arquivo' +
                           '\n7 - Fazer upload de arquivo' +
                           '\n8 - Remover arquivo' +
                           '\n9 - Finalizar aplicação')
    return leitura.lerNumeroInteiroPositivo('\nInforme a opção desejada')


'''
Faz a verificação do login.
Se validacao for 0, significa que o usuário deverá
logar no servidor antes de executar qualquer ação na aplicação.
Caso contrário, o usuário já realizou o login.
'''


def verificarLogin(validacao):
    leitura = IOUsuario()
    if validacao is 0:
        leitura.enviarMensagem('\nVocê deve entrar com login.')
        leitura.pausarAplicacao()
        return False


# Inicia a aplicação
def inicio():
    ftp = Servicos()

    '''
    Realiza 3 tentativas de conexão ao servidor ftp.
    Caso não se tenha sucesso a aplicação é encerrada.
    '''

    for tentativa in range(0, 3):
        ftp.leitura.limparTela()
        ftp.host = ftp.leitura.lerString('\nInforme o servidor')
        ftp.conexao = abrirConexao(ftp.host, PORTA)
        if ftp.conexao is not None:
            ftp.verificacaoConexao = 1
            break

    if ftp.verificacaoConexao is 0:
        ftp.leitura.limparTela()
        ftp.leitura.enviarMensagem('\nA aplicação irá ser' +
                                   ' encerrada.' +
                                   '\nNão foi possível criar ' +
                                   'conexao com o servidor: ' +
                                   host)
        ftp.leitura.pausarAplicacao()
        return

    validacao = 0
    opcao = 0

    # Aplicação fica em loop até a opção do usuário eer igual 9.
    while opcao is not 9:
        ftp.leitura.limparTela()
        opcao = menu(ftp.leitura)

        '''
        Se opção for diferente das definidas no menu,
        a função menu() será chamada novamente.
        '''

        while opcao < 1 or opcao > 9:
            ftp.leitura.limparTela()
            ftp.leitura.enviarMensagem(INF_VALIDA)
            opcao = menu(ftp.leitura)

        # 1 - Login
        if opcao is 1:
            '''
            Verifica se o usuário ja fez login no servidor,
            pois essa operação é permitida uma única vez.
            '''

            if validacao is 1:
                ftp.leitura.enviarMensagem('\nOperação já realizada.')
                ftp.leitura.pausarAplicacao()
                continue

            retorno = func.login(ftp)
            if retorno:
                validacao = 1
            else:
                '''
                Se a operação de login falhar,
                uma mensagem é enviada ao usuário.
                '''

                if retorno is not True:
                    ftp.leitura.enviarMensagem('\nFalha no login.')
                    ftp.leitura.pausarAplicacao()

        # 2 - Listar os arquivos e pastas do diretório corrente
        if opcao is 2:
            # Verifica se o usuário ja fez login no servidor.
            if verificarLogin(validacao) is False:
                continue

            func.listarDiretorioCorrente(ftp, False, 1)
            ftp.leitura.pausarAplicacao()

        # 3 - Acessar diretório
        if opcao is 3:
            # Verifica se o usuário ja fez login no servidor.
            if verificarLogin(validacao) is False:
                continue

            func.acessarDiretorio(ftp)
            ftp.leitura.pausarAplicacao()

        # 4 - Remover diretório
        if opcao is 4:
            # Verifica se o usuário ja fez login no servidor.
            if verificarLogin(validacao) is False:
                continue

            func.apagarDiretorio(ftp)
            ftp.leitura.pausarAplicacao()

        # 5 - Criar diretório
        if opcao is 5:
            # Verifica se o usuário ja fez login no servidor.
            if verificarLogin(validacao) is False:
                continue

            func.criarDiretorioRemoto(ftp)
            ftp.leitura.pausarAplicacao()

        # 6 - Fazer download de arquivo
        if opcao is 6:
            # Verifica se o usuário ja fez login no servidor.
            if verificarLogin(validacao) is False:
                continue

            func.baixarArquivo(ftp)
            ftp.leitura.pausarAplicacao()

        # 7 - Fazer upload de arquivo
        if opcao is 7:
            # Verifica se o usuário ja fez login no servidor.
            if verificarLogin(validacao) is False:
                continue

            func.enviarArquivo(ftp)
            ftp.leitura.pausarAplicacao()

        # 8 - Remover arquivo
        if opcao is 8:
            # Verifica se o usuário ja fez login no servidor.
            if verificarLogin(validacao) is False:
                continue

            func.removerArquivoServidor(ftp)
            ftp.leitura.pausarAplicacao()

        # 9 - Finalizar aplicação
        if opcao is 9:
            func.fecharConexao(ftp.conexao)


# Início da aplicação
inicio()

