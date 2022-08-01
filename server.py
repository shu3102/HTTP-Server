from genericpath import isfile
from socket import *
from datetime import datetime, timedelta
import calendar
import os
import sys
import mimetypes
import os.path
import threading
import time
import re
from wsgiref.handlers import format_date_time
import gzip
from threading import *
import _thread
import json
import string
import random
import shutil
from configparser import ConfigParser


config = ConfigParser()

config.read('server_config.ini')
global cookie_id
MAX_URI_LEN = config['http_server']['max_urllen']
port_no = config['http_server']['port_no']
MAX_PAYLOAD = config['http_server']['max_payload']
cookie_id = config['http_server']['cookie_id']
#print("COOOKie id", cookie_id)
#print(type(cookie_id))


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


CLIENTS = []


class form_socket:
    global local_head
    local_head = {}
    global CLIENTS

    def __init__(self, servern, serverport):
        self.servern = servern
        self.serverport = serverport

    def connect(self):

        while 1:
            try:
                client, addr = sock.accept()
                print(addr, "is conneted")
                CLIENTS.append((client, addr))
                _thread.start_new_thread(self.recieve_data, (client, addr))
                #req = client.recv(8192)
                #f = open("p1.txt", "w")
                #f.write(req.decode(encoding="utf8", errors='ignore'))
                # f.close()
                #req_obj = httprequest(req, client, addr)
            except:
                print("Error")
                break

    def recieve_data(self, client, addr):
        req = client.recv(8192)
        f = open("p1.txt", "w")
        f.write(req.decode(encoding="utf8", errors='ignore'))
        f.close()
        req_obj = httprequest(req, client, addr)

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
        self.cookie = None
        self.method = None
        self.uri = None
        self.version = "1.1"
        self.if_modified_since = None
        self.Range = None
        self.encoding = None
        self.user_agent = None
        self.req_body = None
        self.containt_type = None
        self.containt_length = None
        self.parse_request(data, client, addr)
        self.accept = None
        self.accept_encoding = None
        # print("This is accpet", self.accept)

    def split_by_header(msg):
        try:
            reqHeader, reqBody = msg.split("\r\n\r\n")
        except:
            splitArray = msg.split("\r\n\r\n")
            reqHeader = splitArray[0]
            reqBody = ""
            for i in range(1, len(splitArray)):
                reqBody += str(splitArray[i])
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
        req = encoded_req.decode(encoding="utf8", errors='ignore')
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
        #print("Local header is:", local_head)
        if(local_head == {}):
            response_obj = httpresponse()
            text = b"\r\n+Error"
            response_line = self.make_responseline(400)
            response_headers = self.add_header()
            blank_line = b"\r\n"
            body = b"Error"
            form_socket.mysend(b"".join(
                [response_line, response_headers.encode(), blank_line, body]), client, addr)
            return
        req_line = httprequest.split_by_space(line[0])
        length = len(req_line)
        if("If-Modified-Since" in local_head):
            #print("Prsent=============")
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
        if("Content-Type" in local_head):
            self.containt_type = local_head['Content-Type']
        if("Content-Length" in local_head):
            self.containt_length = local_head["Content-Length"]
        if("Accept-Encoding" in local_head):
            self.encoding = local_head['Accept-Encoding']
        if("Accept" in local_head):
            self.accept = local_head["Accept"]

        if("Cookie" in local_head):
            #print("happy")
            self.cookie = local_head['Cookie']
        #self.accept = self.check_accept(local_head["Accept"])
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
            res_obj = httpresponse()
            res_obj.make_error_response(400, client, addr)
        # req_obj=httprequest(request)
        if(self.method == "GET"):
            response_obj = httpresponse()
            GET_response = httpresponse.get_method(
                response_obj, req, self, client, addr, head=False)
            if(GET_response != None):
                print(GET_response.decode())
            # form_socket.mysend(GET_response,client,addr)

            # form_socket.mysend(GET_response,client,addr)
        if(self.method == "PUT"):
            response_obj = httpresponse()
            PUT_responce = httpresponse.put_method(
                response_obj, req, self, client, addr)
            #form_socket.mysend(PUT_responce, client, addr)

        if(self.method == "POST"):
        
            response_obj = httpresponse()
            POST_responce = httpresponse.post_method(
                response_obj, req, self, client, addr)

            form_socket.mysend(POST_responce, client, addr)

        if(self.method == "DELETE"):
            response_obj = httpresponse()
            httpresponse.delete_method(response_obj, req, self, client, addr)
        if(self.method == "HEAD"):
            response_obj = httpresponse()
            httpresponse.get_method(
                response_obj, req, self, client, addr, head=True)


class httpresponse:
    global header
    header = {'Server': 'HTTP server',
              'Content-Type': 'text/html', 'Connection': 'closed'}
    status_code = {200: 'OK',
                   202: 'Accepted',
                   404: 'NOT FOUND',
                   501: 'Not Implemented',
                   505: 'HTTP Version Not Supported',
                   400: 'Bad Request',
                   204: 'No Content',
                   201: 'Created',
                   304: 'Not Modified',
                   401: 'Unauthorized',
                   403: 'Forbidden',
                   414: 'Request-URI too long',
                   415: 'Unsupported Media Type'}

    def convert_to_gmt(self, date):
        dt = str(date).split(" ")
        tosend = ""
        tosend += dt[0]+", "+dt[2]+" "+dt[1]+" "+dt[4]+" "+dt[3]+" "+"GMT"
        return tosend

    def get_method(self, request, req_obj, client, addr, head):
        get_header = {'Server': 'HTTP server',
                      'Content-Type': 'text/html', 'Connection': 'Closed'}
        log_status = None
        file_f = False
        read_p = False
        dir_f = False
        if(req_obj.uri == '/'):
            req_obj.uri = '/index.html'
        if(req_obj.uri == '/favicon.ico'):
            req_obj.uri = '/myimage.jpg'
        filen = req_obj.uri.strip("/")
        #print("filen is", filen)

        if(len(req_obj.uri) > 255):
            log_status = 414
            self.make_error_response(414, client, addr, req_obj)
            return

        if(os.path.isdir(filen)):
            dir_f = True
            file_list = os.listdir(filen)
            m = ""
            dir_size = 0
            for f in file_list:
                m = m+str(f)+"<br>"
                # dir_size+=os.path.getsize("/"+f)
            dir_size = 0
            for ele in os.scandir(filen):
                dir_size += os.path.getsize(ele)
            #print("dir size", dir_size)
            response_headers = self.add_header()
            #print("These are directory headres;", response_headers)
            dir_body = f"<html><title>Directory content</title><h1>Directory content</h1><h2>{m}</h2></html>"
            response_line = self.make_responseline(200)
            blank_line = b"\r\n"
            form_socket.mysend(b"".join([response_line, response_headers.encode(
            ), blank_line, dir_body.encode()]), client, addr)
            f = open("Access.log", "a+")
            log_status = 200
            f.write(
                f"{addr[0]} -- {time.ctime()}  {req_obj.method}  {req_obj.uri}  {req_obj.version}  {log_status}  {dir_size} {req_obj.user_agent}\n")
            f.close()
            return

        if(not os.path.exists(filen)):
            #print("Not exists")
            self.make_error_response(404, client, addr, req_obj)
            return
        if (os.path.exists(filen)):
            if(os.path.isfile(filen)):
                file_f = True
                #print("file present")
                if(os.access(filen, os.R_OK)):
                    read_p = True
                    #print("read permisson")

            if(read_p == False):
                log_status = 403
                self.make_error_response(403, client, addr, req_obj)
            # if(mimetypes.guess_type(filen)[0] not in accept_val):
               # pass
        if(file_f == True and read_p == True):
            content_type = mimetypes.guess_type(filen)[0]  # or 'text/html'
            extra_headers = {'Content-Type': content_type}
            get_header.update(extra_headers)
            response_headers = self.add_header(extra_headers)

            size = os.path.getsize(filen)
            extra_headers = {'Content-length': str(size)}
            get_header.update(extra_headers)
            #print("content-length is",size)
            response_headers = self.add_header(extra_headers)

            extra_headers = {'Accept-Ranges': 'bytes'}
            get_header.update(extra_headers)
            response_headers = self.add_header(extra_headers)

            lastmodified = os.path.getmtime(filen)
            #print(lastmodified)
            last_mod = format_date_time(lastmodified)
            extra_headers = {'Last-modified': last_mod}
            get_header.update(extra_headers)
            response_headers = self.add_header(extra_headers)

            format_m = "%a, %d %b %Y %H:%M:%S GMT"
            expires = datetime.utcnow() + timedelta(days=(365))
            expires = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
            extra_headers = {'Expires': expires}
            get_header.update(extra_headers)
            response_headers = self.add_header(extra_headers)

            if req_obj.cookie == None:
                #print("ckiie")
                expire = datetime.utcnow() + timedelta(days=(1))
                expire = expire.strftime("%a, %d %b %Y %H:%M:%S GMT")
                cookie_id = config['http_server']['cookie_id']
                c = "id="+str(cookie_id)+';'+'Expires='+expire+';'
                extra_headers = {'Set-Cookie': c}
                get_header.update(extra_headers)
                response_headers = self.add_header(extra_headers)
                with open('server_cook.log', 'a+') as f:
                    towrite = "".join(('\n', "IP ADDRESS=", str(
                        addr), "|", "COOKIE ID=", cookie_id))
                    f.write(towrite)
                    f.close()
                s = int(cookie_id)
                s = s+1
                config['http_server']['cookie_id'] = str(s)
                with open('server_config.ini', 'w') as file:
                    config.write(file)
                    file.close()

            if(req_obj.if_modified_since != None):

                # time.strptime(req_obj.if_modified_since,"%a, %d %b %Y %H:%M:%S GMT"):
                if self.header_to_time(req_obj.if_modified_since) >= self.header_to_time(last_mod):
                 
                    log_status = 304
                    self.make_error_response(304, client, addr, req_obj)
                    return
              
            encode_f = False
            gzip_f = False
            if('Accept-Encoding' in local_head):
                encode_f = True
                if('gzip' in local_head['Accept-Encoding']):
                    gzip_f = True
                    extra_headers = {'Content-Encoding': 'gzip'}
                    get_header.update(extra_headers)
                    response_headers = self.add_header(extra_headers)
            gethead = ""
            gethead += "Date:"+self.time_to_header(time.localtime())
            for i in get_header:
                gethead += str(i)+": "+str(get_header[i])+"\r\n"

            with open(filen, 'rb') as f:
                body = f.read()

            if(encode_f == True and gzip_f == True):
                body = gzip.compress(body)
            log_status = 200
            response_line = self.make_responseline(200)

            blank_line = b"\r\n"

            if(head == False):

                with open('Access.log', "a+") as fd:
                    # rline=response_line.decode().split('\r\n')
                    fd.write(
                        f"{addr[0]} -- {time.ctime()}  {req_obj.method}  {req_obj.uri}  {req_obj.version}  {log_status}  {size} {req_obj.user_agent}\n")
                   
                fd.close()

                form_socket.mysend(
                    b"".join([response_line, gethead.encode(), blank_line, body]), client, addr)
                return
            elif(head == True):

                with open('Access.log', "a+") as fd:
                    #fd.write(f"{time.ctime()} - {addr} - {req_obj.uri} - {req_obj.method} - {response_line} - {log_status}\n")
                    fd.write(
                        f"{addr[0]} -- {time.ctime()}  {req_obj.method}  {req_obj.uri}  {req_obj.version}  {log_status}  0 {req_obj.user_agent}\n")
                fd.close()
                form_socket.mysend(
                    b"".join([response_line, response_headers.encode(), blank_line]), client, addr)

                return
        else:
            self.make_error_response(404, client, addr, req_obj)
            return

        self.make_error_response(400, client, addr, req_obj)

    def put_method(self, request, req_obj, client, addr):
        try:
            myuri = req_obj.uri
            if("/" in myuri):
                if(len(myuri) < MAX_URI_LEN):
                    
                    file_name = myuri.strip('/')
                    if(file_name == ""):
                        file_name = "indexput.html"
                    current_dir = os.getcwd()
                    file_path = current_dir + myuri

                    if(len(req_obj.req_body) > 0):
                        if(int(len(req_obj.req_body)) < MAX_PAYLOAD):
                            if(os.path.isfile(file_path)):
                                if(os.access(file_path, os.R_OK) and os.access(file_path, os.W_OK)):
                                    # success
                                    status_code = 200
                                    # appending as of now
                                    with open(file_name, 'a') as fp:
                                        fp.write(req_obj.req_body)
                                        fp.close()
                                    self.make_error_response(
                                        status_code, client, addr, req_obj)
                                    return
                                else:
                                    # forbidden file
                                    # file understood by server but dont want to write
                                    status_code = 403
                                    self.make_error_response(
                                        status_code, client, addr, req_obj)
                                    return
                            else:
                                # create new file
                                status_code = 201
                                with open(file_name, 'w') as fp:
                                    fp.write(req_obj.req_body)
                                    fp.close()
                                self.make_error_response(
                                    status_code, client, addr, req_obj)
                                return

                        else:
                            # max Payload
                            status_code = 413
                            self.make_error_response(
                                status_code, client, addr, req_obj)
                            return

                    else:
                        # length required
                        status_code = 411
                        self.make_error_response(
                            status_code, client, addr, req_obj)
                        return

                else:
                    # larger length
                    # 414 Error
                    status_code = 414
                    self.make_error_response(
                        status_code, client, addr, req_obj)
                    return

        except:
            # BAD Request
            status_code = 400
            self.make_error_response(status_code, client, addr, req_obj)
            return

    def post_method(self, request, req_obj, client, addr):
        # print(req_obj)
        # print(request)

        containt_type = (req_obj.containt_type).strip(" ")
        containt_type.strip(" ")
        #print("PRINTING CONTAINT TYPE ")
        #print(containt_type)
        body = req_obj.req_body
        #print("Data is ____________")
        # print(body)
        #print(req_obj.uri)
        if(str(containt_type) == "application/x-www-form-urlencoded"):
            #print("inside application/x/www-form-urlencoded")
            file_name = "Master/post" + \
                str(req_obj.uri).strip("/") + str(1) + ".json"
            respnceGot = self.post_encoded(body)
            #print(file_name)
            filePath = file_name
            #print(filePath)

            if(os.path.exists(filePath)):
                status_code = 200

            elif(not(os.path.exists(filePath))):
                status_code = 201
                # create file

            f = open(filePath, 'w')
            f.write(str(respnceGot))
            f.close()

            self.make_error_response(status_code, client, addr, req_obj)
            return

        elif(containt_type == "multipart/form-data"):
            #print("********************************************8")
            post_uri = req_obj.uri
            if(str(post_uri) != "/"):
                post_uri = str(post_uri).strip("/")
                f = open(post_uri, 'w')
                f.write(body)
                f.close()

                self.make_error_response(201, client, addr, req_obj)
                return

            filePath = "post1.txt"
            status_code = 201
            # create file
            #print(type(body))
            new_body = body.split("\r\n")
            #print(len(new_body))
            # print(new_body)
            #print(len(body))
            # print(body)
            entity_data = ""
            isbinary = False
            for i in range(1, len(new_body)):
                try:
                    entity_data += new_body[i]
                except:
                    # pass
                    body[i] = new_body[i].decode("ISO-8859-1")
                    entity_data += new_body[i]
                    isbinary = True

            if(isbinary):
                print("This is binary file")
            data = []
            
            split_char = entity_data.split(':')[0]
            
            new_message = entity_data.split(split_char + ':')
            
            new_message.pop(0)
            
            for z in range(0, len(new_message)):
                new_message[z] = new_message[z].lstrip(' name=')
       
            if_file_exist = 0
            count = 0
            for i in new_message:
                if 'filename' in i:
                    if_file_exist = 1
                    filedata = i
                    # print(i)
                    if('png' in i):
                        content_type = "Content-Type: image/png"
                    elif('jpg' in i):
                        content_type = "Content-Type: image/jpg"
                    elif('jpeg' in i):
                        content_type = "Content-Type: image/jpeg"
                    elif('gif' in i):
                        content_type = "Content-Type: image/gif"
                    else:
                        content_type = ""
                    break
                data.append(i)
                count += 1

            

            # if file exist write data into file:
            if(if_file_exist == 1):
                
                filename = filedata.split("filename=")
                
                if(len(filename) >= 2):
                    fname = filename[1].split("\r\n")[0].strip('"')
                    # error handling required
                    if(isbinary):
                        temp = filename[1].split("\r\n")
                        fdata = ""
                       
                        for i in range(1, len(temp)):
                            fdata += temp[i]
                            if(i == 1):
                                fdata += "\r\n"
                        fdata = fdata[len(content_type):]
                    else:
                        fdata = filename[1].split("\r\n")[1]

                    # remove_string = "Content-Type" +
                    # if file already exit.. appending random string to it, might change to uuid, anyways need to append the file
                    if(os.path.isfile(fname)):
                        letters = string.ascii_lowercase
                        result_str = ''.join(random.choice(letters)
                                             for i in range(5))
                        fname = result_str+fname
                    fname = fname
                    if(isbinary):
                        fwrite = open(fname, "wb")
                        fwrite.write(fdata.encode("ISO-8859-1"))
                        fwrite.close()
                    else:
                        fwrite = open(fname, "w")
                        fwrite.write(fdata)
                        fwrite.close()
                else:
                    pass
                data.append(new_message[count].split(
                    ' filename=')[0] + "filename=" + fname)
            # return data

            f = open(filePath, 'w')
            f.write(str(data))
            f.close()

            self.make_error_response(status_code, client, addr, req_obj)
            return

        else:
            self.make_error_response(415, client, addr, req_obj)
            return

    def post_encoded(self, data_post):
        data = data_post.split("&")
        body_parameter = {}
        for i in data:
            divide = i.split("=")
            if(len(divide) == 2):
                body_parameter[str(divide[0])] = divide[1]
            else:
                body_parameter["null"] = "null"
        json_data = json.dumps(body_parameter)
        return json_data

    def delete_method(self, request, req_obj, client, addr):
        file_f = False
        filen = req_obj.uri.strip("/")
        file_uri = req_obj.uri
        path = req_obj.uri
        directory = "Delete_method"
        try:
            os.mkdir(directory)
        except:
            pass

        if(not os.path.exists(filen)):
            self.make_error_response(404, client, addr, req_obj)
            return
        if(os.path.isfile(filen)):
            file_f = True
            #print("file_f is true")
        if(file_f):
            if(os.access(filen, os.R_OK and os.W_OK)):
                #print("Have access")
                try:
                    os.remove(filen)
                    #print("Deleted")
                except:
                    current_path = os.getcwd()
                    current_path = current_path+"/"+filen
                    dest_path = os.getcwd()+"/"+directory
                   # print("cuurrent path", current_path)
                    #print("destination path", dest_path)
                    shutil.move(current_path, dest_path)
                   # print("moved to delete folder")

                self.make_error_response(200, client, addr, req_obj)
                return

            else:
                self.make_error_response(
                    403, client, addr, req_obj)  # permission denied
                return
        else:
            self.make_error_response(400, client, addr, req_obj)  # bad request
            return

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

    def make_error_response(self, status_c, client, addr, req_obj):
        #print(f"called {status_c}")
        not_body = False
        if(status_c == 200):
            response_line = self.make_responseline(status_c)
            response_line = response_line.decode()
            body = "<h1>OK</h1>"
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
            not_body = True
        elif(status_c == 201):
            response_line = self.make_responseline(status_c)
            response_line = response_line.decode()
            # response_line=response_line+location  location header to be added
            body = "<h1>New resource created</h1>"
        elif(status_c == 202):
            response_line = self.make_responseline(status_c)
            response_line = response_line.decode()
            body = "<h1>Accepted</h1>"
        elif(status_c == 505):
            response_line = self.make_responseline(status_c)
            response_line = response_line.decode()
            body = "<h1>Supported version HTTP/1.1</h1>"
        elif(status_c == 304):
            response_line = self.make_responseline(status_c)
            response_line = response_line.decode()
            not_body = True
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
        elif(status_c == 415):
            response_line = self.make_responseline(status_c)
            response_line = response_line.decode()
            body = "<h1>415 Unsupported Media Type </h1>"
        headers = self.add_header()
        if(not_body == False):
            headers = self.add_header()
            response = b"".join(
                [response_line.encode(), headers.encode(), "\r\n".encode(), body.encode()])
            for_log = b"".join(
                [response_line.encode(), headers.encode(), "\r\n".encode(), body.encode()])
        if(not_body):
            headers = self.add_header()
            response = b"".join(
                [response_line.encode(), headers.encode(), "\r\n".encode()])
            for_log = b"".join(
                [response_line.encode(), headers.encode(), "\r\n".encode()])
        log_size = sys.getsizeof(for_log)

        with open('Access.log', "a+") as fd:
            fd.write(
                f"{addr[0]} -- {time.ctime()}  {req_obj.method}  {req_obj.uri}  {req_obj.version}  {status_c}  {log_size} {req_obj.user_agent}\n")
        if(status_c >= 400):
            with open('Error.log', "a+") as fd:
                fd.write(
                    f"{addr[0]} --  {time.ctime()}  {req_obj.method}  {req_obj.uri}  {req_obj.version}  {status_c}  {log_size} {req_obj.user_agent}\n")
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
        #print(x)
        return x.encode()


def ready_start():
    #print("taking input")
    command = input()
    command = command.lower()
    if(command == "restart"):
        CLIENTS = []
        print("Restarting ")
        sock.close()
    elif(command == "stop"):
        print("Stopping ")
        sock.close()
        print("Server Stoped")
        # command_thread.
        # break
        sys.exit()
        return 0


if __name__ == '__main__':
    servern = '127.0.0.1'
    serverport = port_no
    print(port_no)
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind((servern, int(serverport)))
    sock.listen(50)
    print()
    command_thread = Thread(target=ready_start)
    command_thread.start()

    p = form_socket(servern, serverport)
    p.connect()
    input_thread = Thread(target=p.connect)
    input_thread.start()
