import socket
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 8000)
sock.bind(server_address)

sock.listen(1)
print("server start")

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
        with open("room.json", "r") as f:
            json_data = f.read()

        data = json.loads(json_data)

        isExists = 0
        for room in data['rooms']:
            if room['name'] == params[b"name"].decode():
                isExists = 1

        if isExists == 1:
            response =  b"HTTP/1.1 403 Forbidden\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>The room already exists in the database.</body></html>"
        else:
            data['rooms'].append({"name": params[b"name"].decode(), "reserve": []})
            json_data = json.dumps(data)
            with open('room.json', 'w') as f:
                f.write(json_data)

            response =  b"HTTP/1.1 200 OK\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>The room has been added to the database.</body></html>"

    elif request_path == b"/remove":
        with open("room.json", "r") as f:
            json_data = f.read()

        data = json.loads(json_data)

        index = -1
        indexCounter = -1
        for room in data['rooms']:
            indexCounter = indexCounter + 1
            if room['name'] == params[b"name"].decode():
                index = indexCounter

        if index == -1:
            response =  b"HTTP/1.1 403 Forbidden\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>The room does not exist in the database.</body></html>"
        else:
            
            data['rooms'].remove({"name": params[b"name"].decode()})
            json_data = json.dumps(data)
            with open('room.json', 'w') as f:
                f.write(json_data)

            response =  b"HTTP/1.1 200 OK\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>The room has been removed from the database.</body></html>"

    elif request_path == b"/reserve":
        
        with open("room.json", "r") as f:
            json_data = f.read()
        data = json.loads(json_data)

        isAllow = 0
        isExists = 0
        indexCounter = -1
        outOfBound = 0
        for room in data['rooms']:
            indexCounter = indexCounter + 1
            if room['name'] == params[b'name'].decode():
                index = indexCounter
                isExists = 1
                isAllow = 1
                for reserve in room['reserve']:
                    if reserve['day'] == int(params[b'day'].decode()):
                        for i in range(int(params[b'duration'].decode())):
                            if reserve['hour'] == int(params[b'hour'].decode()) + i:
                                isAllow = 0

        for i in range(int(params[b'duration'].decode())):
            if int(params[b'hour'].decode()) + i not in [9, 10, 11, 12, 13, 14, 15, 16, 17]:
                outOfBound = 1

        if int(params[b'day'].decode()) not in [1, 2, 3, 4, 5, 6, 7] or int(params[b'hour'].decode()) not in [9, 10, 11, 12, 13, 14, 15, 16, 17] :
            response =  b"HTTP/1.1 400 Bad Request\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>Invalid day or hour value.</body></html>"
        elif outOfBound == 1:
            response =  b"HTTP/1.1 400 Bad Request\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>You can reserve between 09.00 and 18.00 hours.</body></html>"
        elif isAllow == 1:
            for i in range(int(params[b'duration'].decode())):
                data['rooms'][index]['reserve'].append({"day": int(params[b'day'].decode()), "hour": int(params[b'hour'].decode()) + i})

            json_data = json.dumps(data)
            with open('room.json', 'w') as f:
                f.write(json_data)

            response =  b"HTTP/1.1 200 OK\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>The room has been reserved.</body></html>"

        elif isExists == 1 and isAllow == 0:
            response =  b"HTTP/1.1 403 Forbidden\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>The room is already reserved.</body></html>"

        elif isExists == 0:
            response =  b"HTTP/1.1 403 Forbidden\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>The room does not exist.</body></html>"


    elif request_path == b"/checkavailability":

        with open("room.json", "r") as f:
            json_data = f.read()
        data = json.loads(json_data)

        busyHours = []
        availabkeHours = []


        isAllow = 0
        isExists = 0
        indexCounter = -1
        outOfBound = 0
        for room in data['rooms']:
            indexCounter = indexCounter + 1
            if room['name'] == params[b'name'].decode():
                index = indexCounter
                isExists = 1
                isAllow = 1
                for reserve in room['reserve']:
                    if reserve['day'] == int(params[b'day'].decode()):
                        busyHours.append(reserve['hour'])

        if int(params[b'day'].decode()) not in [1, 2, 3, 4, 5, 6, 7]:
            response =  b"HTTP/1.1 400 Bad Request\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>Invalid day or hour value.</body></html>"
        elif isExists == 0:
            response =  b"HTTP/1.1 404 Not Found\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>The room does not exist.</body></html>"
        else:
            for i in range(9, 18):
                if i not in busyHours:
                    availabkeHours.append(i)
            response =  b"HTTP/1.1 200 OK\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>"
            response += b"\nDay: " + params[b'day'] + b"  -  Available hours: " + b" - ".join(str(element).encode() for element in availabkeHours)
            response += b"\n</body></html>"


            
    else:
        response = b"HTTP/1.1 404 Not Found\n"

    connection.sendall(response)
    connection.close()