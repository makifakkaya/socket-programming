# ROOM SERVER
# The server listens on localhost on port 8081

import threading
import socket
import json

# Create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 8081)
sock.bind(server_address)

# Start listening on the socket
sock.listen(1)
print("server start")

# This function is called when a new connection is accepted by the server
def request():
    try:
        # Accept a new connection
        connection, client_address = sock.accept()

        # Receive data from the connection
        data = connection.recv(1024)

        # Split the received data by newline character to get the request line
        request_line = data.split(b"\n")[0]

        # Split the request line to get the request type, request URI, and HTTP version
        request_type, request_uri, http_version = request_line.split(b" ")

        # Split the request URI to get the path and query string
        if b"?" in request_uri:
            request_path, request_params = request_uri.split(b"?", 1)
        else:
            request_path = request_uri
            request_params = b""

        # Create an empty dictionary to store the query string parameters
        params = {}

        # If there is a query string, split it by '&' to get the individual parameters
        if request_params:
            for param in request_params.split(b"&"):
                key, value = param.split(b"=")
                params[key] = value

        # /add
        if request_path == b"/add":

            # Open the 'room.json' file in read mode
            with open("room.json", "r") as f:
                json_data = f.read() # Read the contents of the file

            # Load the JSON data from the file
            data = json.loads(json_data)

            doesExist = 0 # room exists or not

            # Iterate over the rooms in the data
            for room in data['rooms']:
                # If the room already exists in the data
                if room['name'] == params[b"name"].decode():
                    # Set the 'doesExist' flag to True
                    doesExist = 1

            # If the room already exists in the data
            if doesExist == 1:
                # Set the response to a 403 Forbidden error
                response =  b"HTTP/1.1 403 Forbidden\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>The room already exists in the database.</body></html>"

            # If the room does not exist in the data
            else:
                # Add the new room to the data
                data['rooms'].append({"name": params[b"name"].decode(), "reserve": []})
                json_data = json.dumps(data)
                with open('room.json', 'w') as f:
                    f.write(json_data)

                # Set the response to a 200 OK status with a message that the room was added to the database
                response =  b"HTTP/1.1 200 OK\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>The room has been added to the database.</body></html>"

        # If the request path is '/remove'
        elif request_path == b"/remove":

            # Read 'room.json'
            with open("room.json", "r") as f:
                json_data = f.read()

            data = json.loads(json_data)

            index = -1
            indexCounter = -1

            # Iterate over the rooms in the data
            for room in data['rooms']:
                indexCounter = indexCounter + 1
                if room['name'] == params[b"name"].decode():
                    index = indexCounter

            # If the room to be removed was not found
            if index == -1:
                # Set the response to a 403 Forbidden error
                response =  b"HTTP/1.1 403 Forbidden\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>The room does not exist in the database.</body></html>"

            # If the room to be removed was found
            else:
                # Iterate over the rooms in the data
                for elem in data['rooms']:
                    if elem['name'] == params[b"name"].decode():
                        # Remove the element from the list
                        data['rooms'].remove(elem)
                        break
                    
                # Open the 'room.json' file to write new data.
                json_data = json.dumps(data)
                with open('room.json', 'w') as f:
                    f.write(json_data)

                # Set the response to a 200 OK status with a message that the room was removed from the database
                response =  b"HTTP/1.1 200 OK\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>The room has been removed from the database.</body></html>"


        # If the request path is '/reserve'
        elif request_path == b"/reserve":
            
            # Open the 'room.json' to read
            with open("room.json", "r") as f:
                json_data = f.read()
            data = json.loads(json_data) # Load the JSON data from the file

            isAllow = 0
            doesExist = 0
            indexCounter = -1
            outOfBound = 0

            # Iterate over the rooms in the data
            for room in data['rooms']:
                indexCounter = indexCounter + 1
                # If the room to be reserved is found
                if room['name'] == params[b'name'].decode():
                    index = indexCounter
                    doesExist = 1 
                    isAllow = 1 # Will be changed if exists
                    for reserve in room['reserve']:
                        # If days are equal
                        if reserve['day'] == int(params[b'day'].decode()):
                            # If the clocks collide
                            for i in range(int(params[b'duration'].decode())):
                                if reserve['hour'] == int(params[b'hour'].decode()) + i:
                                    isAllow = 0 # Set allow as false

            # Check if the times are within bounds (9-17)
            for i in range(int(params[b'duration'].decode())):
                if int(params[b'hour'].decode()) + i not in [9, 10, 11, 12, 13, 14, 15, 16, 17]:
                    outOfBound = 1

            # Check if the day are within bounds (1-7)
            if int(params[b'day'].decode()) not in [1, 2, 3, 4, 5, 6, 7] or int(params[b'hour'].decode()) not in [9, 10, 11, 12, 13, 14, 15, 16, 17] :
                # Set the response to a 400 Bad Requests error
                response =  b"HTTP/1.1 400 Bad Request\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>Invalid day or hour value.</body></html>"

            # Check if the times are within bounds (9-17)
            elif outOfBound == 1:
                # Set the response to a 400 Bad Requests error
                response =  b"HTTP/1.1 400 Bad Request\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>You can reserve between 09.00 and 18.00 hours.</body></html>"
            
            # If allow
            elif isAllow == 1:
                
                # Fill all hours
                for i in range(int(params[b'duration'].decode())):
                    data['rooms'][index]['reserve'].append({"day": int(params[b'day'].decode()), "hour": int(params[b'hour'].decode()) + i})

                # Write back
                json_data = json.dumps(data)
                with open('room.json', 'w') as f:
                    f.write(json_data)
                response =  b"HTTP/1.1 200 OK\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>The room has been reserved.</body></html>"

            elif doesExist == 1 and isAllow == 0:
                response =  b"HTTP/1.1 403 Forbidden\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>The room is already reserved.</body></html>"

            elif doesExist == 0:
                response =  b"HTTP/1.1 403 Forbidden\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>The room does not exist.</body></html>"

        # Check if the request path is '/checkavailability'
        elif request_path == b"/checkavailability":
            # Open the 'room.json' file in read mode
            with open("room.json", "r") as f:
                json_data = f.read()
            
            # Load the JSON data from the file
            data = json.loads(json_data)

            # Create a list to store the busy hours
            busyHours = []

            # Create a list to store the available hours
            availabkeHours = []


            isAllow = 0
            doesExist = 0
            indexCounter = -1
            outOfBound = 0

            # Iterate over the rooms in the data
            for room in data['rooms']:
                indexCounter = indexCounter + 1
                # If the room to be checked is found
                if room['name'] == params[b'name'].decode():
                    index = indexCounter
                    doesExist = 1
                    isAllow = 1
                    # Iterate over the reserved time slots for the room
                    for reserve in room['reserve']:
                        # If the day to be checked matches the reserved day
                        if reserve['day'] == int(params[b'day'].decode()):
                            # Add the reserved hour to the busy hours list
                            busyHours.append(reserve['hour'])

            # If the day to be checked is not a valid day (1-7)
            if int(params[b'day'].decode()) not in [1, 2, 3, 4, 5, 6, 7]:
                # Set the response to a 400 Bad Request error
                response =  b"HTTP/1.1 400 Bad Request\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>Invalid day or hour value.</body></html>"
            # If the room to be checked was not found
            elif doesExist == 0:
                # Set the response to a 404 Not Found error
                response =  b"HTTP/1.1 404 Not Found\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>The room does not exist.</body></html>"
            else:
                for i in range(9, 18):
                    # If the hour is not in the busy hours list
                    if i not in busyHours:
                        # Add the hour to the available hours list
                        availabkeHours.append(i)

                # Set the response to a 200 OK status with the day and available hours for the room
                response =  b"HTTP/1.1 200 OK\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>"
                response += b"\nDay: " + params[b'day'] + b"  -  Available hours: " + (b" - ".join(str(element).encode() for element in availabkeHours)+b"<br>")
                response += b"\n</body></html>"
        # If the request path is not recognized
        else:
            # Set the response to a 404 Not Found error
            response = b"HTTP/1.1 404 Not Found\n"
    # If an exception occurs
    except Exception as e:
        # Set the response to a 400 Bad Request error
        response = b"HTTP/1.1 400 Bad Request\n"
        response += b"Content-Type: text/html\n"
        response += b"\n"
        response += b"<html><body>400 Bad Request</body></html>"

    # Send the response to the client
    connection.sendall(response)
    # Close the connection to the client
    connection.close()

while True:
    # Create a new thread for each incoming request
    thread = threading.Thread(target=request)
    # Start the thread
    thread.start()
    # Wait for the thread to finish
    thread.join()