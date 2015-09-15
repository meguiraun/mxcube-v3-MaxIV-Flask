from flask import session, redirect, url_for, render_template, request, Response
from . import main as mxcube
# from . import mockups#samplecentring, sample, beamline, collection

import logging

@mxcube.route("/")
def serve_static_file():
   #return url_for('static', filename='Main.html')
   print "-----------------" 
   print "serving main html file ***********"
   return mxcube.send_static_file('Main.html')
   #return static_file('Main.html', os.path.dirname(__file__))

# @mxcube.route("/<url:path>")
# def serve_static_file(url):
#    return static_file(url, os.path.dirname(__file__))

###----MOCKUPs----###
@mxcube.route("/mxcube/api/v0.1/mockups/isready", methods=['GET'])
def mockup_ready():
    logging.getLogger('HWR').info('[Routes] Called mockup ready')
    print "mockup ready called  "
    #data = dict(request.POST.items())
    return str(mxcube.mockups.isReady())
@mxcube.route("/mxcube/api/v0.1/mockups/newres/<int:newres>", methods=['PUT'])
def mockup_newres():
    logging.getLogger('HWR').info('[Routes] Called mockup setting new resolution')
    print "mockup setting new resolution called  "
    #data = dict(request.POST.items())
    #return sampleCentring.move(data)
    return mxcube.mockups.setResolution(newres)

###----SSE SAMPLE VIDEO STREAMING----###
keep_streaming = True
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

def stream_video():
    """it just send a message to the client so it knows that there is a new image. A HO is supplying that image"""
    event_id = 0
    logging.getLogger('HWR').info('[Stream] Camera video streaming started')
    while keep_streaming:
        mxcube.sampleCentring.video.new_frame.wait()
        im = mxcube.sampleCentring.video.new_frame.get()
        msg.update({
         'event': 'update',
         'data' : im,
         'id'   : event_id
        })
        #print "mezu bat", str(event_id), str(len(im))
        yield sse_pack(msg)
        event_id += 1
        #gevent.sleep(0.08)
        gevent.sleep(0.1)

@mxcube.route("/mxcube/api/v0.1/samplecentring/camera/subscribe", methods=['GET'])
def subscribeToCamera():
    """SampleCentring: subscribe to the streaming
    data = {generic_data} #or nothing?
    return_data={"url": url}
    """
    #data = dict(request.POST.items())
    logging.getLogger('HWR').info('[Stream] Camera video streaming going to start')
    return Response(stream_video(), mimetype="text/event-stream")

@mxcube.route("/mxcube/api/v0.1/samplecentring/camera/unsubscribe", methods=['GET'])
def unsubscribeToCamera():
    """SampleCentring: subscribe from the streaming
    data = {generic_data} #or nothing?
    return_data={"result": True/False}
    """
    keep_streaming = False
    return True

###----SAMPLE CENTRING----###
@mxcube.route("/mxcube/api/v0.1/samplecentring/<id>/move", methods=['PUT'])
def moveSampleCentringMotor(id):
    """SampleCentring: move "id" moveable to the position specified in the data:position
    Moveable can be a motor (kappa, omega, phi), a ligth, light/zoom level.
    data = {generic_data, "moveable": id, "position": pos}
    return_data={"result": True/False}
    """
    data = json.loads(request.data)
    return mxcube.sampleCentring.move(data)

@mxcube.route("/mxcube/api/v0.1/samplecentring/status", methods=['GET'])
def get_status():
    """SampleCentring: get generic status, positions of moveables ...
    data = {generic_data}
    return_data = { generic_data, 
                  Moveable1:{'Status': status, 'position': position}, 
                  ...,  
                  MoveableN:{'Status': status, 'position': position} 
                  }
    """
    data = dict(request.POST.items())
    return mxcube.sampleCentring.getStatus()

@mxcube.route("/mxcube/api/v0.1/samplecentring/<id>/status", methods=['GET'])
def get_status_of_id(id):
    """SampleCentring: get status of element with id:"id"
    data = {generic_data, 'Moveable1', ..., MoveableN}
    return_data = {'Status': status, 'position': position}
    """
    data = dict(request.POST.items())
    return mxcube.sampleCentring.getStatus(data)

# @mxcube.route("/mxcube/api/v0.1/samplecentring/camera/subscribe", methods=['GET'])
# def subscribeToCamera():
#     """SampleCentring: subscribe to the streaming
#     data = {generic_data} #or nothing?
#     return_data={"url": url}
#     """
#     data = dict(request.POST.items())
#     print "In sample camera"
#     print data
#     return {'url':'/mxcube/api/v0.1/samplecentring/camera/stream'}
#     print "subscribing done"
# @mxcube.route("/mxcube/api/v0.1/samplecentring/camera/unsubscribe", methods=['GET'])
# def unsubscribeToCamera():
#     """SampleCentring: subscribe from the streaming
#     data = {generic_data} #or nothing?
#     return_data={"result": True/False}
#     """
#     print "In sample camera unsubscribe"
#     data = dict(request.POST.items())
#     print "unsubscribing done"
#     return True

@mxcube.route("/mxcube/api/v0.1/samplecentring/centring/<id>", methods=['GET'])
def get_centring_of_id(id):
    """SampleCentring: get centring point position of point with id:"id", id=1,2,3...
    data = {generic_data, "point": id}
    return_data = {"id": {x,y}}
    """
    data = dict(request.POST.items())
    return mxcube.sampleCentring.getCentring(data)

@mxcube.route("/mxcube/api/v0.1/samplecentring/centring/<id>", methods='POST')
def put_centring_with_id(id):
    """SampleCentring: set centring point position of point with id:"id", id=1,2,3...
    data = {generic_data, "point": id, "position": {x,y}}
    return_data={"result": True/False}
    """
    data = dict(request.POST.items())
    return sampleCentring.setCentring(data)

@mxcube.route("/mxcube/api/v0.1/samplecentring/centre", methods=['PUT'])
def centre():
    """Start centring procedure
    data = {generic_data, "Mode": mode}
    return_data={"result": True/False}
    """
    data = dict(request.POST.items())
    return sampleCentring.centre(data)

@mxcube.route("/mxcube/api/v0.1/samplecentring/snapshot", methods=['PUT'])
def snapshot():
    """Save snapshot of the sample view
    data = {generic_data, "Path": path} # not sure if path should be available, or directly use the user/proposal path
    return_data={"result": True/False}
    """
    data = dict(request.POST.items())
    return sampleCentring.snapshot(data)

###----SAMPLE----###
@mxcube.route("/mxcube/api/v0.1/samples/<id>", methods='POST')
def add_sample(id):
    """Add the information of the sample with id:"id"
    data = {generic_data, "SampleId":id, sample_data={'holderLength': 22.0, 'code': None, 'containerSampleChangerLocation': '1', 'proteinAcronym': 'Mnth', 'cellGamma': 0.0, 'cellAlpha': 0.0, 'sampleId': 444179, 'cellBeta': 0.0, 'crystalSpaceGroup': 'R32', 'sampleLocation': '2', 'sampleName': 'sample-E02', 'cellA': 0.0, 'diffractionPlan': {}, 'cellC': 0.0, 'cellB': 0.0, 'experimentType': 'Default'}}
    return_data={"result": True/False}
    """
    data = dict(request.POST.items())
    return samples.addSample(data)

@mxcube.route("/mxcube/api/v0.1/samples/<id>", methods=['PUT'])
def update_sample(id):
    """Update the information of the sample with id:"id"
    data = {generic_data, "SampleId":id, sample_data={'holderLength': 22.0, 'code': None, 'containerSampleChangerLocation': '1', 'proteinAcronym': 'Mnth', 'cellGamma': 0.0, 'cellAlpha': 0.0, 'sampleId': 444179, 'cellBeta': 0.0, 'crystalSpaceGroup': 'R32', 'sampleLocation': '2', 'sampleName': 'sample-E02', 'cellA': 0.0, 'diffractionPlan': {}, 'cellC': 0.0, 'cellB': 0.0, 'experimentType': 'Default'}}
    return_data={"result": True/False}
    """
    data = dict(request.POST.items())
    return samples.updateSample(data)

@mxcube.route("/mxcube/api/v0.1/samples/<id>", methods=['GET'])
def get_sample(id):
    """Get the information of the sample with id:"id"
    data = {generic_data, "SampleId":id}
    return_data={"SampleId":id, sample_data={'holderLength': 22.0, 'code': None, 'containerSampleChangerLocation': '1', 'proteinAcronym': 'Mnth', 'cellGamma': 0.0, 'cellAlpha': 0.0, 'sampleId': 444179, 'cellBeta': 0.0, 'crystalSpaceGroup': 'R32', 'sampleLocation': '2', 'sampleName': 'sample-E02', 'cellA': 0.0, 'diffractionPlan': {}, 'cellC': 0.0, 'cellB': 0.0, 'experimentType': 'Default'}}
    """
    data = dict(request.POST.items())
    return samples.getSample(data)

@mxcube.route("/mxcube/api/v0.1/samples/<id>", methods=['DELETE'])
def delete_sample(id):
    """Delete the sample with id:"id"
    data = {generic_data, "SampleId":id}
    return_data={"result": True/False}
    """
    data = dict(request.POST.items())
    return samples.deleteSample(data)

@mxcube.route("/mxcube/api/v0.1/samples", methods=['GET'])
def get_sample_list():
    """Get the sample list already on the queue
    data = {generic_data}
    return_data={"SampleId1":id, ..., "SampleIdN":id}
    """
    data = dict(request.POST.items())
    return samples.getSampleList()

@mxcube.route("/mxcube/api/v0.1/samples/<id>/mode", methods=['POST'])
def set_sample_mode(id):
    """Set sample changer mode: sample changer, manually mounted, ... (maybe it is enoug to set for all the same mode)
    data = {generic_data, "Mode": mode}
    return_data={"result": True/False}
    """
    data = dict(request.POST.items())
    return samples.getMode(data)

@mxcube.route("/mxcube/api/v0.1/samples/<id>/centring", methods=['PUT'])
def set_centring_mode(id):
    """Set centring method: semi auto, fully auto,  ...
    data = {generic_data, "Mode": mode}
    return_data={"result": True/False}
    """
    data = dict(request.POST.items())
    return samples.setCentring(data)

###----SAMPLECHANGER----###
@mxcube.route("/mxcube/api/v0.1/samples/<id>/mount", methods=['PUT'])
def mount_sample(id):
    """Mount sample with id:"id"
    data = {generic_data, "SampleId": id}
    return_data={"result": True/False}
    """
    data = dict(request.POST.items())
    return samples.mountSample(data)

@mxcube.route("/mxcube/api/v0.1/samples/<id>/umount", methods=['PUT'])
def umount_sample():
    """Umount mounted sample
    data = {generic_data}
    return_data={"result": True/False}
    """
    data = dict(request.POST.items())
    return samples.umountSample(data)

###----COLLECTION----###
@mxcube.route("/mxcube/api/v0.1/samples/<id>/collections/<colid>/mode", methods=['POST'])
def set_collection_method(method):
    """Define the collection method, standard collection, helical, mesh
    data={generic_data, "Method":method}
    return_data={"result": True/False}
    OBSOLETE BY ADD COLLECTION
    """
    data = dict(request.POST.items())
    return mxcube.collection.defineCollectionMethod(data)

@mxcube.route("/mxcube/api/v0.1/samples/<id>/collections/<colid>", methods=['PUT'])
def update_collection(method):
    """update a collection into the sample queue ***asociated to a sample!
    data={generic_data, "Method":method, "SampleId": sampleid ,"CollectionId": id, parameters}, 
    for example for a standard data collection:
    data={generic_data, "Method":StandardCollection, "SampleId": sampleid, "CollectionId": colid, parameters:{
            osc_range: { label: "Oscillation range", default_value: 1.0, value: 0 },
            osc_start: { label: "Oscillation start", default_value: 0, value: 0 },
            exp_time: { label: "Exposure time", default_value: 10.0, value: 0 },
            n_images: { label: "Number of images", default_value: 1, value: 0 },
            energy: {label: "Energy", default_value: 12.3984, value: 0 },
            resolution: {label: "Resolution", default_value: 2.498, value: 0 },
            transmission: {label: "Transmission", default_value: 100.0, value: 0} },
          }, 
    return_data={"result": True/False}
    """
    data = dict(request.POST.items())
    return mxcube.collection.updateCollection(data)

@mxcube.route("/mxcube/api/v0.1/samples/<id>/collections/<colid>", methods=['POST'])
def add_collection(id, colid):
    """Add a collection into the sample queue ***asociate to a sample!
    data={generic_data, "Method":method, "SampleId": sampleid ,"CollectionId": id, parameters}, 
    for example for a standard data collection:
    data={generic_data, "Method":StandardCollection, "SampleId": sampleid, "CollectionId": colid, parameters:{
            osc_range: { label: "Oscillation range", default_value: 1.0, value: 0 },
            osc_start: { label: "Oscillation start", default_value: 0, value: 0 },
            exp_time: { label: "Exposure time", default_value: 10.0, value: 0 },
            n_images: { label: "Number of images", default_value: 1, value: 0 },
            energy: {label: "Energy", default_value: 12.3984, value: 0 },
            resolution: {label: "Resolution", default_value: 2.498, value: 0 },
            transmission: {label: "Transmission", default_value: 100.0, value: 0} },
          }, 
    return_data={"result": True/False}
    """
    data = dict(request.POST.items())
    print data
    return mxcube.collection.addCollection(data)

@mxcube.route("/mxcube/api/v0.1/samples/<id>/collections/<colid>", methods=['GET'])
def get_collection(id):
    """get the collection with id:"colid"
    data={generic_data}, 
    for example for a standard data collection:
    return_data={"Method":StandardCollection,  "SampleId": sampleid, "CollectionId": colid, parameters:{
            osc_range: { label: "Oscillation range", default_value: 1.0, value: 0 },
            osc_start: { label: "Oscillation start", default_value: 0, value: 0 },
            exp_time: { label: "Exposure time", default_value: 10.0, value: 0 },
            n_images: { label: "Number of images", default_value: 1, value: 0 },
            energy: {label: "Energy", default_value: 12.3984, value: 0 },
            resolution: {label: "Resolution", default_value: 2.498, value: 0 },
            transmission: {label: "Transmission", default_value: 100.0, value: 0} },
          }, 
    """
    data = dict(request.POST.items())
    return mxcube.collection.getCollection(data)

@mxcube.route("/mxcube/api/v0.1/samples/<id>/collections", methods=['GET'])
def get_collection_list(id):
    """get the collection with id:"id"
    data={generic_data}, 
    for example for a standard data collection:
    return_data={"Method":StandarCollection,  "SampleId": sampleid, "CollectionId": colid, parameters:{
            osc_range: { label: "Oscillation range", default_value: 1.0, value: 0 },
            osc_start: { label: "Oscillation start", default_value: 0, value: 0 },
            exp_time: { label: "Exposure time", default_value: 10.0, value: 0 },
            n_images: { label: "Number of images", default_value: 1, value: 0 },
            energy: {label: "Energy", default_value: 12.3984, value: 0 },
            resolution: {label: "Resolution", default_value: 2.498, value: 0 },
            transmission: {label: "Transmission", default_value: 100.0, value: 0} },
          }, 
    """
    data = dict(request.POST.items())
@mxcube.route("/mxcube/api/v0.1/samples/<id>/collections/<colid>", methods=['DELETE'])
def delete_collection(id):
    """delete the collection with id:"id"
    data={generic_data, "CollectionId": id},   
    return_data={"result": True/False}
    """
    data = dict(request.POST.items())
    return samples.getCollection(data)
    
@mxcube.route("/mxcube/api/v0.1/samples/<id>/collections/status", methods=['GET'])
def get_collection_status(id):
    """get the status of all data collections, (running, stopped, cancelled, finished, ...)
    data={generic_data},   
    return_data={ {"CollectionId": id1, "Status": status}, ..., {"CollectionId": idN, "Status": status} }
    """
    data = dict(request.POST.items())
    return mxcube.collection.getCollectionStatus(data)

@mxcube.route("/mxcube/api/v0.1/samples/<id>/collections/<colid>/status", methods=['GET'])
def get_collection_id_status(id):
    """get the status of the collection with id:"id", (running, stopped, cancelled, finished, ...)
    data={generic_data},
    return_data={"CollectionId": id, "Status": status}
    """
    data = dict(request.POST.items())
    return mxcube.collection.getCollectionStatus(data)

@mxcube.route("/mxcube/api/v0.1/samples/<sampleid>/collections/<colid>/run", methods=['POST'])
def run_collection(**args):
    """run the collection with id:"colid"
    data={generic_data},
    return_data={"CollectionId": id, "Status": status}
    """
    print "in run collection", args['sampleid'], args['colid']
    data = dict(request.POST.items())
    print data
    #return "collection ok"
    return mxcube.collection.executeCollection(data)
    #return collection.runCollectionStatus(data)

# @mxcube.route("/mxcube/api/v0.1/samples/<id>/collections/<colid>/run", methods='POST')
# def run_queue(id):
#     """run the whole queue
#     data={generic_data},
#     return_data={"CollectionId": id, "Status": status}
#     """
#     data = dict(request.POST.items())
#     print data
#     #return collection.runCollectionStatus(data)

###----BEAMLINE----###
@mxcube.route("/mxcube/api/v0.1/beamline/<id>/move", methods=['PUT'])
def moveBlMotor(id):
    """Beamline: move "id" moveable (energy, resolution ...) to the position specified
    data = {generic_data, "moveable": id, "position": pos}
    return_data={"result": True/False}
    """  
    data = dict(request.POST.items())
    print data, id
    return mxcube.beamline.move(data)

@mxcube.route("/mxcube/api/v0.1/beamline/status", methods=['GET'])
def get_bl_status(id):
    """Beamline: get beamline generic status (energy, resolution ...)
    data = {generic_data}
    return_data = { generic_data, {"moveable1":position}, ..., {"moveableN":position} , xxxx }
    """  
    data = dict(request.POST.items())
    return mxcube.beamline.getStatus()

@mxcube.route("/mxcube/api/v0.1/beamline/<id>/status", methods=['GET'])
def get_bl_id_status(id):
    """Beamline: get beamline status of id:"id"
    data = {generic_data, "Moveable":id}
    return_data = {"Moveable": id, "Status": status}
    """ 
    data = dict(request.POST.items())
    return beamline.getStatus(data)

###----SAMPLE QUEUE----###
