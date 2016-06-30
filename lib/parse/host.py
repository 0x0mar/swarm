#!/user/bin/python
# -*- coding: utf-8 -*-

import socket
from IPy import IP
from lib.core.logger import LOG



def getlist(**t):
	"""
	return integrated ip and domain name list from target list and file, 
	with network segment parsed
	"""
	try:
		LOG.info('begin to parse target list')
		iplist=[]
		if t['target']!='':
			target=t['target']
			iplist.extend(target)

		if t['target_file']!='':
			target_file=t['target_file']
			f=open(target_file,'r')
			targets=f.read()
			iplist.extend(targets.splitlines())
			f.close()
		# parse network segment and check
		iplist=_unite_list(iplist)
		LOG.info('parse completed')
		return iplist
	except ValueError, e:
		LOG.error('invalid target')
		raise
	except socket.gaierror, e:
		LOG.error('invalid target')
		raise 
	except IOError, e:
		LOG.error('can not open target file')
		raise 

def getswarmlist(**t):
	"""
	return integrated ip and domain name list with port list from swarm list and file 
	like (['127.0.0.1','127.0.0.2','google.com'],[80,90,90])
	"""
	try:
		LOG.info('begin to parse swarm list')
		rawlist=[]
		iplist=[]
		portlist=[]
		if t['swarm']!='':
			swarm=t['swarm']
			rawlist.extend(swarm)

		if t['swarm_file']!='':
			swarm_file=t['swarm_file']
			f=open(swarm_file,'r')
			swarm=f.read()
			rawlist.extend(swarm.splitlines())
			f.close()
		iplist,portlist=_unite_swarmlist(rawlist)
		LOG.info('parse completed')
		return iplist,portlist
	except ValueError, e:
		LOG.error('invalid swarm target')
		raise
	except socket.gaierror, e:
		LOG.error('invalid swarm target')
		raise
	except IndexError, e:
		LOG.error('invalid swarm target')
		raise
	except IOError, e:
		LOG.error('can not open swarm file')
		raise 

def getiplist(srclist):
	"""
	return a complete ip list without domain name in it
	"""
	ret=[]
	for cur in srclist:
		ret.extend(_ipname2ip(cur))
	return ret

def removeip(srclist):
	"""
	remove ip in src(domain name or ip) list
	"""
	ret=[]
	for cur in srclist:
		try:
			IP(cur)
		except ValueError, e:	
			ret.append(cur)
	return ret

def _unite_swarmlist(rawlist):
	"""
	convert rawlist into ip list without domain name
	"""
	retip=[]
	retport=[]
	for x in rawlist:
		ipport=x.split(':')
		port=ipport[1]
		if int(port,10)<0 or int(port,10)>65535:
			raise ValueError('port format error')

		ip=ipport[0]
		# do check 
		_try_ipname2ip(ip)
		retip.append(ip)
		retport.append(int(port,10))
	return (retip,retport)


def _unite_list(srclist):
	"""
	convert srclist into ip and domain name list without network segment
	"""
	ret=[]
	# can not use enumetrate() here
	for cur in srclist:
		# if this is a network segment
		if cur.find('/')!=-1:
			ret.extend(_seg2iplist(cur))
		else:
			# just do check
			_try_ipname2ip(cur)
			ret.append(cur)
	return ret

def _seg2iplist(seg):
	iplist=[]
	ip=IP(seg)
	for x in ip:
		iplist.append(x.strNormal())
	return iplist

def _ipname2ip(src):
	"""
	convert src (domain name or ip) into ip list and do check meanwhile
	"""
	try:
		retip=[]
		retip.append(IP(src).strNormal())
		return retip
	# maybe it is a domain name so we have a try
	except ValueError, e:
		retip=[]
		tmp=socket.getaddrinfo(src,None)
		for cur in tmp:
			retip.append(cur[4][0])
		return {}.fromkeys(retip).keys()

def _try_ipname2ip(src):
	try:
		IP(src)
	except ValueError, e:
		# maybe it is a domain name so we have a try
		socket.getaddrinfo(src,None)

	




