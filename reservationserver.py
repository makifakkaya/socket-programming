import socket
import json
        
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 8001)
sock.bind(server_address)

sock.listen(1)
print("reservation server start")

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

    if request_path == b"/reserve":
             
        roomserver_address = ("localhost", 8000)
        roomserver_socket = socket.create_connection(roomserver_address)

        activityserver_address = ("localhost", 8002)
        activityserver_socket = socket.create_connection(activityserver_address)

        room_name = params[b"room"].decode()
        activity_name = params[b"activity"].decode()
        day = params[b"day"].decode()
        hour = params[b"hour"].decode()
        duration = params[b"duration"].decode()

        request = f"GET /reserve?name={room_name}&day={day}&hour={hour}&duration={duration} HTTP/1.1\r\n"
        roomserver_socket.sendall(request.encode())

        request = f"GET /check?name={activity_name} HTTP/1.1\r\n"
        activityserver_socket.sendall(request.encode())
        
        response = activityserver_socket.recv(1024)
        response_line = response.decode().split("\r\n")[0]
        http_version, status_code, status_description = response_line.split(" ", 2)
        status_code = int(status_code)
        activityserver_socket.close()

        if status_code == 200:
            activityExists = 1
        else:
            activityExists = 0

        response = roomserver_socket.recv(1024)
        response_line = response.decode().split("\r\n")[0]
        http_version, status_code, status_description = response_line.split(" ", 2)
        status_code = int(status_code)
        roomserver_socket.close()

        

        if activityExists == 0:
            response =  b"HTTP/1.1 404 Not Found\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>The activity does not exist in the database.</body></html>"
        elif status_code == 200:


            activity_name = params[b"activity"].decode()
            room_name = params[b"room"].decode()
            day = int(params[b"day"].decode())
            hour = int(params[b"hour"].decode())
            duration = int(params[b"duration"].decode())

            with open("reservation.json", "r") as f:
                json_data = f.read()

            data = json.loads(json_data)


            if len(data['reservations']) == 0:
                lastIndex = 0
            else:
                lastIndex = data['reservations'][len(data['reservations'])-1]["id"]

            data['reservations'].append({"id": lastIndex+1, "activity_name": activity_name, "room_name": room_name, "day": day, "hour": hour, "duration": duration})
            json_data = json.dumps(data)
            with open('reservation.json', 'w') as f:
                f.write(json_data)

            
            response =  b"HTTP/1.1 200 OK\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>The room has been reserved.</body></html>"
        elif status_code == 403:
            response =  b"HTTP/1.1 403 Forbidden\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>The room is already reserved.</body></html>"
        elif status_code == 400:

            response =  b"HTTP/1.1 400 Bad Request\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>You can reserve between 09.00 and 18.00 hours.</body></html>"

    elif request_path == b"/listavailability":
             
        

        room_name = params[b"room"].decode()
        if b"day" in params:
            day = params[b"day"].decode()
        else:
            day = -1
        print(day)

        if day == -1:
            response_hours = ""
            for i in range(1,8):
                roomserver_address = ("localhost", 8000)
                roomserver_socket = socket.create_connection(roomserver_address)
                request = f"GET /checkavailability?name={room_name}&day={i} HTTP/1.1\r\n"
                roomserver_socket.sendall(request.encode())
                response = roomserver_socket.recv(1024)
                response_line = response.decode().split("\r\n")[0]
                http_version, status_code, status_description = response_line.split(" ", 2)
                status_code = int(status_code)
                if status_code == 200:
                    response_hours += "\n" + response.decode().split("\n")[4]
                
        else:
            roomserver_address = ("localhost", 8000)
            roomserver_socket = socket.create_connection(roomserver_address)
            request = f"GET /checkavailability?name={room_name}&day={day} HTTP/1.1\r\n"
            roomserver_socket.sendall(request.encode())
            response = roomserver_socket.recv(1024)
            response_line = response.decode().split("\r\n")[0]
            http_version, status_code, status_description = response_line.split(" ", 2)
            status_code = int(status_code)
            if status_code == 200:
                response_hours = response.decode().split("\n")[4]
        
        
        roomserver_socket.close()
        
        if status_code == 200:
            response =  b"HTTP/1.1 200 OK\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>"
            response += response_hours.encode()
            response += b"\n</body></html>"


    elif request_path == b"/display":
        with open("reservation.json", "r") as f:
            json_data = f.read()

        data = json.loads(json_data)

        doesExist = 0
        for reservation in data['reservations']:
            if reservation["id"] == int(params[b'id'].decode()):
                doesExist = 1
                theReservation = reservation

        if doesExist == 0:
            response =  b"HTTP/1.1 404 Not Found\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>\n"
            response += b"The reservation does not exist."
            response += b"\n</body></html>"
        else:
            response =  b"HTTP/1.1 200 OK\n"
            response += b"Content-Type: text/html\n"
            response += b"\n"
            response += b"<html><body>\n"
            response += json.dumps(theReservation).encode()
            response += b"\n</body></html>"



    else:
        response = b"HTTP/1.1 404 Not Found\n"

    connection.sendall(response)
    connection.close()