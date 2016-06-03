#!/usr/bin/python

import common
import server
import time
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from struct import pack, unpack, calcsize
import sys
from Queue import Queue, Empty

reload(sys)
sys.setdefaultencoding('utf-8')

# flags
TESTING = False

# ros imports
import rospy
from geometry_msgs.msg import Twist
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Quaternion, Pose, Point, Vector3
from std_msgs.msg import Header, ColorRGBA
import tf, actionlib
from tf.transformations import euler_from_quaternion
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import std_srvs.srv

# python imports
import sys, select, termios, tty, math, time, os, csv

# global vars
speed = .2
turn = 1
marker_id = 0
markers = {}

box_socket = None
box_connected = False
ENCODE_CODE = '!I'

jobQueue = Queue()


def connect_to_box():
    global box_socket

    listen_socket = socket(AF_INET, SOCK_STREAM)
    listen_socket.bind(('0.0.0.0', BOX_PORT))
    Listen_socket.listen(5)
    listening_socket.settimeout(None)
    box_socket, box_addr = listen_socket.accept()
    box_connected = True

# read positions from file
def read_markers():
    dircur = os.path.dirname(__file__)
    filename = os.path.join(dircur, 'db/db.csv')
    with open(filename, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            create_marker(row[0], float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]), float(row[6]), float(row[7]), float(row[8]))

# create a new marker and add it to screen
def create_marker(name, rad, t0, t1, t2, r0, r1, r2, r3):
        global marker_id
        global markers
        if rad == 0:
            diam = 0.2
            c = ColorRGBA(0.0, 1.0, 0.0, 0.7)
        else:
            diam = float(rad) * 2
            c = ColorRGBA(1.0, 0.0, 0.0, 0.4)
        marker = Marker(type=Marker.SPHERE, id=marker_id,
                        action=Marker.ADD,
                        pose=Pose(Point(t0, t1, t2), Quaternion(r0, r1, r2, r3)),
                        scale=Vector3(diam, diam, diam),
                        header=Header(frame_id='map'),
                        color=c)
        #print marker
        markers[name] = (marker, rad)
        marker_publisher.publish(marker)
        marker_id += 1

# prompts user for name of marker and then go to it
def goto_marker(sac, listener, name):
    global markers
    marker = markers[name][0]

    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = 'map'
    goal.target_pose.header.stamp = rospy.Time.now()
    goal.target_pose.pose = marker.pose

    sac.send_goal(goal)
    success = sac.wait_for_result(rospy.Duration(0))    # CHANGE IT FROM 60 -> 0
    print "move base " + str(success)
    if not success:
        #clear_costmap = rospy.ServiceProxy('/move_base/clear_costmaps', std_srvs.srv.Empty)
        #clear_costmap()
        sac.send_goal(goal)
        success = sac.wait_for_result(rospy.Duration(0))    # SAME AS ABOVE (CHANGE)
        print "move base " + str(success)
    return success

# get distance
def get_distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def worker():
    listening_socket = socket(AF_INET, SOCK_STREAM)
    listening_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    listening_socket.bind(('0.0.0.0', common.POLL_PORT))
    listening_socket.listen(5)
    listening_socket.settimeout(None)

    try:
        while True:
            print "[GOOD NEWS] Waiting for data!"
            client_socket, client_addr = listening_socket.accept()
            print '[GOOD NEWS] Data received!' + str(client_socket) + str(client_addr)
            recv_data = client_socket.recv(common.BUF_SIZE)
            print '[GOOD NEWS] finished'
            # get the code, name, location, and number of snacks
            code_name_loc_num, rest_snacks = recv_data[:common.HEADER_SIZE], recv_data[common.HEADER_SIZE:]
            secret_code, name, location, num_snacks = unpack(common.CODE_NAME_LOC_NUM_ENCODING, code_name_loc_num)

            # strip out any nulls in the string (due to how we pack the data)
            name = name.replace('\0', '')
            location = location.replace('\0', '')


            print '  [DATA-RECEIVED]  secret_code: %d, name: %s, location:%s, num_snacks: %d' % \
                  (secret_code, name, location, num_snacks)
            job = server.Job(name, location, secret_code)
            for i in range(0, num_snacks):
                single_snack, rest_snacks = rest_snacks[:common.SNACK_SIZE], rest_snacks[common.SNACK_SIZE:]
                snack_name, snack_amount = unpack(common.SNACK_ENCODING, single_snack)

                # strip out any nulls in the snack (same reason as the name/location one)
                snack_name = snack_name.replace('\0', '')
                print '    [SNACK-DATA]  snack_name: %s, snack_amount: %d' % (snack_name, snack_amount)
                job.addSnack(snack_name, snack_amount)

            jobQueue.put(job)

            print "job put on queue"
    except KeyboardInterrupt:
        exit()

def dispatchJobs(sac):
    global jobQueue, box_socket, box_connected

    try:
        while (1):
            if not jobQueue.empty():
                job = jobQueue.get(True)
                location = job.location
                secret_code = job.code
                print "doing job"

                if not TESTING:
                    packed_code = pack(ENCODE_CODE, secret_code)
                    #box_socket.sendall(packed_code)
                    #box_socket.close()
                    box_connected = False

                    # start a new thread to listen to a new connection from the both
                    '''
                    t = Thread(target=connect_to_box, args=())
                    t.daemon = True
                    t.start()
                    '''

                    success = goto_marker(sac, listener, location)
                    if not success:
                        print "snack delivery failed"
                    else:
                        print "snack delivery done"
                else:
                    time.sleep(15)
                    success = True

                if not TESTING:
                    if success:
                        #recv_data = box_socket.recv(common.BUF_SIZE)
                        #code = unpack(common.CODE_ENCODING, recv_data)
                        #if code == 1:
                        while not box_connected:
                            continue
                        time.sleep(5)
                        goto_marker(sac, listener, 'base')
                    else:
                        goto_marker(sac, listener, 'base')

                notifyServerDone(job)
    except KeyboardInterrupt:
        exit()

def notifyServerDone(job):
    print "sending to server"
    send_socket = socket(AF_INET, SOCK_STREAM)
    send_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    send_socket.connect(('0.0.0.0', common.SERVICE_PORT))

    send_socket.sendall(str(job.code))
    print "sent to server"

if __name__=="__main__":
    settings = termios.tcgetattr(sys.stdin)

    if not TESTING:
        rospy.init_node('navigator')
        pub = rospy.Publisher('~cmd_vel', Twist, queue_size=5)
        marker_publisher = rospy.Publisher('visualization_marker', Marker)
        sac = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        sac.wait_for_server(rospy.Duration(5))

        listener = tf.TransformListener()
        listener.waitForTransform('/base_link', '/map', rospy.Time(0), rospy.Duration(100000.0))
        (trans,rot) = listener.lookupTransform('/base_link', '/map', rospy.Time(0))

        read_markers()

    x = 0
    th = 0
    status = 0
    count = 0
    acc = 0.1
    target_speed = 0
    target_turn = 0
    control_speed = 0
    control_turn = 0

    # block until the box initially conencts to us
    '''
    listen_socket = socket(AF_INET, SOCK_STREAM)
    listen_socket.bind(('0.0.0.0', common.BOX_PORT))
    Listen_socket.listen(5)
    box_socket, box_addr = listen_socket.accept()
    box_connected = True
    '''

    t = Thread(target=dispatchJobs, args=(sac,))
    t.daemon = True
    t.start()
    # print "[STARTUP]: started dispatcher, lisening to job requests"
    # t = Thread(target=service, args=())
    # t.daemon = True
    # t.start()
    print "[STARTUP]: service ready"
    print "[STARTUP]: ready to receive requests"
    worker()

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
