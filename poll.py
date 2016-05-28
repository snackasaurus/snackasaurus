#!/usr/bin/python

import common
import server
import time
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM
from struct import pack, unpack, calcsize
import sys
from Queue import Queue, Empty

reload(sys)
sys.setdefaultencoding('utf-8')

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

# flags
TESTING = True

# global vars
speed = .2
turn = 1
marker_id = 0
markers = {}

box_socket = None
ENCODE_CODE = '!I'

jobQueue = Queue()


def connect_to_box():
    global
    listen_socket = socket(AF_INET, SOCK_STREAM)
    listen_socket.bind(('0.0.0.0', BOX_PORT))
    Listen_socket.listen(5)
    box_socket, box_addr = listen_socket.accept()

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
        clear_costmap = rospy.ServiceProxy('/move_base/clear_costmaps', std_srvs.srv.Empty)
        clear_costmap()
        sac.send_goal(goal)
        success = sac.wait_for_result(rospy.Duration(0))    # SAME AS ABOVE (CHANGE)
        print "move base " + str(success)
    return success

# get distance
def get_distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)


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


            print '  [DATA-RECEIVED]  secret_code: %d, name: %s, location:%s, num_snacks: %d' % \
                  (secret_code, name, location, num_snacks)

            for i in range(0, num_snacks):
                single_snack, rest_snacks = rest_snacks[:common.SNACK_SIZE], rest_snacks[common.SNACK_SIZE:]
                snack_name, snack_amount = unpack(common.SNACK_ENCODING, single_snack)

                # strip out any nulls in the snack (same reason as the name/location one)
                snack_name = snack_name.replace('\0', '')
                print '    [SNACK-DATA]  snack_name: %s, snack_amount: %d' % (snack_name, snack_amount)

            jobQueue.put((location, secret_code))

            #print "waiting for job"
            #server.get_job()
            #print "got job"

            #time.sleep(5)
            #print "job was done"
    except KeyboardInterrupt:
        exit()

def dispatchJobs():
    global jobQueue, box_socket
    connect_to_box()
    while (1):
        if not jobQueue.empty():
            location, secret_code = jobQueue.get(True)
            print "doing job"

            packed_code = pack(ENCODE_CODE, secret_code)
            box_socket.sendall(packed_code)
            success = goto_marker(sac, listener, location) # brings robot back to the base
            if not success:
                print "snack delivery failed"
            else:
                print "snack delivery done"

            if success:
                recv_data = box_socket.recv(common.BUF_SIZE)
                code = unpack(common.CODE_ENCODING, recv_data)
                if code == 1:
                    time.sleep(30)
                    goto_marker(sac, listener, 'base')
            else:
                goto_marker(sac, listener, 'base')

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

    t = Thread(target=dispatchJobs, args=())
    t.daemon = True
    t.start()
    print "started dispatcher, lisening to job requests"
    worker()
    print "ready to receive requests"

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
