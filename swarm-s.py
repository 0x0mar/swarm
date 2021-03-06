#!/user/bin/python
# -*- coding: utf-8 -*-


from lib.core.sswarm import SSwarm
from lib.core.logger import LOG
from socket import timeout
from lib.core.logger import init_logger
from lib.core.logger import LOG
import argparse

def main():
	try:
		parser=argparse.ArgumentParser()
		parser.add_argument('-p',dest='s_port',metavar='LISTEN PORT',type=int,required=True,
			help="Listen port to receive info from master")
		args=parser.parse_args()
		init_logger('log',True,False)

		sswarm=SSwarm(args.s_port)
		# Parse arguments from mswarm
		sswarm.get_parse_args()
		# Ready to get and exec command from master host
		sswarm.get_do_task()

	except Exception, e:
		raise 
	
if __name__=='__main__':
	main()