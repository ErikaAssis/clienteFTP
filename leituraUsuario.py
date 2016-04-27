# coding: utf-8

from os import system
import getpass

'''
Classe com métodos responsáveis pela entrada de dados
e saída de dados para o usuário da aplicação.
'''


class IOUsuario():

    def lerSenha(self):
        return getpass.getpass('Informe sua senha:')

    def lerString(self, mensagem):
        return raw_input(mensagem + ":")

    def lerNumeroInteiroPositivo(self, mensagem):
        try:
            numero = int(raw_input(mensagem + ":"))
            if numero >= 0:
                return numero
            else:
                return None
        except ValueError:
            print '\nValor digitado não é um número inteiro.'
            print 'Repetir a operação.'

    def enviarMensagem(self, mensagem):
        print mensagem

    def pausarAplicacao(self):
        raw_input('\nDigite Enter para continuar...')

    def limparTela(self):
        system('clear')

