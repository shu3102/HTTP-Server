from genericpath import isfile
from socket import *
from datetime import datetime, timedelta
import calendar
import os
import mimetypes
import os.path
import time
import re
from wsgiref.handlers import format_date_time
import gzip
from threading import *
import _thread


MAX_URI_LEN = 1000
MAX_PAYLOAD = 10000


def error_responce(status_code, status, msg):
    MsgString = """
    <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
    <html>
    <head>
    <title>{status_code} {status}</title>
    </head>
    <body>
    <h1>Forbidden</h1>
    <h4>{msg}</h4>
    <hr>
    </body>
    </html>
    """
    return MsgString


class form_socket:
    global local_head
    local_head = {}
    global CLIENTS
    CLIENTS = []

    def __init__(self, servern, serverport):
        self.servern = '127.0.0.1'
        self.serverport = 10009

    def connect(self):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind((self.servern, self.serverport))
        sock.listen(5)
        while 1:
            # client,addr=sock.accept()
            #print(addr,"is conneted")
            # req=client.recv(1024)
            # print(req.decode())
            # msg=self.parse_request(req)
            # print(msg.decode())
            # self.sendto(msg,addr)
            client, addr = sock.accept()
            print(addr, "is conneted")
            CLIENTS.append((client, addr))
            req = client.recv(2048)
            print(req.decode())
            req_obj = httprequest(req, client, addr)
            #msg = httprequest.parse_request(req_obj,req)
            # print(msg.decode())
           # self.mysend(msg,client,addr)
            # return msg

    def mysend(response, client, addr):
        for cli in CLIENTS:
            if(cli == (client, addr)):
                try:
                    client.sendto(response, addr)
                    client.close()
                except:
                    client.close()
                    form_socket.remove(client)

    def remove(conn):
        if conn in CLIENTS:
            CLIENTS.remove(conn)
            return


class httprequest:
    global local_head

    def __init__(self, data, client, addr):

        self.method = None
        self.uri = None
        self.version = "1.1"
        self.if_modified_since = None
        self.Range = None
        self.encoding = None
        self.user_agent = None
        self.req_body = None
        self.parse_request(data, client, addr)
        self.accept = None
        self.accept_encoding = None
        print("This is accpet", self.accept)

    def split_by_header(msg):
        reqHeader, reqBody = msg.split("\r\n\r\n")
        return reqHeader, reqBody

    def split_by_line(msg):
        line = msg.split("\r\n")
        return line

    def split_by_space(line):
        word = line.split(" ")
        return word

    def parse_request(self, encoded_req, client, addr):
        global local_head
        local_head = {}
        req = encoded_req.decode()
        # request=req.split("\n")
        # if(len(request)>1):
        # self.req_body=req

        reqHeader, reqBody = httprequest.split_by_header(req)

        line = httprequest.split_by_line(reqHeader)
        self.req_body = reqBody

        for j in range(1, len(line)):
            if("If-Modified-Since" in line[j]):

                t = ""
                line_len = len(line[j])
                flag = 0
                k = 0
                for i in line[j]:
                    k = k+1
                    if(i == ':'):
                        # flag=1
                        f = i
                        m = line[j]
                        he = line[j][:k-1]
                        val = line[j][k+1:]
                        local_head[he] = val
                        break

                continue

            word = line[j].split(":")
            if(len(word) > 1):
                local_head[word[0]] = word[1]
            else:
                local_head[word[0]] = " "
        print("Local header is:", local_head)
        if(local_head == {}):
            text = b"\r\n+Error"
            form_socket.mysend(text, client, addr)
        req_line = httprequest.split_by_space(line[0])
        length = len(req_line)

        if("If-Modified-Since" in local_head):
            print("Prsent=============")
            self.if_modified_since = local_head["If-Modified-Since"]

        if(length > 1):
            self.uri = req_line[1]
            self.method = req_line[0]

        if(length > 2):
            self.version = req_line[2]
        self.user_agent = local_head['User-Agent']
        if("Range" in local_head):
            self.Range = local_head['Range']
        self.encoding = local_head['Accept-Encoding']
        self.accept = self.check_accept(local_head["Accept"])
        self.call_method(local_head, req, client, addr)

    def check_accept(self, req):
        word = req.split(",")
        accept_values = {}
        for i in range(0, len(word)):
            sp = word[i]
            additional = sp.split(";")
            if(len(additional) == 1):
                accept_values[additional[0].strip(" ")] = 1
                # type_content.append(additional[0])
                # value_content.append(1)
            elif(len(additional) > 1):
                # type_content.append(additional[0])
                qvalue = additional[1].split("=")
                # value_content.append(float(qvalue[1]))
                accept_values[additional[0].strip(" ")] = float(qvalue[1])
        print("Type content:", accept_values)
        return accept_values

    def call_method(self, local_head, req, client, addr):

        if("Host" not in local_head):
            response_line = self.make_responseline(400)
            error_msg = response_line+form_socket.add_header(self)
            return error_msg.encode()
        # req_obj=httprequest(request)
        if(self.method == "GET"):
            response_obj = httpresponse()
            GET_response = httpresponse.get_method(
                response_obj, req, self, client, addr)
            # print(GET_response.decode())

            # form_socket.mysend(GET_response,client,addr)
        if(self.method == "PUT"):
            print(
                "################################# CALLING PUT ########################################## ")
            response_obj = httpresponse()
            PUT_responce = httpresponse.put_method(
                response_obj, req, self, client, addr)

            form_socket.mysend(PUT_responce, client, addr)

        if(self.method == "POST"):
            pass


class httpresponse:
    global header
    header = {'Server': 'HTTP server',
              'Content-Type': 'text/html', 'Connection': 'closed'}
    status_code = {200: 'OK',
                   404: 'NOT FOUND',
                   501: 'Not Implemented',
                   400: 'Bad Request',
                   204: 'No Content',
                   201: 'Created',
                   304: 'Not Modified',
                   401: 'Unauthorized',
                   403: 'Forbidden',
                   414: 'Request-URI too long'}

    def convert_to_gmt(self, date):
        dt = str(date).split(" ")
        tosend = ""
        tosend += dt[0]+", "+dt[2]+" "+dt[1]+" "+dt[4]+" "+dt[3]+" "+"GMT"
        return tosend

    def get_method(self, request, req_obj, client, addr):
        file_f = False
        read_p = False
        dir_f = False
        if(req_obj.uri == '/'):
            req_obj.uri = '/index.htm'
        if(req_obj.uri == '/favicon.ico'):
            req_obj.uri = '/favi.txt'
        filen = req_obj.uri.strip("/")
        print(filen)
        if(len(req_obj.uri) > 255):
            self.make_error_response(414, client, addr)
            return
        if(os.path.isdir(filen)):
            dir_f = True

        if (os.path.exists(filen)):
            if(os.path.isfile(filen)):
                file_f = True
                print("file present")
                if(os.access(filen, os.R_OK)):
                    read_p = True
                    print("read permisson")
            print(req_obj.uri)
            accept_val = {}
            accept_val = req_obj.accept
            if(read_p == False):
                self.make_error_response(403, client, addr)
            if(mimetypes.guess_type(filen)[0] not in accept_val):
                pass
            if(file_f == True and read_p == True):
                content_type = mimetypes.guess_type(filen)[0]  # or 'text/html'
                extra_headers = {'Content-Type': content_type}
                response_headers = self.add_header(extra_headers)

                size = os.path.getsize(filen)
                extra_headers = {'Content-length': str(size)}
                header.update(extra_headers)
                #print("content-length is",size)
                response_headers = self.add_header(extra_headers)

                extra_headers = {'Accept-Ranges': 'bytes'}
                header.update(extra_headers)
                response_headers = self.add_header(extra_headers)

                lastmodified = os.path.getmtime(filen)
                print(lastmodified)
                last_mod = format_date_time(lastmodified)
                extra_headers = {'Last-modified': last_mod}
                header.update(extra_headers)
                response_headers = self.add_header(extra_headers)

                format_m = "%a, %d %b %Y %H:%M:%S GMT"
                expires = datetime.utcnow() + timedelta(days=(365))
                expires = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
                extra_headers = {'Expires': expires}
                header.update(extra_headers)
                response_headers = self.add_header(extra_headers)

            # if(req_obj.if_modified_since!=None):

                # if self.header_to_time(req_obj.if_modified_since) >= self.header_to_time(last_mod) : #time.strptime(req_obj.if_modified_since,"%a, %d %b %Y %H:%M:%S GMT"):
            #   print("compared")
            #   print(self.header_to_time(req_obj.if_modified_since) >= self.header_to_time(last_mod))
            #   response_line=self.make_responseline(304)
                #  response_headers =self.add_header()
                # body=b"<h1>304 Not modified</h1>"
            #   blank_line = b"\r\n"
            #   complete_resonse=b"".join([response_line, response_headers.encode(), blank_line])
                #  form_socket.mysend(complete_resonse,client,addr)
                encode_f = False
                gzip_f = False
                if('Accept-Encoding' in local_head):
                    encode_f = True
                    if('gzip' in local_head['Accept-Encoding']):
                        gzip_f = True
                        extra_headers = {'Content-Encoding': 'gzip'}
                        header.update(extra_headers)
                        response_headers = self.add_header(extra_headers)

                print("These are response headers")
                print(response_headers)
                with open(filen, 'rb') as f:
                    body = f.read()
                if(encode_f == True and gzip_f == True):
                    body = gzip.compress(body)
                response_line = self.make_responseline(200)
                blank_line = b"\r\n"

                form_socket.mysend(b"".join(
                    [response_line, response_headers.encode(), blank_line, body]), client, addr)
        else:
            response_headers = self.add_header()
            response_line = self.make_responseline(404)
            body = b"<h1>404 not found</h1>"
            blank_line = b"\r\n"
            return b"".join([response_line, response_headers.encode(), blank_line, body])

        blank_line = b"\r\n"
        response_line = self.make_responseline(200)
        response_headers = self.add_header()
        body = b"hi "
        return b"".join([response_line, response_headers.encode(), blank_line, body])

    def put_method(self, request, req_obj, client, addr):
        try:
            myuri = req_obj.uri
            if("/" in myuri):
                if(len(myuri) < MAX_URI_LEN):
                    #
                    file_name = myuri.strip('/')
                    if(file_name == ""):
                        file_name = "indexput.html"
                    current_dir = os.getcwd()
                    file_path = current_dir + myuri

                    if(len(req_obj.req_body) > 0):
                        print(int(len(req_obj.req_body)))
                        print("printed lenght")
                        if(int(len(req_obj.req_body)) < MAX_PAYLOAD):
                            if(os.path.isfile(file_path)):
                                if(os.access(file_path, os.R_OK) and os.access(file_path, os.W_OK)):
                                    # success
                                    status_code = 200
                                    # appending as of now
                                    with open(file_name, 'a') as fp:
                                        fp.write(req_obj.req_body)
                                        fp.close()
                                    response_headers = self.add_header()
                                    response_line = self.make_responseline(
                                        status_code)
                                    body = b"<h1>200 OK file updated </h1>"
                                    blank_line = b"\r\n"
                                    print(
                                        "###########################################################################")
                                    print(
                                        "".join([response_line, response_headers.encode(), blank_line, body]))
                                    return b"".join([response_line, response_headers.encode(), blank_line, body])
                                else:
                                    # forbidden file
                                    # file understood by server but dont want to write
                                    status_code = 403
                                    response_headers = self.add_header()
                                    response_line = self.make_responseline(
                                        status_code)
                                    body = b"<h1>403 Forbidden file </h1>"
                                    blank_line = b"\r\n"
                                    return b"".join([response_line, response_headers.encode(), blank_line, body])
                            else:
                                # create new file
                                status_code = 201
                                with open(file_name, 'w') as fp:
                                    fp.write(req_obj.req_body)
                                    fp.close()
                                response_headers = self.add_header()
                                response_line = self.make_responseline(
                                    status_code)
                                body = b"<h1>201 OK New file created </h1>"
                                blank_line = b"\r\n"
                                return b"".join([response_line, response_headers.encode(), blank_line, body])

                        else:
                            # max Payload
                            status_code = 413
                            response_headers = self.add_header()
                            response_line = self.make_responseline(status_code)
                            body = b"<h1>413 Max Payload file </h1>"
                            blank_line = b"\r\n"
                            return b"".join([response_line, response_headers.encode(), blank_line, body])

                    else:
                        # length required
                        status_code = 411
                        response_headers = self.add_header()
                        response_line = self.make_responseline(status_code)
                        body = b"<h1>403 Forbidden file </h1>"
                        blank_line = b"\r\n"
                        return b"".join([response_line, response_headers.encode(), blank_line, body])
                        #file_name = "411_error.html"

                else:
                    # larger length
                    # 414 Error
                    status_code = 414
                    response_headers = self.add_header()
                    response_line = self.make_responseline(status_code)
                    body = b"<h1>414 Error file </h1>"
                    blank_line = b"\r\n"
                    return b"".join([response_line, response_headers.encode(), blank_line, body])

        except:
            # BAD Request
            status_code = 400
            response_headers = self.add_header()
            response_line = self.make_responseline(status_code)
            body = b"<h1>400 Bad Request file </h1>"
            blank_line = b"\r\n"
            return b"".join([response_line, response_headers.encode(), blank_line, body])

    def make_responseline(self, status_c):
        code = self.status_code[status_c]
        resp = "HTTP/1.1 "+str(status_c)+" "+str(code)+"\r\n"
        return resp.encode()

    def time_to_header(self, time_now):
        gmtdate = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time_now)
        return gmtdate+"\r\n"

    def header_to_time(self, date_h):

        time_struct = time.strptime(date_h, "%a, %d %b %Y %H:%M:%S GMT")
        return time_struct

    def make_error_response(self, status_c, client, addr):
        if(status_c == 404):
            response_line = self.make_responseline(status_c)
            response_line = response_line.decode()
            body = "<h1>404 Not found</h1>"

        elif(status_c == 501):
            response_line = self.make_responseline(status_c)
            response_line = response_line.decode()
            body = "<h1>Method not implemented</h1>"
        elif(status_c == 400):
            response_line = self.make_responseline(status_c)
            response_line = response_line.decode()
            body = "<h1>Bad Request: Request not understood</h1>"
        elif(status_c == 204):
            response_line = self.make_responseline(status_c)
            response_line = response_line.decode()
        elif(status_c == 201):
            response_line = self.make_responseline(status_c)
            response_line = response_line.decode()
            # response_line=response_line+location  location header to be added
            body = "<h1>New resource created</h1>"
        elif(status_c == 501):
            response_line = self.make_responseline(status_c)
            response_line = response_line.decode()
            body = "<h1>Method not implemented</h1>"
        elif(status_c == 304):
            response_line = self.make_responseline(status_c)
            response_line = response_line.decode()
        elif(status_c == 401):
            response_line = self.make_responseline(status_c)
            response_line = response_line.decode()
            body = "<h1>Unauthrized</h1>"
        elif(status_c == 403):
            response_line = self.make_responseline(status_c)
            response_line = response_line.decode()
            body = "<h1>Forbidden</h1>"
        elif(status_c == 414):
            response_line = self.make_responseline(status_c)
            response_line = response_line.decode()
            body = "<h1>Request URI too long</h1>"
        headers = self.add_header()
        response = response_line+"\r\n"+body
        form_socket.mysend(response, client, addr)
        return

    def add_header(self, extra_headers=None):
        global header
        header_copy = header.copy()  # make a local copy of headers

        if extra_headers:

            header_copy.update(extra_headers)

        head = ""
        head += "Date:"+self.time_to_header(time.localtime())
        for i in header_copy:
            head += str(i)+":"+str(header_copy[i])+"\r\n"
        return head

    def form_response(self, req):
        response_line = self.make_responseline(200)
        res = self.add_header()
        blank = "\r\n"
        body = "Welcome to http"
        x = "".join([response_line.decode(), res.decode(), blank, body])
        print(x)
        return x.encode()


if __name__ == '__main__':
    p = form_socket('127.0.0.1', 10001)
    p.connect()
    input_thread = Thread(target=p.connect)
    input_thread.start()
