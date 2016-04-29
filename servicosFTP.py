# coding: utf-8

from leituraUsuario import IOUsuario
TAM_BUFFER = 1024

'''
Classe que possui alguns métodos típicos de um serviço FTP,
implementados utilizando sockets.
'''


class Servicos():

    # Construtor
    def __init__(self):
        self.usuario = None
        self.conexao = None
        self.servidor = None
        self.verificacaoConexao = 0
        self.leitura = IOUsuario()

    '''
    Permite alterar o diretório corrente,
    voltando sempre para o diretório pai.
    '''

    def cdup(self, conexao):
        conexao.sendall('CDUP\r\n')

    '''
    Permite alterar o diretório corrente.
    Recebe como parâmetro a conexão já criada e o nome do diretório
    para o qual será alterado.
    '''

    def cwd(self, conexao, nomeDiretorio):
        conexao.sendall('CWD %s\r\n' % nomeDiretorio)

    '''
    Permite apagar o arquivo cujo nome é recebido por parâmetro.
    Recebe como parâmetro a conexão já criada e o nome do arquivo que será
    excluído.
    Retorna a resposta do servidor à ação.
    '''

    def dele(self, conexao, nomeArquivo):
        conexao.sendall('DELE %s\r\n' % nomeArquivo)
        return conexao.recv(TAM_BUFFER)

    '''
    Utilizado quando é preciso fazer uso da conexão de dados.
    Recebe como parâmetro a conexão já criada.
    Retorna a porta que será usada para se criar a conexao de dados.
    '''

    def pasv(self, conexao):
        conexao.sendall('PASV\r\n')
        # Faz chamada ao método "quebrarPasv" para obter o número da porta.
        return self.quebrarPasv(conexao.recv(TAM_BUFFER))

    '''
    Retorna o diretório corrente do servidor.
    '''

    def pwd(self, conexao):
        conexao.sendall('PWD\r\n')
        return conexao.recv(TAM_BUFFER)

    '''
    Permite alterar o tipo de formato em que os dados
    serão enviados ao servidor.
    Recebe como parâmetro a conexão já criada e o tipo do formato.
    Retorna a resposta do servidor
    '''

    def type(self, conexao, tipo):
        try:
            conexao.sendall('TYPE %s\r\n' % tipo)
            return conexao.recv(TAM_BUFFER)
        except Exception:
            pass

    '''
    Lista os ficheiros e diretórios presentes no diretório corrente
    do servidor.
    Recebe como parâmetro a conexão já criada e uma conexao de dados,
    por onde os dados serão recebidos.
    Retorna a lista completa.
    '''

    def nlst(self, conexao, conexaoDados):
        conexao.sendall('NLST\r\n')
        conexao.recv(TAM_BUFFER)
        dados = ''

        while True:
            try:
                dados += conexaoDados.recv(TAM_BUFFER)
                if len(dados) == 0:
                    break
            except Exception, e:
                break

        return dados


    def list(self, conexao, conexaoDados):
        conexao.sendall('LIST\r\n')
        return conexaoDados.recv(TAM_BUFFER)

    '''
    Lista os ficheiros e diretórios presentes no diretório corrente
    do servidor.
    Recebe como parâmetro a conexão já criada e o nome do novo diretório.
    Retorna a resposta do servidor.e uma conexao de dados, por onde
    os dados serão recebidos.
    Retorna a lista completa.
    '''

    def mlsd(self, conexao, conexaoDados):
        conexao.settimeout(0.7)
        conexao.sendall('MLSD\r\n')
        conexao.recv(TAM_BUFFER)
        dados = ''

        while True:
            try:
                dados += conexaoDados.recv(TAM_BUFFER)
                if dados[-1] == '\n':
                    break
            except Exception, e:
                break

        return dados

    '''
    Permite criar um novo diretório.
    Recebe como parâmetro a conexão já criada e o nome do novo diretório.
    Retorna a resposta do servidor.
    '''

    def mkd(self, conexao, nomeDiretorio):
        conexao.sendall('MKD %s\r\n' % nomeDiretorio)
        return conexao.recv(TAM_BUFFER)

    '''
    Permite a exclusão de um diretório remoto.
    Recebe como parâmetro a conexão já criada e o nome do novo diretório
    a ser removido do servidor.
    Retorna a resposta do servidor.
    '''

    def rmd(self, conexao, nomeDiretorio):
        conexao.sendall('RMD %s\r\n' % nomeDiretorio)
        return conexao.recv(TAM_BUFFER)

    '''
    Responsável por solicitar ao servidor uma cópia do arquivo recebido
    pelo parâmetro nomeArquivo.
    '''

    def retr(self, conexao, nomeArquivo):
        conexao.sendall('RETR %s\r\n' % nomeArquivo)
        return conexao.recv(TAM_BUFFER)

    '''
	Pede ao servidor que aceite dados que serão enviados através
    de uma conexão de  dados.
    Recebe como parâmetro a conexão já criada e o nome do arquivo
    que será enviado.
    Retorna a resposta do servidor.
    '''

    def stor(self, conexao, nome):
        conexao.sendall('STOR %s\r\n' % nome.encode('ascii'))
        return conexao.recv(TAM_BUFFER)

    '''
    Comando usado para identificar o usuário que será logado no servidor.
    Necessário para ter acesso a uma comunicação de dados.
    '''

    def user(self, conexao, usuario):
        self.usuario = usuario
        conexao.sendall('USER %s\r\n' % usuario)
        return conexao.recv(TAM_BUFFER)

    '''
    Comando usado para identificar a senha para o usuário que será
    logado no servidor.
    Necessário para ter acesso a uma comunicação de dados.
    '''

    def password(self, conexao, password):
        conexao.sendall('PASS %s\n\r' % password)
        return conexao.recv(TAM_BUFFER)

    '''
    Método responsável por quebrar a mensagem recebida como paramêtro.
    '''

    def quebrarPasv(self, mensagem):
        try:
            quebra1 = mensagem.split()
            quebra2 = quebra1[-1].split('.')[0]
            a1 = quebra2.split('(')[1]
            a2 = a1.split(')')[0]
            a3 = tuple(a2.split(','))
            ip1, ip2, ip3, ip4, porta1, porta2 = a3
            return int(porta1) * 256 + int(porta2)
        except IndexError:
            pass

