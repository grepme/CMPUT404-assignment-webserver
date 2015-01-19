# coding: utf-8
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# Copyright 2014, Modified by: Kyle Richelhoff
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

import SocketServer

# For chroot and paths
import os

# Lazy man's way of importing all our exceptions
from httpexceptions import *

# Match cases
import re


class MyWebServer(SocketServer.BaseRequestHandler):
    
    def handle(self):

        try:
            # headers is a dictionary lookup object for coupling data.
            headers = {}

            # Serving files from and ONLY from
            www_root = "www/"

            self.data = self.request.recv(1024).strip()
            print ("Got a request of:\n %s\n" % self.data)

            # This will split the headers by line
            headers_split = self.data.split('\n')

            # This is to index each request with it's data into a dictionary object
            # ie. Connection: keep-alive
            # In no way is this meant to be optimal, only ease of access.
            for header in headers_split:

                # Split off the first space in the line.
                # We use the first space instead of ": " because of type of requests
                # ie. GET / HTTP/1.1
                headers[header[:header.index(" ")]] = header[header.index(" ") + 1:]

            # Now that the headers are indexed,
            # let's look for a GET request, as this is all we should be handling.
            # We could handle other requests later, but this is not part of the requirements.
            if "GET" not in headers:
                print("Invalid Request")
                raise HTTPForbiddenError(self.request, "Request not valid.")

            else:
                file_name = headers["GET"][:headers["GET"].index(" ")]

            # Seriously, path traversal is a bitch.
            if "../" in file_name:
                raise HTTPNotFound(self.request, "Not Found.")

            # realpath is used to keep the path relative. I'd prefer chroot though, but no root access :(
            path = os.path.realpath(www_root + file_name)

            # If it is a directory, send the HTML index if one exists
            if os.path.isdir(path):
                path = os.path.normpath(path + "/" + "index.html")

            file_type = self.find_file(path)

            self.request.sendall("HTTP/1.1 200 OK\r\n")
            self.request.sendall("Content-Type: {0}; charset=utf-8\r\n".format(file_type))

            # End Headers
            self.request.sendall("\r\n")

            # Send the file over the TCP connection
            # We should probably cache this at some point...
            static_content = open(path)
            self.request.sendall(static_content.read())
            static_content.close()

        #We can intercept any valid HTTPError
        except HTTPError as e:
            # All HTTPErrors have a finish definition to tell off the client for being naughty.
            e.finish()

        # Broad catch-all statement for those pesky errors we don't catch.
        # Just because we don't expect them, doesn't mean we shouldn't handle them.
        except Exception as e:
            print e
            self.request.sendall("An unknown error occurred during your request, please try again.")

    def find_file(self, path):
        if os.path.isfile(path):
            # If it is a file, send the file contents
            file_type = os.path.splitext(path)[1]
            if file_type == ".html" or file_type == ".htm":
                return "text/html"
            elif file_type == ".css":
                return "text/css"
            else:
                # For the purpose of this httpd, we are only defining HTML and CSS mime-types.
                # However, I will define here an any type so that we always match.
                return "*/*"

        else:
            # No file or directory found
            raise HTTPNotFound(self.request, "Not Found.")

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
