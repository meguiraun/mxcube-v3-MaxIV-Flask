from flask import Blueprint
from .. import socketio
from HardwareRepository import HardwareRepository
main = Blueprint('main', __name__,static_folder='static')

import routes, events, src.RestParser, os 
hwr_directory = os.environ["XML_FILES_PATH"]
main.hwr = HardwareRepository.HardwareRepository(os.path.abspath(hwr_directory))
main.hwr.connect()
main.mockups = src.RestParser.MockUps(main.hwr)
main.sampleCentring = src.RestParser.SampleCentring(main.hwr)
main.sample = src.RestParser.Sample(main.hwr)
main.beamline = src.RestParser.BeamLine(main.hwr) 
main.collection = src.RestParser.Collection(main.hwr) 
