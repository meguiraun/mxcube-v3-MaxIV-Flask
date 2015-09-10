//var WEB_SOCKET_SWF_LOCATION = '/_static/js/socketio/WebSocketMain.swf';

$(document).ready(function(){
	var socket = io.connect('http://' + document.domain + ':' + location.port+'/test');// + namespace);
	console.log('http://' + document.domain + ':' + location.port+'/test')// + namespace)
	// socket.on('connect', function() {
	socket.emit('my event', {data: 'I\'m connected!'});
	// });

	// event handler for server sent data
	// the data is displayed in the "Received" section of the page
	socket.on('test', function(msg) {
		// if(msg['signal'] == 'deviceReady'){
		// 	alert('deviceReady')
		// };
		console.log(msg)
	});
    });