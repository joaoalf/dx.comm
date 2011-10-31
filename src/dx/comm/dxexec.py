# -*- coding: utf-8 -*-

##
# dxexec - dotX Executor
# Autor: Joao Alfredo Gama Batista <joaoalf@dotx.com.br>
# Versao: 0.1
#

import os
import sys
from threading import *
from dxUtils import Config, Log

_ConfigDefaults = {'dxexec.comandos':'',
				   'dxexec.arquivo' :'exec.txt',
				   'dxexec.logfile' :'dxexec.log'}

class Main(object):
	"""
	classe: Main

	"""
	def __init__(self, inifile='c:\dxcommd\dxcomm.ini'):
		self.inifile = inifile
		self.thread_list = []
		PARAM = Config.leConfig(self.inifile, _ConfigDefaults)
		global logger
		logger = Log(os.path.join(PARAM['principal.raiz'],
								  PARAM['dxexec.logfile']))

		if len(sys.argv) >= 2:
			if not self.eValido(sys.argv[1].lower(),
								PARAM['dxexec.arquivo'].lower()):
				sys.exit(0)
		else:
			if not os.path.exists(os.path.join(PARAM['principal.entrada'],
											   PARAM['dxexec.arquivo'])):
				sys.exit(0)	  
		try:
			os.unlink(os.path.join(PARAM['principal.entrada'],
								   PARAM['dxexec.arquivo']))
		except OSError:
			logger.logEvento('Erro ao excluir arquivo de entrada!!!')
		
		com_list = PARAM['dxexec.comandos'].split(';')
		if com_list:			
			for i in com_list:
				self.thread_list.append(Exec(i))
				logger.logEvento('Iniciando %s' % i)
			##print len(self.thread_list)
			for j in range(len(self.thread_list)):
				self.thread_list[j].start()
			for l in range(len(self.thread_list)):
				self.thread_list[l].join()
		sys.exit(0)

	def eValido(self, entrada, padrao):
		if entrada == padrao:
			return True
		else:
			return False
		
class Exec(Thread):
	"""
	classe: Thread

	"""
	def __init__(self, comando):
		Thread.__init__(self)
		self.comando = comando

	def run(self):
		try:
			os.spawnve(os.P_NOWAIT, self.comando, [self.comando], os.environ)
		except OSError:
			return False
		return True

if __name__ == "__main__":
	app = Main()
	##app.go()
    
