# -*- coding: utf-8 -*-

##
# DXCOMM - Comunicador dotX
# Autor: Joao Alfredo Gama Batista <joaoalf@dotx.com.br>
# Versao: 4.0
#

import SocketServer
import socket
import string
import os
import sys
import getopt
import time
import datetime
from stat import ST_CTIME
import glob
from threading import *
import dx.utils
from dx.utils import Config, Log

tokens = ['IAM', 'MRC', 'NAL', 'SND', 'ERR']

##ID_SOBRE=wx.NewId()
##ID_CONFIG=1002
##ID_EXIT=1100

if os.name == 'nt':
    _ConfigDefaults = {
        'principal.porta'      :'7781',
        'principal.bufsize'    :'1024',
        'principal.timeout'    :'10',
        'principal.pool'       :'2',
        'principal.raiz'       :'c:\\dxcommd\\',
        'principal.entrada'    :'c:\\dxcommd\\entrada\\',
        'principal.saida'      :'c:\\dxcommd\\saida\\',
        'principal.arq_padrao' :'LOTE.TXT',
        'principal.logfile'    :'dxcomm.log',
        'principal.programa'   :'',
        'principal.server'     :'',
        'principal.regexp'     :'*.*',
        'principal.max_threads':'1',
        'principal.tentativas' :'10'}
    INI_FILE='c:\\dxcommd\\dxcomm.ini'
else:
    _ConfigDefaults = {
        'principal.porta'      :'7781',
        'principal.bufsize'    :'1024',
        'principal.timeout'    :'10',
        'principal.pool'       :'2',
        'principal.raiz'       :'/usr/local/dxcommd/',
        'principal.entrada'    :'/usr/local/dxcommd/entrada/',
        'principal.saida'      :'/usr/local/dxcommd/saida/',
        'principal.arq_padrao' :'lote.txt',
        'principal.logfile'    :'dxcomm.log',
        'principal.programa'   :'',
        'principal.server'     :'',
        'principal.regexp'     :'[0-9][0-9][0-9][0-9]/*/*',
        'principal.max_threads':'10',
        'principal.tentativas' :'3'}
    INI_FILE='/usr/local/dxcommd/dxcomm.ini'

class Controlador(SocketServer.BaseRequestHandler):
    """
    classe: Controlador
    Controla o dialogo entre o cliente e o servidor.
    """

    log_string = ''
    vem_data = 0
    vem_data_ok = 0
    tamanho_data = 0
    nome_data = ''
    terminar = 0

    def handle(self):
        while 1:
            if self.terminar == 1: break
            if self.vem_data == 0:
                dados = self.request.recv(self.server.bufsize)
                if not dados: break
            else:
                if not self.nome_data:
                    self.nome_data = self.server.arq_padrao
                fd = file(os.path.join(self.server.entrada_dir,self.nome_data),
                          'wb+')
                ##print 'p2' + str(self.tamanho_data)
                falta_receber = self.tamanho_data
                tentativa = 0
                while falta_receber > 0:
                    dados = self.request.recv(self.server.bufsize)
                    ##else:
                    ##    dados = self.request.recv(falta_receber)
                    if not dados:
                        tentativa += 1
                        time.sleep(0.5)
                        if tentativa >= 10: break
                    else:
                        fd.write(dados)
                        falta_receber = falta_receber - len(dados)
                    ##print falta_receber
                fd.close()
            self.request.send(self.validaDados(dados))
        logger.logEvento(self.log_string)
        if self.vem_data_ok:
            if self.server.comando:
                comando = ''.join((self.server.comando,' ', self.nome_data))
                self.log_string = 'Executando programa (%s)...' % comando
                if not os.system(comando):
                    self.log_string += 'OK'
                else:
                    self.log_string += 'ERRO'
                logger.logEvento(self.log_string)

    def validaDados(self, d):
        if self.vem_data == 1:
            rcbd = os.path.getsize(os.path.join(self.server.entrada_dir,
                                                self.nome_data))
            if rcbd == self.tamanho_data:
                self.log_string += 'OK'
                self.vem_data_ok = 1
            else:
                self.log_string+='(ERRO %i =! %i)' % (rcbd, self.tamanho_data)
                try:
                    os.unlink(os.path.join(self.server.entrada_dir,
                                           self.nome_data))
                    self.log_string+='Removendo %s' % \
                                      os.path.join(self.server.entrada_dir,
                                                   self.nome_data)
                except OSError:
                    self.log_string+='Falha na remocao de %s' % \
                                      os.path.join(self.server.entrada_dir,
                                                   self.nome_data)

            ##Utils.logEvento(log_file, self.log_string)
            self.terminar = 1
            return 'MRC\r\n'
        else:
            token = d[:3]
            args = d[3:-2]
            if token in tokens:
                if token == tokens[0]:
                    self.log_string += 'Conexao (%s), ' % args
                    return 'MRC\r\n'
                elif token == tokens[2]:
                    self.log_string += 'arquivo (%s), ' % args.lower()
                    self.nome_data = args.lower()
                    return 'MRC\r\n'
                elif token == tokens[3]:
                    self.log_string += 'recebendo %s byes...' %args
                    self.vem_data = 1
                    self.tamanho_data = int(args)
                    return 'MRC\r\n'
            else:
                return 'ERR\r\n'


class Main(object):
    """
    classe: Main
    Classe principal da aplicacao.
    """
    def __init__(self, inifile='dxcomm.ini', name='Main'):
        if os.name == 'nt':
            self.usa_gui = True
        else:
            self.usa_gui = False
        self.inifile = inifile

        try:
            opts, args=getopt.getopt(sys.argv[1:], "hcg", ["help", "config=", "gui"])
        except getopt.GetoptError:
            self.usage()
            sys.exit(2)
        output = None
        verbose = False
        for o, a in opts:
            if o in ('-h', '--help'):
                self.usage()
                sys.exit()
            if o in ('-c', '--config'):
                self.inifile=a
            if o in ('-g', '--gui'):
                self.usa_gui = True
                #global Taskbar
                #from gui import Taskbar
                #print "usa_gui: True"

        self.PARAM = Config.leConfig(self.inifile, _ConfigDefaults)

        global logger
        logger = Log(os.path.join(self.PARAM['principal.raiz'],
                                  self.PARAM['principal.logfile']))
        try:
            os.chdir(self.PARAM['principal.raiz'])
        except OSError:
            logger.logEvento('Criando diretorio raiz...')        
            os.mkdir(self.PARAM['principal.raiz'])
            os.chdir(self.PARAM['principal.raiz'])
        try:
            os.listdir(self.PARAM['principal.saida'])
        except OSError:
            logger.logEvento('Criando diretorio de saida...')
            os.mkdir(self.PARAM['principal.saida'])
        try:
            os.listdir(self.PARAM['principal.entrada'])
        except OSError:
            logger.logEvento('Criando diretorio de entrada...')
            os.mkdir(self.PARAM['principal.entrada'])

        if os.name == 'nt':
            self.limpaAntigos(self.PARAM['principal.saida'])
            
        self.criarServidor()
        self.criarCliente(1)
        
    def criarServidor(self):
        self.srv1 = Servidor(int(self.PARAM['principal.porta']),
                             int(self.PARAM['principal.bufsize']),
                             self.PARAM['principal.programa'],
                             self.PARAM['principal.entrada'],
                             self.PARAM['principal.arq_padrao'])
        self.srv1.setDaemon(1)

    def criarCliente(self, tipo):
        self.cli_ped = Cliente(int(self.PARAM['principal.porta']),
                               int(self.PARAM['principal.bufsize']),
                               self.PARAM['principal.saida'],
                               int(self.PARAM['principal.timeout']),
                               int(self.PARAM['principal.pool']),
                               self.PARAM['principal.server'],
                               self.PARAM['principal.regexp'],
                               int(self.PARAM['principal.max_threads']),
                               int(self.PARAM['principal.tentativas']))

        self.cli_ped.setDaemon(1)
       
    def go(self):
        logger.logEvento('Iniciando dxcomm (plataforma: %s' % os.name + ')')
        if self.usa_gui:
            import gui
            a = gui.Taskbar(self.PARAM)
            self.srv1.start()
            self.cli_ped.start()
            a.MainLoop()
            self.cli_ped.join(1.0)
            self.srv1.join(1.0)
        else:
            self.srv1.start()
            self.cli_ped.start()
            while 1:
                try:
                    time.sleep(1.0)
                    if not self.cli_ped.isAlive():
                        logger.logEvento('Thread (Cliente) terminou... reiniciando...')
                        self.cli_ped.join(1.0)
                        del self.cli_ped
                        self.criarCliente(1)
                        self.cli_ped.start()
                    if not self.srv1.isAlive():
                        logger.logEvento('Thread (Servidor) terminou... reiniciando...')
                        self.srv1.join(1.0)
                        del self.srv1
                        self.criarServidor()
                        self.srv1.start()
                except KeyboardInterrupt:
                    self.cli_ped.join(1.0)
                    #self.cli_plu.join(1.0)
                    self.srv1.join(1.0)
                    break
        logger.logEvento('Terminando aplicacao!!')
        sys.exit(0)            

    def limpaAntigos(self, caminho):
        """Remove os arquivos antigos do diretório de pedido"""

        for arquivo in os.listdir(caminho):
            if arquivo != 'RECYCLED' and datetime.date.fromtimestamp(os.stat(os.path.join(caminho, arquivo))[ST_CTIME]) < datetime.date.today():
                os.unlink(os.path.join(caminho, arquivo))
                
    def usage(self):
        """Mensagem de ajuda do programa"""
        print """dotX Communicator daemon (dxcommd)
2003, 2011 (C) JJLR Consultoria e Servicos Ltda

Uso: dxcommd [opcoes]

opcoes:

-h --help       Exibe esta mensagem de ajuda.
-c --config=    Informa o arquivo de configuracao a ser usado.
-g --gui        Usa interface grafica.
"""

class Servidor(Thread, SocketServer.ThreadingTCPServer):
    """
    classe: Servidor
    Wrapper da thread do servidor
    """

    def __init__(self, porta, bufsize, comando, entrada_dir, arq_padrao,
                 name='Servidor'):
        self.allow_reuse_address = 1
        self.daemon_threads = 1
        self.bufsize = bufsize
        self.comando = comando
        self.entrada_dir = entrada_dir
        self.arq_padrao = arq_padrao
        Thread.__init__(self, name=name)
        SocketServer.ThreadingTCPServer.__init__(self, ('',porta), Controlador)
        self._stopevent = Event()
        self._sleepperiod = 1.0

    def run(self):
        logger.logEvento('Iniciando Thread (Servidor)')
        while not self._stopevent.isSet():
            self.handle_request()
            self._stopevent.wait(self._sleepperiod)
        logger.logEvento('Terminando Thread (Servidor)')

    def join(self, timeout=None):
        self._stopevent.set()
        Thread.join(self, timeout)

class Cliente(Thread):
    """
    classe: Cliente
    Faz o pooling do diretorio e envia os arquivos para o servidor remoro
    """

    def __init__(self, porta, bufsize, saida_dir, timeout, pool,
                 server, regexp, max_threads, tentativas, name='Cliente'):
        Thread.__init__(self, name=name)
        self._stopevent = Event()
        self._sleepperiod = 1.0
        self.bufsize = bufsize
        self.saida_dir = saida_dir
        self.porta = porta
        self.timeout = timeout
        self.pool = pool
        self.server = server
        self.regexp = regexp
        self.name = name
        self.max_threads = max_threads
        self.tentativas = tentativas
        self.thread_list = {}

    def run(self):
        n=0
        logger.logEvento('Iniciando Thread (%s)' % self.name)
        os.chdir(self.saida_dir)
        while not self._stopevent.isSet():
            for lote in glob.glob(self.regexp)[:self.max_threads]:
                ##print lote
                n=n+1
                thread_name = ''.join(['EnviaLote', str(n)])
                self.thread_list[thread_name] = EnviaLote(self.porta,
                                                          self.bufsize,
                                                          self.timeout,
                                                          self.server,
                                                          lote,
                                                          self.tentativas,
                                                          thread_name)
                self.thread_list[thread_name].start()
                ##if self.enviaLote(lote, self.server):
                ##    self.log_string+='...OK'
                ##else:
                ##    self.log_string+='...ERR'
                ##logger.logEvento(self.log_string)
            for t in self.thread_list.values():
                #t.join(self.timeout)
                if not t.isAlive():
                    self.thread_list.pop(t.getName())
            time.sleep(self.pool)
            self._stopevent.wait(self._sleepperiod)

    def join(self, timeout=None):
        logger.logEvento('Terminando Thread (%s)' % self.name)
        self._stopevent.set()
        Thread.join(self, timeout)

class EnviaLote(Thread):

    def __init__(self, porta, bufsize, timeout, server, lote,
                 tentativas, name='EnviaLote'):
        Thread.__init__(self, name=name)
        self._stopevent = Event()
        self._sleepperiod = 1.0
        self.bufsize = bufsize
        self.porta = porta
        self.timeout = timeout
        self.server = server
        self.lote = lote
        self.tentativas = tentativas
        self.name = name

    def run(self):
        n=0
        while True:
            n=n+1
            if n > self.tentativas:
                break
            
            dir1, arq = os.path.split(self.lote)
            if self.server == None or self.server == '':
                self.server = dir1.split('/')[1]
            ##print self.log_string
            lote_gerado = False
            while not lote_gerado:
                try:
                    tam1 = os.stat(self.lote)[6]
                    time.sleep(0.5)
                    tam2 = os.stat(self.lote)[6]
                except:
                    return False
                if tam1 == tam2:
                    lote_gerado = True
            self.log_string = 'Enviando (%s) para (%s)... Tentativa %i (%s) ' \
                              % (arq, self.server, n, self.name)
            #self.log_string='Conectando com %s (%s)' % (self.server, self.name)
            self.csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.csock.settimeout(self.timeout)
            try:
                fd = file(self.lote, 'rb')
            except IOError:
                self.csock.close()
                self.log_string += '(ERRO: ABERTURA DO ARQUIVO)'
                ##return False
                continue
            try:
                dxUtils.lock(fd, dxUtils.LOCK_EX | dxUtils.LOCK_NB)
            except IOError:
                #rint 'NoLock!'
                self.csock.close()
                fd.close()
                self.log_string += '(ERRO: TRAVAMENTO DO ARQUIVO)'
                ##return False
                continue

            try:
                self.csock.connect((self.server, self.porta))
            except:
                self.csock.close()
                self.log_string += '(ERRO: CONEXAO COM SERVIDOR)'
                ##return False
                continue
            try:
                self.csock.send('IAM'+socket.gethostname()+'\r\n')
                data = self.csock.recv(self.bufsize)
                if not data or data[:3] == 'ERR':
                    try:
                        self.csock.close()
                    except:
                        pass
                    self.log_string += '(ERRO: SERVIDOR TERMINOU INESPERADAMENTE)'
                    ##return False
                    continue

            except socket.error:
                self.csock.close()
                self.log_string += '(ERRO: SERVIDOR TERMINOU INESPERADAMENTE)'
                ##return False
                continue
            try:
                self.csock.send('NAL'+arq+'\r\n')
                data = self.csock.recv(self.bufsize)
                if not data or data[:3] == 'ERR':
                    try:
                        self.csock.close()
                    except:
                        pass
                    self.log_string += '(ERRO: SERVIDOR TERMINOU INESPERADAMENTE)'
                    ##return False
                    continue
            except socket.error:
                self.csock.close()
                self.log_string += '(ERRO: SERVIDOR TERMINOU INESPERADAMENTE)'
                ##return False
                continue
            tam = os.path.getsize(self.lote)
            #tam = os.stat(lote)[6]
            self.log_string='Enviando %s (%i bytes) para loja %s (%s)' % (arq, tam,
                                                                          self.server,
                                                                          self.name)
            try:
                self.csock.send('SND'+str(tam)+'\r\n')
                data = self.csock.recv(self.bufsize)
                if not data or data[:3] == 'ERR':
                    try:
                        self.csock.close()
                    except:
                        pass
                    self.log_string += '(ERRO: SERVIDOR TERMINOU INESPERADAMENTE)'
                    ##return False
                    continue
            except socket.error:
                self.csock.close()
                self.log_string += '(ERRO: SERVIDOR TERMINOU INESPERADAMENTE)'
                ##return False
                continue
            ##falta = os.path.getsize(lote)
            ##falta = ''
            #logger.logEvento(self.log_string)
            chuck=''
            sent=0
            tentativa=0
            espera=0.5
            while tam > 0:
                if tam < self.bufsize:
                    try:
                        chunck = fd.read(tam)
                    except ValueError:
                        fd.close()
                        break
                    ##print 'Bloco final'
                else:
                    try:
                        chunck = fd.read(self.bufsize)
                    except ValueError:
                        break
                #print 'Bloco: %i\nFalta: %i' % (len(chunck), tam)
                if not chunck:
                    tentativa +=1
                    #print "Tentativa de leitura do arquivo ", tentativa
                    time.sleep(espera)
                    espera += 0.5
                    if tentativa >= 10:
                        self.log_string += '(ERRO: LEITURA DO ARQUIVO)'
                        fd.close()
                        self.csock.close()
                        break
                else:
                    try:
                        sent = self.csock.send(chunck)
                    except socket.error:
                        fd.close()
                        self.csock.close()
                        self.log_string += '(ERRO: SOCKET)'
                    if not sent:
                        tentativa +=1
                        #print "Tentativa de envio dos dados ", tentativa
                        time.sleep(0.5)
                        if tentativa >= 10:
                            self.log_string += '(ERRO: ENVIANDO DADOS)'
                            fd.close()
                            self.csock.close()
                            break
                    tam -= sent

            ##print "Falta: %i" % tam
            dxUtils.unlock(fd)
            fd.close()
            if tam == 0:
                apagou=False
                while not apagou:
                    try:
                        os.unlink(self.lote)
                        apagou=True
                    except:
                        try:
                            os.rename(self.lote, self.lote+".xxx")
                            apagou=True
                        except:
                            time.sleep(1)
            try:
                data = self.csock.recv(self.bufsize)
            except:
                self.log_string += '(TEMPO ESGOTADO OU CONEXAO PERDIDA)'
            if not data or data[:3] == 'ERR': return False
            self.log_string += '...OK'
            logger.logEvento(self.log_string)

            self.csock.close()
            return True
        logger.logEvento(self.log_string)
        ##dxUtils.unlock(fd)
        ##fd.close()
        apagou=False
        while not apagou:
            try:
                os.unlink(self.lote)
                apagou=True
            except:
                try:
                    os.rename(self.lote, self.lote+".xxx")
                    apagou=True
                except:
                    time.sleep(1)
        ##os.unlink(self.lote)
        logger.logEvento("Limite de tentativas excedido para arquivo (%s)" % arq)
        return False
    
    def join(self, timeout=None):
        logger.logEvento('Terminando Thread (%s)' % self.name)
        self._stopevent.set()
        Thread.join(self, timeout)

if __name__ == "__main__":
    app = Main(INI_FILE)
    app.go()

