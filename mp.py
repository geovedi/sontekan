#!/usr/bin/python

from math import sqrt
from joblib import Parallel, delayed
Parallel(n_jobs=2)(delayed(sqrt)(i ** 2) for i in range(10))


# XXX: Better use joblib
#NUMBER_OF_PRODUCER_PROCESSES = 3
#NUMBER_OF_CONSUMER_PROCESSES = 3
#
#from multiprocessing import Process, Lock, Queue
#import random, hashlib, time, os
#
#class Consumer:
#    def __init__(self):
#        self.msg = None
#     
#    def consume_msg(self, producer_lock, queue):
#        while(1):
#            print 'Got into consumer method, with pid: %s' % os.getpid()
#            producer_lock.acquire()
#            if queue.qsize() != 0:
#                self.msg = queue.get()
#                print 'got msg: %s' % self.msg
#            else:
#                self.msg = None
#                print 'Queue looks empty'
#            producer_lock.release()
#            time.sleep(random.randrange(5,10))
#
#class Producer:
#    def __init__(self):
#        self.msg = None
#     
#    def produce_msg(self, consumer_lock, queue):
#        while(1):
#            print 'Got into producer method, with pid: %s' % os.getpid()
#            consumer_lock.acquire()
#            self.msg = hashlib.md5(random.random().__str__()).hexdigest()    
#            queue.put(self.msg)
#            print 'Produced msg: %s' % self.msg
#            consumer_lock.release()
#            time.sleep(random.randrange(5,10))
#
#if __name__ == "__main__": 
#    process_pool = []
#    producer_lock = Lock()
#    consumer_lock = Lock()
#    queue = Queue()
#    
#    producer = Producer() 
#    consumer = Consumer()
#
#    for i in (0,NUMBER_OF_PRODUCER_PROCESSES):
#        p = Process(target=producer.produce_msg, args=(consumer_lock, queue,))
#        process_pool.append(p)
#        
#    for i in (0,NUMBER_OF_CONSUMER_PROCESSES):
#        p = Process(target=consumer.consume_msg, args=(producer_lock, queue,))
#        process_pool.append(p)
#
#    for each in process_pool:
#        each.start()

