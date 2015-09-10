from flask import session
from flask.ext.socketio import emit, join_room, leave_room
from .. import socketio
from threading import Thread
import time, os
from . import main as mxcube


from HardwareRepository import HardwareRepository
from dispatcher import *


###----SSE SAMPLE VIDEO STREAMING----###
def sse_pack(d):
    """Pack data in SSE format"""
    buffer = ''
    for k in ['retry','id','event','data']:
        if k in d.keys():
            buffer += '%s: %s\n' % (k, d[k])
    return buffer + '\n'
msg = {
    'retry': '1000'
    }  
msg['event'] = 'message'

# @mxcube.route('/mxcube/api/v0.1/samplecentring/camera/stream')
# def stream_video():
#     """it just send a message to the client so it knows that there is a new image. A HO is supplying that image"""
#     bottle.response.content_type = 'multipart/x-mixed-replace; boundary="!>"'
#     response.content_type ="text/event-stream"
#     response.cache_control = 'no-cache'
#     response.headers['content-type'] ='text/event-stream'
#     response.headers['Access-Control-Allow-Origin'] = '*'
#     response.headers['CharacterEncoding'] = "utf-8"
#     event_id = 0
#     print "going to stream video"
#     while True:
#         sampleCentring.video.new_frame.wait()
#         im = sampleCentring.video.new_frame.get()    
#         msg.update({
#          'event': 'update',
#          'data' : im,
#          'id'   : event_id
#         })
#         #print "mezu bat", str(event_id), str(len(im))
#         yield sse_pack(msg)
#         event_id += 1
#         #gevent.sleep(0.08)
#         gevent.sleep(0.1)


def signalCallback(*args):
    emit('my responsess', {'data': 'Server generated  adsfagsdfv', 'count': 3.14159, 'data':args}, namespace='/chat')
    print 'event sent', args
hwr_directory = os.environ["XML_FILES_PATH"]
hwr = HardwareRepository.HardwareRepository(os.path.abspath(hwr_directory))
hwr.connect()
res= hwr.getHardwareObject('/resolution-mockup')
res.connect(res,'deviceReady', signalCallback)
res.connect(res,'positionChanged', signalCallback)  
#res.connect(res,dispatcher.All, signalCallback)  all signal does not seem to work
def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    # froga = aTest.aTest()
    while count<5:
        print "waiting"
        time.sleep(2)
        count += 1
        #froga.bidali(count)
        socketio.emit('my responsess', {'data': 'Server generated event adsfagsdfv', 'count': count}, namespace='/chat')