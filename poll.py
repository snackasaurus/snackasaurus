#!/usr/bin/python

import common
import server
import time
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM
from struct import unpack, calcsize

from Queue import Empty

def worker():
    listening_socket = socket(AF_INET, SOCK_STREAM)
    listening_socket.bind(('0.0.0.0', common.POLL_PORT))
    listening_socket.listen(5)

    try:
        while True:
            client_socket, client_addr = listening_socket.accept()
            print '[GOOD NEWS] Data received!'
            recv_data = client_socket.recv(common.BUF_SIZE)

            # get the code, name, location, and number of snacks
            code_name_loc_num, rest_snacks = recv_data[:common.HEADER_SIZE], recv_data[common.HEADER_SIZE:]
            secret_code, name, location, num_snacks = unpack(common.CODE_NAME_LOC_NUM_ENCODING, code_name_loc_num)

            # strip out any nulls in the string (due to how we pack the data)
            name = name.replace('\0', '')
            location = location.replace('\0', '')


            print '  [DATA-RECEIVED]  secret_code: 0x%x, name: %s, location:%s, num_snacks: %d' % \
                  (secret_code, name, location, num_snacks)

            for i in range(0, num_snacks):
                single_snack, rest_snacks = rest_snacks[:common.SNACK_SIZE], rest_snacks[common.SNACK_SIZE:]
                snack_name, snack_amount = unpack(common.SNACK_ENCODING, single_snack)

                # strip out any nulls in the snack (same reason as the name/location one)
                snack_name = snack_name.replace('\0', '')
                print '    [SNACK-DATA]  snack_name: %s, snack_amount: %d' % (snack_name, snack_amount)

            #print "waiting for job"
            #server.get_job()
            #print "got job"

            #time.sleep(5)
            #print "job was done"
    except KeyboardInterrupt:
            break

worker()
