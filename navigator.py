#!/usr/bin/env python

# ros imports
import rospy
from geometry_msgs.msg import Twist
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Quaternion, Pose, Point, Vector3
from std_msgs.msg import Header, ColorRGBA
import tf, actionlib
from tf.transformations import euler_from_quaternion
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal

# python imports
import sys, select, termios, tty, math, time, os, csv

# global vars
speed = .2
turn = 1
marker_id = 0
markers = {}

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
    rad = markers[name][1]
    if (rad > 0.001):
        while True:
            state = sac.get_state()
            listener.waitForTransform('/base_link', '/map', rospy.Time(0), rospy.Duration(4.0))
            (trans,rot) = listener.lookupTransform('/base_link', '/map', rospy.Time(0))
            dest = get_distance(trans[0], trans[1], marker.pose.position.x, marker.pose.position.y)
            if dest < rad:
                sac.cancel_goal()
                success = True
                break
            time.sleep(0.01)
    success = sac.wait_for_result(rospy.Duration(60))
    print "move base " + str(success)

# get distance
def get_distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

if __name__=="__main__":
    settings = termios.tcgetattr(sys.stdin)

    rospy.init_node('navigator')
    pub = rospy.Publisher('~cmd_vel', Twist, queue_size=5)
    marker_publisher = rospy.Publisher('visualization_marker', Marker)
    sac = actionlib.SimpleActionClient('move_base', MoveBaseAction)
    sac.wait_for_server(rospy.Duration(5))

    listener = tf.TransformListener()
    listener.waitForTransform('/base_link', '/map', rospy.Time(0), rospy.Duration(4.0))
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

    goto_marker(sac, listener, "002")

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
