import socket
import json
import threading

# Create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to localhost on port 8082
server_address = ('localhost', 8082)
sock.bind(server_address)

# Start listening for incoming connections
sock.listen(1)
print("activity server start")

# Function to handle requests
def request():
    try:
        # Accept the incoming connection
        connection, client_address = sock.accept()

        # Receive the data from the client
        data = connection.recv(1024)

        # Split the request line into its individual parts
        request_line = data.split(b"\n")[0]
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

        # If the request path is '/add'
        if request_path == b"/add":
            # Open the 'activity.json' file in read mode
            with open("activity.json", "r") as f:
                # Read the contents of the file
                json_data = f.read()

            # Load the contents of the file as a JSON object
            data = json.loads(json_data)

            # Set a flag to indicate if the activity already exists in the database
            doesExist = 0

            # Iterate over the list of activities in the database
            for room in data['activities']:
                if room['name'] == params[b"name"].decode():
                    # Set the flag to indicate that the activity already exists
                    doesExist = 1

            # If the activity already exists
            if doesExist == 1:
                # Set the response to a 403 Forbidden status with a message
                response =  b"HTTP/1.1 403 Forbidden\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>The activity already exists in the database.</body></html>"
            # If the activity does not already exist
            else:
                # Add the activity to the database
                data['activities'].append({"name": params[b"name"].decode()})

                # Write the updated JSON data to the file
                json_data = json.dumps(data)
                with open('activity.json', 'w') as f:
                    f.write(json_data)

                # Set the response to a 200 OK status with a message
                response =  b"HTTP/1.1 200 OK\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>The activity has been added to the database.</body></html>"

        # If the request path is '/remove'
        elif request_path == b"/remove":

            # Read the contents of 'activity.json'.
            with open("activity.json", "r") as f:
                json_data = f.read()

            data = json.loads(json_data)
            index = -1
            indexCounter = -1
            # Iterate over the list of activities in the database
            for room in data['activities']:
                indexCounter = indexCounter + 1

                # If the name of the current activity matches the name in the request
                if room['name'] == params[b"name"].decode():
                    # Set the index to the current counter value
                    index = indexCounter

            # If the activity was not found in the database
            if index == -1:
                # Set the response to a 403 Forbidden status with a message
                response =  b"HTTP/1.1 403 Forbidden\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>The activity does not exist in the database.</body></html>"
            # If the activity was found in the database
            else:
                # Remove the activity from the list
                for elem in data['activities']:
                    if elem['name'] == params[b"name"].decode():
                        # Remove the element from the list
                        data['activities'].remove(elem)
                        break
                # Dump the updated list of activities as JSON data
                json_data = json.dumps(data)
                # Open the 'activity.json' file to write
                with open('activity.json', 'w') as f:
                    f.write(json_data)

                # Set the response to a 200 OK status with a message
                response =  b"HTTP/1.1 200 OK\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>The activity has been removed from the database.</body></html>"

        # If the request path is '/check'
        elif request_path == b"/check":

            # Open the 'activity.json' file to read
            with open("activity.json", "r") as f:
                json_data = f.read()

            # Load the contents of the file as a JSON object
            data = json.loads(json_data)
            index = -1
            indexCounter = -1
            # Iterate over the list of activities in the database
            for room in data['activities']:
                indexCounter = indexCounter + 1
                # If the name of the current activity matches the name in the request
                if room['name'] == params[b"name"].decode():
                    # Set the index to the current counter value
                    index = indexCounter
            
            # If the activity was not found in the database
            if index == -1:
                # Set the response to a 404 Not Found status with a message
                response =  b"HTTP/1.1 404 Not Found\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>The activity does not exist in the database.</body></html>"
            # If the activity was found in the database
            else:
                # Set the response to a 200 OK status with a message indicating that the activity exists
                response =  b"HTTP/1.1 200 OK\n"
                response += b"Content-Type: text/html\n"
                response += b"\n"
                response += b"<html><body>The activity exists in the database.</body></html>"

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