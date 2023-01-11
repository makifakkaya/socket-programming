import threading
import socket
import json
        
# create a socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket to localhost:8080
server_address = ('localhost', 8080)
sock.bind(server_address)

# start listening for incoming connections
sock.listen(1)
print("reservation server start")

# define request function
def request():
    try:
        
        # accept a connection
        connection, client_address = sock.accept()

        data = connection.recv(1024)

        # Split the request line into its individual parts
        request_line = data.split(b"\n")[0]

        # split the first line by space character to extract request type, request URI and HTTP version
        request_type, request_uri, http_version = request_line.split(b" ")

        # Split the request URI at the '?' character
        if b"?" in request_uri:
            request_path, request_params = request_uri.split(b"?", 1)
        else:
            request_path = request_uri
            request_params = b""

        # Create an empty dictionary to store the request parameters
        params = {}
        
        # If the request has any parameters
        if request_params:
            for param in request_params.split(b"&"):
                # Split the parameter at the '=' character
                key, value = param.split(b"=")
                # Add the key-value pair to the params dictionary
                params[key] = value

        # If the request path is '/reserve'
        if request_path == b"/reserve":
                
            # ROOM SERVER
            roomserver_address = ("localhost", 8081)
            roomserver_socket = socket.create_connection(roomserver_address)

            # ACTIVITY SERVER
            activityserver_address = ("localhost", 8082)
            activityserver_socket = socket.create_connection(activityserver_address)

            # Create variable to store paramaters
            room_name = params[b"room"].decode()
            activity_name = params[b"activity"].decode()
            day = params[b"day"].decode()
            hour = params[b"hour"].decode()
            duration = params[b"duration"].decode()

            # Send request to ROOM SERVER
            request = f"GET /reserve?name={room_name}&day={day}&hour={hour}&duration={duration} HTTP/1.1\r\n"
            roomserver_socket.sendall(request.encode())

            # Send request to ACTIVITY SERVER
            request = f"GET /check?name={activity_name} HTTP/1.1\r\n"
            activityserver_socket.sendall(request.encode())
            
            # Get response from ACTIVITY SERVER
            response = activityserver_socket.recv(1024)
            response_line = response.decode().split("\r\n")[0]
            http_version, status_code, status_description = response_line.split(" ", 2)
            status_code = int(status_code)
            activityserver_socket.close()

            # Understanding from response code
            if status_code == 200:
                activityExists = 1
            else:
                activityExists = 0

            # Get response from ROOM SERVER
            response = roomserver_socket.recv(1024)
            response_line = response.decode().split("\r\n")[0]
            http_version, status_code, status_description = response_line.split(" ", 2)
            status_code = int(status_code)
            roomserver_socket.close()

            # If does not exist
            if activityExists == 0:
                # Set the response to a 404 Not Found status with a message
                response =  b"HTTP/1.1 404 Not Found\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>The activity does not exist in the database.</body></html>"
            # If exists
            elif status_code == 200:
                # Store paramaters
                activity_name = params[b"activity"].decode()
                room_name = params[b"room"].decode()
                day = int(params[b"day"].decode())
                hour = int(params[b"hour"].decode())
                duration = int(params[b"duration"].decode())

                # Open 'reservation.json' file to read
                with open("reservation.json", "r") as f:
                    json_data = f.read()

                data = json.loads(json_data)

                # Find last index of array. # If length is zero, last index is 0
                if len(data['reservations']) == 0:
                    lastIndex = 0
                else:
                    lastIndex = data['reservations'][len(data['reservations'])-1]["id"]

                # Add new reservation value with ID.
                data['reservations'].append({"id": lastIndex+1, "activity_name": activity_name, "room_name": room_name, "day": day, "hour": hour, "duration": duration})
                json_data = json.dumps(data)
                
                # Write to file.
                with open('reservation.json', 'w') as f:
                    f.write(json_data)

                # Set the response to a 200 OK status with a message
                response =  b"HTTP/1.1 200 OK\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>The room has been reserved.</body></html>"
            elif status_code == 403:
                # Set the response to a 403 Forbidden error with a message
                response =  b"HTTP/1.1 400 Forbidden\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>Invalid.</body></html>"
            elif status_code == 400:
                # Set the response to a 400 Bad Request error with a message
                response =  b"HTTP/1.1 400 Bad Request\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>You can reserve between 09.00 and 18.00 hours.</body></html>"

        # If the request path is '/listavailability'
        elif request_path == b"/listavailability":
            
            # Store paramaters
            room_name = params[b"room"].decode()

            # If send day info or not.
            if b"day" in params:
                # Get day info if send
                day = params[b"day"].decode()
            else:
                day = -1

            # If there is no day info
            if day == -1:
                response_hours = ""

                # Send request for all days.
                for i in range(1,8):
                    # Connect to ROOM SERVER
                    roomserver_address = ("localhost", 8081)
                    roomserver_socket = socket.create_connection(roomserver_address)
                    request = f"GET /checkavailability?name={room_name}&day={i} HTTP/1.1\r\n"
                    roomserver_socket.sendall(request.encode())
                    response = roomserver_socket.recv(1024)
                    response_line = response.decode().split("\r\n")[0]
                    http_version, status_code, status_description = response_line.split(" ", 2)
                    status_code = int(status_code)
                    # If OK
                    if status_code == 200:
                        response_hours += "\n" + response.decode().split("\n")[4]
            # If send day info
            else:
                # Connect to ROOM SERVER
                roomserver_address = ("localhost", 8081)
                roomserver_socket = socket.create_connection(roomserver_address)
                request = f"GET /checkavailability?name={room_name}&day={day} HTTP/1.1\r\n"
                roomserver_socket.sendall(request.encode())
                response = roomserver_socket.recv(1024)
                response_line = response.decode().split("\r\n")[0]
                http_version, status_code, status_description = response_line.split(" ", 2)
                status_code = int(status_code)
                # Get informations
                if status_code == 200:
                    response_hours = response.decode().split("\n")[4]
            
            
            roomserver_socket.close()
            
            # If ok, return hours.
            if status_code == 200:
                response =  b"HTTP/1.1 200 OK\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>"
                response += response_hours.encode()
                response += b"\n</body></html>"

        # If the request path is '/display'
        elif request_path == b"/display":

            # open 'reservation.json' file to read.
            with open("reservation.json", "r") as f:
                json_data = f.read()

            data = json.loads(json_data)


            doesExist = 0
            for reservation in data['reservations']:
                # If exists
                if reservation["id"] == int(params[b'id'].decode()):
                    doesExist = 1
                    theReservation = reservation

            # If does not exist
            if doesExist == 0:
                # Set the response to a 404 Not Found error with a message
                response =  b"HTTP/1.1 404 Not Found\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>\n"
                response += b"The reservation does not exist."
                response += b"\n</body></html>"
            # If exist
            else:
                # Set the response to a 200 OK status with a message
                response =  b"HTTP/1.1 200 OK\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>\n"
                response += json.dumps(theReservation).encode()
                response += b"\n</body></html>"

        else:
            response = b"HTTP/1.1 404 Not Found\n"

    except Exception as e:
        # Set the response to a 400 Bad Request status with a message
        response = b"HTTP/1.1 400 Bad Request\n"
        response += b"Content-Type: text/html\n"
        response += b"\n"
        response += b"<html><body>400 Bad Request</body></html>"

    # Send the response to the client
    connection.sendall(response)
    # Close the connection
    connection.close()

while True:
    # Create a new thread for each incoming request
    thread = threading.Thread(target=request)
    # Start the thread
    thread.start()
    # Wait for the thread to finish
    thread.join()