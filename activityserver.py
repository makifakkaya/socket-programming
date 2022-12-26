import socket
import json

class Room:
    def __init__(self, name,):
        self.name = name
        
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 8002)
sock.bind(server_address)

sock.listen(1)
print("activity server start")

while True:
    connection, client_address = sock.accept()

    data = connection.recv(1024)

    request_line = data.split(b"\n")[0]
    request_type, request_uri, http_version = request_line.split(b" ")
    request_path, request_params = request_uri.split(b"?")

    params = {}
    if request_params:
        for param in request_params.split(b"&"):
            key, value = param.split(b"=")
            params[key] = value

    if request_path == b"/add":
        with open("activity.json", "r") as f:
            json_data = f.read()

        data = json.loads(json_data)

        isExists = 0
        for room in data['activities']:
            if room['name'] == params[b"name"].decode():
                isExists = 1

        if isExists == 1:
            response =  b"HTTP/1.1 403 Forbidden\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>The activity already exists in the database.</body></html>"
        else:
            data['activities'].append({"name": params[b"name"].decode()})
            json_data = json.dumps(data)
            with open('activity.json', 'w') as f:
                f.write(json_data)

            response =  b"HTTP/1.1 200 OK\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>The activity has been added to the database.</body></html>"

    elif request_path == b"/remove":
        with open("activity.json", "r") as f:
            json_data = f.read()

        data = json.loads(json_data)
        index = -1
        indexCounter = -1
        for room in data['activities']:
            indexCounter = indexCounter + 1
            if room['name'] == params[b"name"].decode():
                index = indexCounter

        if index == -1:
            response =  b"HTTP/1.1 403 Forbidden\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>The activity does not exist in the database.</body></html>"
        else:
            data['activities'].remove({"name": params[b"name"].decode()})
            json_data = json.dumps(data)
            with open('activity.json', 'w') as f:
                f.write(json_data)

            response =  b"HTTP/1.1 200 OK\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>The activity has been removed from the database.</body></html>"

    elif request_path == b"/check":
        with open("activity.json", "r") as f:
            json_data = f.read()

        data = json.loads(json_data)
        index = -1
        indexCounter = -1
        for room in data['activities']:
            indexCounter = indexCounter + 1
            if room['name'] == params[b"name"].decode():
                index = indexCounter

        if index == -1:
            response =  b"HTTP/1.1 404 Not Found\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>The activity does not exist in the database.</body></html>"
        else:
            response =  b"HTTP/1.1 200 OK\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>The activity exists in the database.</body></html>"

    else:
        response = b"HTTP/1.1 404 Not Found\n"

    connection.sendall(response)
    connection.close()