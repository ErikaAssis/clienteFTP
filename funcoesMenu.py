# coding: utf-8

import socket
import glob
from servicosFTP import Servicos

TEMPO = 0.8
TAM_BUFFER = 1024


'''
Cria uma conexão para ser usada como conexão de dados.
Recebe como parâmetros o host, ao qual será conectado,
e a porta que será usada.
Retorna, caso sucesso, a conexão criada, senão é retornado None.
'''


def criarConexaoDados(host, porta):

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        cliente.connect((host, porta))
        conteudoMensagem(cliente)
    except Exception, e:
        cliente = None
    finally:
        return cliente


'''
Realiza o login utilizando o objeto da classe Servicos().
Retorna True se operação foi realizada com sucesso, caso contrário,
retorna False.
'''


def login(ftp):

    ftp.leitura.limparTela()

    tempoConexao(ftp.conexao)

    ftp.leitura.enviarMensagem('\nEntre com usuário e senha' +
                               ' para acessar o servidor\n')
    try:
        conteudoMensagem(ftp.conexao)
        verificarResposta(ftp.user(ftp.conexao,
                          ftp.leitura.lerString('USUÁRIO')), '331')
        validacao = verificarResposta(ftp.password(ftp.conexao,
                                      ftp.leitura.lerSenha()), '230')
        conteudoMensagem(ftp.conexao)
        return validacao
    except Exception:
        return False


'''
Lista os arquivos e pastas do diretório corrente.
Recebe como paramêtro um objeto da classe Servicos(), o tipo indicando a
função cliente e a versaoMlsd que indica o que será listado.
Se versaoMlsd for 1, serão listados arquivos e diretórios;
se for 2, serão listados apenas diretórios;
se 3, serão listados apenas arquivos.
Retorna True indicando sucesso da função.
'''


def listarDiretorioCorrente(ftp, tipo, versaoMlsd):

    # Se parâmetro tipo for falso, então a funcao limpaTela é chamada.
    if tipo is False:
        ftp.leitura.limparTela()

    tempoConexao(ftp.conexao)

    # Limpa as mensagens do servidor, caso exista alguma que não foi lida.
    conteudoMensagem(ftp.conexao)

    # Recebe o diretório corrente do servidor.
    respostaServ = ftp.pwd(ftp.conexao)
    resposta = verificaMensagemSocket(respostaServ, ftp.conexao)

    if resposta is None:
        resposta = respostaServ

    if verificarResposta(resposta, '257') is False:
        ftp.leitura.enviarMensagem('\nNão foi possível realizar a operação.')
        return False

    ftp.leitura.enviarMensagem('\nDiretório corrente: ' +
                               resposta.split(' ')[1] + '\n')

    # Chama a função de PASV e cria uma conexão de dados.
    conexaoDados = criarConexaoDados(ftp.host, ftp.pasv(ftp.conexao))

    if conexaoDados is None:
        ftp.leitura.enviarMensagem('\nFalha ao criar conexão de dados.')
        return False

    # Imprime os dados para o usuário.
    if tipo is False:
        # Lista arquivos e diretórios.
        objetos = formatarMLSD(ftp.mlsd(ftp.conexao, conexaoDados), versaoMlsd)

        if len(objetos) is 0:
            ftp.leitura.enviarMensagem('\nDiretório vazio.\n')
        else:
            print objetos
    else:
        if tipo is True:

            '''
            Lista apenas um tipo de informação. Será usada nas funções:
            acessarDiretorio(),apagarDiretorio(),
            baixarArquivo() e removerArquivoServidor().
            '''

            arquivos = formatarMLSD(ftp.mlsd(ftp.conexao, conexaoDados),
                                    versaoMlsd)
            if len(arquivos) is 0:
                ftp.leitura.enviarMensagem('\nDiretório vazio.\n')
            else:
                print arquivos

    # Fecha a conexão de dados.
    fecharConexao(conexaoDados)

    return True


'''
Acessa os diretórios contidos no servidor.
Recebe como paramêtro um objeto da classe Servicos().
'''


def acessarDiretorio(ftp):

    ftp.leitura.limparTela()

    opcao = 'S'

    # Leitura de dados fica em loop até usuário optar por sua finalização.
    while opcao is 'S' or opcao is 's':  # Listar só diretorios
        tempoConexao(ftp.conexao)
        '''
        Lista apenas os diretórios presentes do diretório
        corrente do servidor.
        '''

        if listarDiretorioCorrente(ftp, False, 2) is False:
            ftp.leitura.enviarMensagem('\nFalha ao listar o diretório' +
                                       ' corrente.')
            return

        # Recebe o diretório corrente do servidor.
        respostaServ = ftp.pwd(ftp.conexao)
        resposta = verificaMensagemSocket(respostaServ, ftp.conexao)

        if resposta is None:
            resposta = respostaServ

        if pegarDiretorio(resposta) == '/':
            novoDiretorio = ftp.leitura.lerString('Informe o diretório que ' +
                                                  'deseja acessar.\t')
        else:
            novoDiretorio = ftp.leitura.lerString('Informe o diretório que ' +
                                                  'deseja acessar' +
                                                  '\nPara voltar ao' +
                                                  ' diretório' +
                                                  ' pai digite ..\t')

        # Altera o diretório corrente do servidor.
        ftp.cwd(ftp.conexao, novoDiretorio)



        # Limpa as mensagens do servidor, caso exista alguma que não foi lida.
        conteudo = conteudoMensagem(ftp.conexao)

        print conteudo

        if verificarResposta(conteudo, '250') is True:
            '''
            Lista apenas os diretórios e arquivos presentes
            no diretório corrente do servidor.
            '''

            listarDiretorioCorrente(ftp, False, 1)
            opcao = ftp.leitura.lerString('Deseja continuar a operação? S/N')

            verificacao1 = opcao != 'N' and opcao != 'n'
            verificacao2 = opcao != 'S' and opcao != 's'

            while verificacao1 and verificacao2:
                opcao = ftp.leitura.lerString('\nInforme uma opção válida.' +
                                              '\tDeseja continuar a ' +
                                              'operação? S/N')
        else:
            if verificarResposta(conteudo, '550') is True:
                ftp.leitura.enviarMensagem('\nDiretório %s não existe.'
                                           % novoDiretorio)
                opcao = 'N'


'''
Apaga um diretório contido no servidor,
caso não seja aplicada restrições ao usuário logado.
Recebe como paramêtro um objeto da classe Servicos().
'''


def apagarDiretorio(ftp):

    ftp.leitura.limparTela()

    if ftp.usuario == 'anonymous':
        ftp.leitura.enviarMensagem('\nFalha na operação de ' +
                                   'exclusão de diretório.' +
                                   'Usuário possui restrições de uso.')
        return

    tempoConexao(ftp.conexao)

    # Lista apenas os diretórios presentes do diretório corrente do servidor.
    if listarDiretorioCorrente(ftp, True, 2) is False:
        ftp.leitura.enviarMensagem('\nFalha ao listar o diretório corrente.')
        return

    nomeDiretorio = ftp.leitura.lerString('Informe o diretório a ser removido')

    # Limpa as mensagens do servidor, caso exista alguma que não foi lida.
    conteudoMensagem(ftp.conexao)

    if verificarResposta(ftp.rmd(ftp.conexao, nomeDiretorio), '250') is True:
        
        ftp.leitura.enviarMensagem('\nDiretório %s foi excluído.'
                                       % nomeDiretorio)
        '''
        Lista apenas os diretórios presentes do diretório
        corrente do servidor.
        '''
        listarDiretorioCorrente(ftp, True, 2)
        return
    else:
        if remover(ftp, nomeDiretorio) is False:        
            ftp.leitura.enviarMensagem('\nFalha na operação de exclusão.')
        else:
            ftp.leitura.enviarMensagem('\nDiretório %s foi excluído.'
                                       % nomeDiretorio)


'''
Cria um diretório no servidor, caso não seja aplicada
restrições ao usuário logado.
Recebe como paramêtro um objeto da classe Servicos().
'''


def criarDiretorioRemoto(ftp):

    ftp.leitura.limparTela()

    if ftp.usuario == 'anonymous':
        ftp.leitura.enviarMensagem('\nFalha na operação de ' +
                                   'criação de diretório.' +
                                   ' Usuário possui restrições de uso.')
        return

    ftp.leitura.enviarMensagem('\nO diretório definido a seguir ' +
                               'será criado no diretório corrente.')

    tempoConexao(ftp.conexao)

    '''
    Limpa as mensagens do servidor,
    caso exista alguma que não foi lida.
    '''
    conteudoMensagem(ftp.conexao)

    # Recebe a resposta da função de criação do diretório.
    respostaServ = ftp.mkd(ftp.conexao,
                           ftp.leitura.lerString('\nNome do diretório' +
                                                 ' a ser criado'))
    resposta = verificaMensagemSocket(respostaServ, ftp.conexao)

    if resposta is None:
        resposta = respostaServ

    if verificarResposta(resposta, '257') is True:
        ftp.leitura.enviarMensagem('\nDiretório criado com sucesso: ' +
                                   resposta.split(' ')[1])
        '''
        Lista diretórios e arquivos presentes do diretório
        corrente do servidor.
        '''
        if listarDiretorioCorrente(ftp, False, 1) is False:
            ftp.leitura.enviarMensagem('\nFalha ao listar o diretório.')
    else:
        if(verificarResposta(resposta, '550') is True):
            ftp.leitura.enviarMensagem('\nPermissão negada.')
        else:
            ftp.leitura.enviarMensagem('\nDiretório já existe e não ' +
                                       'pode ser sobreposto.')


'''
Faz o download de um arquivo contido no diretório corrente do servidor.
Recebe como paramêtro um objeto da classe Servicos().
'''


def baixarArquivo(ftp):

    ftp.leitura.limparTela()

    tempoConexao(ftp.conexao)

    # Lista apenas os arquivos presentes do diretório corrente do servidor.
    if listarDiretorioCorrente(ftp, False, 3) is False:
        ftp.leitura.enviarMensagem('\nFalha ao listar os arquivos ' +
                                   'do diretório corrente.')
        return

    # Limpa as mensagens do servidor, caso exista alguma que não foi lida.
    conteudoMensagem(ftp.conexao)

    respostaServ = ftp.type(ftp.conexao, 'I')  # Dados em binário.
    resposta = verificaMensagemSocket(respostaServ, ftp.conexao)

    if resposta is None:
        resposta = respostaServ

    if verificarResposta(resposta, '200') is True:

        # Chama a função de PASV e cria uma conexão de dados.
        conexaoDados = criarConexaoDados(ftp.host, ftp.pasv(ftp.conexao))

        if conexaoDados is None:
            ftp.leitura.enviarMensagem('\nErro na operação.')
            return

        nomeArquivo = ftp.leitura.lerString('Informe o nome do arquivo' +
                                            ' que deseja copiar' +
                                            '\nO arquivo será salvo no ' +
                                            'diretório corrente' +
                                            ' da aplicação')

        # Limpa as mensagens do servidor, caso exista alguma que não foi lida.
        conteudoMensagem(ftp.conexao)

        '''
        Caso servidor aceite a solicitação enviada por retr(),
        é criado uma cópia do arquivo solicitado.
        '''

        if verificarResposta(ftp.retr(ftp.conexao, nomeArquivo), '150') is True:

            arquivo = open(nomeArquivo, 'wb')

            while True:
                try:
                    dados = conexaoDados.recv(TAM_BUFFER)
                    if len(dados) is 0:
                        break
                    arquivo.write(dados)
                except socket.error:
                    break

            arquivo.close()
            fecharConexao(conexaoDados)

            ftp.leitura.enviarMensagem('\nOperação realizada com sucesso.')
        else:
            ftp.leitura.enviarMensagem('\nFalha ao copiar o arquivo.')
    else:
        ftp.leitura.enviarMensagem('\nFalha ao copiar o arquivo.')


'''
Envia um arquivo ao diretório corrente do servidor,
caso não seja aplicada restrições ao usuário logado.
Recebe como paramêtro um objeto da classe Servicos().
'''


def enviarArquivo(ftp):

    ftp.leitura.limparTela()

    if ftp.usuario == 'anonymous':
        ftp.leitura.enviarMensagem('\nFalha na operação de enviar arquivo.' +
                                   ' Usuário possui restrições de uso.')
        return

    ftp.leitura.enviarMensagem('\nDiretório corrente da aplicação\n')
    listarConteudo()
    nomeArquivo = ftp.leitura.lerString('\nEscolha o arquivo a ser enviado')

    tempoConexao(ftp.conexao)

    # Limpa as mensagens do servidor, caso exista alguma que não foi lida.
    conteudoMensagem(ftp.conexao)

    # Altera o tipo de transmissão de dados.
    respostaServ = ftp.type(ftp.conexao, 'A')
    resposta = verificaMensagemSocket(respostaServ, ftp.conexao)

    if resposta is None:
        resposta = respostaServ

    if verificarResposta(resposta, '200') is True:
        # Chama a função de PASV e cria uma conexão de dados.
        conexaoDados = criarConexaoDados(ftp.host, ftp.pasv(ftp.conexao))

        if conexaoDados is not None:
            tempoConexao(conexaoDados)

            # Limpa as mensagens do servidor, caso exista alguma que não foi lida.
            conteudoMensagem(ftp.conexao)

            '''
            Caso servidor aceite a solicitação enviada por stor(),
            é enviado ao mesmo uma cópia do arquivo especificado.
            '''
            if verificarResposta(ftp.stor(ftp.conexao, nomeArquivo), '150') is True:

                try:
                    conexaoDados.sendall(open(nomeArquivo, 'rb').read())
                    ftp.leitura.enviarMensagem('\nO arquivo %s foi enviado' 
                                                % nomeArquivo +
                                               ' para o diretório' +
                                               ' corrente do servidor.\n')

                    # Fecha a conexão de dados criada.
                    fecharConexao(conexaoDados)

                    '''
                    Lista diretórios e arquivos presentes do diretório
                    corrente do servidor.
                    '''
                    if listarDiretorioCorrente(ftp, True, 1) is False:
                        ftp.leitura.enviarMensagem('\nFalha ao listar o' +
                                                   ' diretório corrente.')

                except IOError, e:
                    ftp.leitura.enviarMensagem('\nArquivo %s não existe' 
                                                % nomeArquivo +
                                               ' no diretório.')
        else:
            ftp.leitura.enviarMensagem('\nOcorreu uma falha na operação\n')
    else:
        ftp.leitura.enviarMensagem('\nOcorreu uma falha na operação\n')


'''
Remove um arquivo do diretório corrente do servidor,
caso não seja aplicada restrições ao usuário logado.
Recebe como paramêtro um objeto da classe Servicos().
'''


def removerArquivoServidor(ftp):

    ftp.leitura.limparTela()

    if ftp.usuario == 'anonymous':
        ftp.leitura.enviarMensagem('\nFalha na operação de exclusão arquivo.' +
                                   ' Usuário possui restrições de uso.')
        return

    ftp.leitura.enviarMensagem('\nO arquivo será excluido' +
                               ' do diretório corrente')

    tempoConexao(ftp.conexao)

    # Lista apenas os arquivos presentes do diretório corrente do servidor.
    if listarDiretorioCorrente(ftp, True, 3) is False:
        ftp.leitura.enviarMensagem('\nFalha ao listar o diretório corrente.')
        return

    # Limpa as mensagens do servidor, caso exista alguma que não foi lida.
    conteudoMensagem(ftp.conexao)

    respostaServ = ftp.dele(ftp.conexao,
                            ftp.leitura.lerString('Informe o nome do arquivo' +
                                                  ' que deseja apagar'))
    resposta = verificaMensagemSocket(respostaServ, ftp.conexao)

    if resposta is None:
        resposta = respostaServ

    '''
    É enviado ao usuário mensagens de conclusão da operação,
    de acordo com a resposta da
    solicitação feita ao servidor por dele().
    '''
    if verificarResposta(resposta, '250') is True:

        ftp.leitura.enviarMensagem('\nArquivo deletado com sucesso')
        # Lista apenas os arquivos presentes do diretório corrente do servidor.
        listarDiretorioCorrente(ftp, False, 3)
    else:
        if verificarResposta(resposta, '550') is True:
            ftp.leitura.enviarMensagem('\nFalha ao excluir arquivo')


# Quebra a string recebida e retorna o que seria o diretório.
def pegarDiretorio(diretorio):
    try:
        diretorio.split(' ')[1]
        diretorio = diretorio.split("\"")[1]
        return diretorio.split("\"")[0]
    except IndexError:
        pass

# Lista o contéudo do diretório corrente da aplicação.
def listarConteudo():
    for file in glob.glob('*.*'):
        print '\t' + file

'''
Verifica se o início da mensagem recebida por parâmetro
é igual ao código recebido por parâmetro.
'''


def verificarResposta(mensagem, codigo):
    print mensagem
    return mensagem.startswith(codigo)


# Verifica a mensagem recebida pelo servidor.
def verificaMensagemSocket(mensagem, conexao):
    conexao.settimeout(TEMPO)

    try:
        if mensagem.startswith('226'):
            return conexao.recv(TAM_BUFFER)
        return None
    except socket.timeout, e:
        pass


# Fecha a conexão recebida por parâmetro.
def fecharConexao(conexao):
    conexao.close()


# Define o tempo da conexão
def tempoConexao(conexao):
    conexao.settimeout(TEMPO)


# Lê a mensagem completa recebida pelo servidor.
def conteudoMensagem(conexao):
    dados = ''
    tempoConexao(conexao)

    while True:
        try:
            dados += conexao.recv(TAM_BUFFER)
            if dados == '':
                break
        except socket.timeout, e:
            err = e.args[0]
            if err == 'timed out':
                break
        except Exception, e:
            break
    print dados
    return dados

'''
Formata o dado recebido por paramêtro de acordo com o tipo:
tipo 1 = diretórios e arquivos
tipo 2 = diretórios
tipo 3 = arquivos
'''


def formatarMLSD(dados, tipo):
    dados = dados.split('\n')

    msgFormatada = list()

    # Armazena nomes de diretorios e arquivos.
    if tipo is 1:

        for indice in range(len(dados)-1):
            a = list(dados[indice].split(';'))
            msgFormatada.append(a[-1].split('\r')[0])

    else:  # Armazena apenas nomes de diretórios.
        if tipo is 2:

            for indice in range(len(dados)-1):
                a = list(dados[indice].split(';'))
                if(a[2].split('=')[0] == 'type'):
                    msgFormatada.append(a[-1].split('\r')[0])

        else:  # Armazena apenas nomes de arquivos.

            for indice in range(len(dados)-1):
                a = list(dados[indice].split(';'))
                if(a[2].split('=')[0] == 'size'):
                    msgFormatada.append(a[-1].split('\r')[0])

    msgFormatada.sort(reverse=True)

    saidaFormatada = ''

    for indice in range(len(msgFormatada)):
        saidaFormatada += '\t' + msgFormatada[indice] + '\n'

    return saidaFormatada

def remover(ftp, diretorio):
    tempoConexao(ftp.conexao)

    # Limpa as mensagens do servidor, caso exista alguma que não foi lida.
    conteudoMensagem(ftp.conexao)
    #timed out
    diretorio1 = pegarDiretorio(ftp.pwd(ftp.conexao))
    diretorio = '/' + diretorio
    diretorio1 += diretorio

    ftp.cwd(ftp.conexao, diretorio1)

    if verificarResposta(ftp.conexao.recv(1024),
                         '250') is True:
      conexaoDados = criarConexaoDados(ftp.host,
                                       ftp.pasv(ftp.conexao))
      if conexaoDados is not None: 
        ftp.conexao.sendall('LIST\n\r')
        retorno = conexaoDados.recv(1024)

        if len(retorno) is 0:
            return True

        conteudo = retorno.split('\r')
 
        for i in range(len(conteudo)-1):
            a = list(conteudo[i].split(' '))
            if a[0].startswith('-') or a[0].startswith('\n-'):
              ftp.dele(ftp.conexao, a[-1])
              conteudoMensagem(ftp.conexao)
            else:
                print a[-1]
                remover(ftp, a[-1])
