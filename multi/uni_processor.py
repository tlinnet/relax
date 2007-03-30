################################################################################
#                                                                              #
# Copyright (C) 2007  Gary S Thompson (see https://gna.org/users/varioustoxins #
#                                      for contact details)                    #
#                                                                              #
#                                                                              #
# This file is part of the program relax.                                      #
#                                                                              #
# relax is free software; you can redistribute it and/or modify                #
# it under the terms of the GNU General Public License as published by         #
# the Free Software Foundation; either version 2 of the License, or            #
# (at your option) any later version.                                          #
#                                                                              #
# relax is distributed in the hope that it will be useful,                     #
# but WITHOUT ANY WARRANTY; without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
# GNU General Public License for more details.                                 #
#                                                                              #
# You should have received a copy of the GNU General Public License            #
# along with relax; if not, write to the Free Software                         #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA    #
#                                                                              #
################################################################################
import threading, Queue
import sys
import multi
import time,datetime

from multi.processor import Processor,Result_command,Result_string
#class Processor(object):
#    def add_to_queue(self,command,memo=None):
#        pass
#    def run_queue(self):
#        pass
#    def run(self):
#        pass
#    def return_object(self,result):
#        pass
#    def get_name(self):
#        pass
#    def exit(self):
#        pass
#
#    def on_master(self):
#        pass
#
#    def on_slave(self):
#        return not self.on_master()
#
#    def run_command_globally(self,command):
#        queue = [command for i in range(1,MPI.size)]
#        self.run_command_queue(queue)
#
#    def pre_run(self):
#        if self.on_master():
#            self.start_time =  time.time()
#
#    def get_time_delta(self,start_time,end_time):
#        end_time = time.time()
#        time_diff= end_time - self.start_time
#        time_delta = datetime.timedelta(seconds=time_diff)
#        time_delta_str = time_delta.__str__()
#        (time_delta_str,millis) = time_delta_str.rsplit(sep='.',maxsplit=1)
#        return time_delta
#
#    def post_run(self):
#        if self.on_master():
#
#            print 'overall runtime: ' + time_delta_str + '\n'

#FIXME need to subclass
class Uni_processor(Processor):
    def __init__(self,relax_instance):
        self.relax_instance= relax_instance

        self.command_queue=[]
        self.memo_map={}


    def on_master(self):
        return True

    def add_to_queue(self,command,memo=None):
        self.command_queue.append(command)
        if memo != None:
            command.set_memo_id(memo)
            self.memo_map[memo.memo_id()]=memo

    def run_queue(self):
        #FIXME: need a finally here to cleanup exceptions states


        for command in self.command_queue:
            command.run(self)
        #self.run_command_queue()
        #TODO: add cheques for empty queuese and maps if now warn
        del self.command_queue[:]
        self.memo_map.clear()
# FIXME: remove me
#    def run_command_queue(self):
#    		for command in self.command_queue:
#    			command.run(self)

    def run(self):
#        start_time =  time.clock()
        self.pre_run()
        self.relax_instance.run()
        self.post_run()
#        end_time = time.clock()
#        time_diff= end_time - start_time
#        time_delta = datetime.timedelta(seconds=time_diff)
#        print 'overall runtime: ' + time_delta.__str__() + '\n'





    def return_object(self,result):
        if isinstance(result, Exception):
		    #FIXME: clear command queue
		    #       and finalise mpi (or restart it if we can!
		    raise result



        if isinstance(result, Result_command):
            memo=None
            if result.memo_id != None:
                memo=self.memo_map[result.memo_id]
                result.run(self.relax_instance,self,memo)
            if result.memo_id != None and result.completed:
            		del self.memo_map[result.memo_id]

	    elif isinstance(result, Result_string):
	        #FIXME can't cope with multiple lines
	        print result.rank,result.string
	    else:
	        message = 'Unexpected result type \n%s \nvalue%s' %(result.__class__.__name__,result)
	        raise Exception(message)




