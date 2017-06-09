function doConnect(url) {
	websocket = new WebSocket(url);
	websocket.onopen = function(evt) { onOpen(evt) };
	websocket.onclose = function(evt) { onClose(evt) };
	websocket.onmessage = function(evt) { onMessage(evt) };
	websocket.onerror = function(evt) { onError(evt) };
}

function onOpen(evt) {
	writeToScreen("connected\n");
}

function onClose(evt) {
	writeToScreen("disconnected\n");
}

function onMessage(evt) {
	writeToScreen("response: " + evt.data + '\n');
}

function onError(evt) {
	writeToScreen('error: ' + evt.data + '\n');
	websocket.close();
}

function doSend(message) {
	writeToScreen("sent: " + message + '\n'); 
	websocket.send(message);
}

function writeToScreen(message) {
	console.log(message);
}

function doDisconnect() {
	websocket.close();
}

function sendAction(action) {
	doSend(JSON.stringify({action: "start"}));
}
