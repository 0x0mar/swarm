#!/user/bin/python
# -*- coding: utf-8 -*-

import socket
import time
import multiprocessing
from lib.core.logger import LOG
from lib.core.swarm_manager import SwarmManager
from scanner.domainsc import DomainScanner

class SSwarm(object):
	"""
	A role of slave in the distributed system.
	"""
	def __init__(self,s_port):
		super(SSwarm, self).__init__()
		self._s_port=s_port
		self._args={}

	def get_parse_args(self):
		# first receive args
		args=self._receive_master()
		sync_flag=args[-8:]
		args=args[:-8]
		self._parse_args(args)
		LOG.debug('complete parsing args')

		if sync_flag=='__SYNC__':
			# do data sync here
			LOG.debug('begin to synchronize data...')
			self._sync_data()
			LOG.debug('data synchronize completed')

	def get_do_task(self):
		proc=[]
		if self._args['process_num']==0:
			for cur in range(multiprocessing.cpu_count()):
				p=multiprocessing.Process(target=self._get_do_task_proc)
				p.start()
				proc.append(p)
		else:
			for cur in range(self._args['process_num']):
				p=multiprocessing.Process(target=self._get_do_task_proc)
				p.start()
				proc.append(p)
		for cur in proc:
			proc.join()
		LOG.debug('task completed')

	def _get_do_task_proc(self):
		self._manager=SwarmManager(address=(self._args['m_addr'], self._args['m_port']),
				authkey=self._args['authkey'])
		self._manager.connect()

		self._task_queue = self._manager.get_task_queue()
		self._result_queue = self._manager.get_result_queue()
		# init scanners and other modules
		self._init_module()
		LOG.debug('begin to get and do task...')
	
		while True:
			task=self._task_queue.get()
			LOG.debug('get task:%s'%task)
			taskl=task.split(':')
			task_flag=taskl[0]
			task_index=taskl[1]
			if task_flag=='__doms__':
				result=self.do_domain_scan(taskl[2:])
			
			elif task_flag=='__off__':
				break

			result=":".join([task_flag,task_index,result])
			LOG.debug('put result:%s'%result)
			self._result_queue.put(result)


	def do_domain_scan(self,task):
		"""
		Task format:
		__doms__:task_index:domain name:dict:dict_path:start_line:scan_lines
		__doms__:task_index:domain name:comp:charset:begin_str:end_str
		Result format:
		__doms__:task_index:result
		Example:
		put task:
		__doms__:26:github.com:dict:2000:3000
		__doms__:980:github.com:comp:ABCDEFGHIJKLMN8980:DAAA:D000
		get result:
		__doms__:980:gist.github.com;XX.github.com
		__doms__:980:no subdomain
		"""
		if task[1]=='dict':
			result=self._domain_scanner.dict_brute(task[0],task[2],task[3],task[4])
		else:
			result=self._domain_scanner.complete_brute(task[0],task[2],task[3],task[4])
		return result

	def do_dir_scan():
		pass

	def do_web_vul_scan():
		pass

	def do_host_vul_scan():
		pass

	def do_try_exp():
		pass

	def do_try_post_exp():
		pass

	def _init_module(self):
		self._domain_scanner=DomainScanner(self._args['thread_num'],self._args['domain_timeout'])

	def _parse_args(self,args):
		l=args.split(',')
		for cur in l:
			pair=cur.split(':')
			LOG.debug('key: %s, value: %s'%(pair[0],pair[1]))
			self._args[pair[0]]=pair[1]
		self._unite_args()

	def _unite_args(self):
		"""
		Correct type of some args.
		"""
		self._args['m_port']=int(self._args['m_port'],10)
		self._args['process_num']=int(self._args['process_num'],10)
		self._args['thread_num']=int(self._args['thread_num'],10)
		self._args['domain_timeout']=float(self._args['domain_timeout'])

	def _sync_data(self):
		print self._receive_master()
		print self._receive_master()
		# TODO: do data sync here
		pass

	def _receive_master(self):
		s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		# incase 'Address already in use error'
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(('',self._s_port))
		LOG.debug('listen on port:%d'%self._s_port)
		s.listen(1)
		sock, addr=s.accept()
		LOG.debug('receive from master host...')
		buff=''
		while True:
			d=sock.recv(4096)
			buff+=d
			if d.find('__EOF__')!=-1:
				break
		sock.send('ack')
		sock.close()
		s.close()
		# cut off last __EOF__
		buff=buff[:-7]
		# return to origin args
		buff=buff.replace('__EOF___','__EOF__')
		return buff
