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
import json
import string
import random
import shutil
from configparser import ConfigParser




config=ConfigParser()
print(config.read('server_config.ini'))
global cookie_id
MAX_URI_LEN =config['http_server']['max_urllen']
port_no=config['http_server']['port_no']
MAX_PAYLOAD=config['http_server']['max_payload']
cookie_id =config['http_server']['cookie_id']
print("COOOKie id",cookie_id)
print(type(cookie_id))


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
        self.serverport = 10001

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
            req = client.recv(8192)
            f = open("p1.txt", "w")
            f.write(req.decode(encoding="utf8", errors='ignore'))
            f.close()
            #print(req.decode(encoding="utf8", errors='ignore'))
            print("\n\n\n\n\n @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n\n")
            #print(req.decode())
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
        self.cookie=None
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
        # request=req.split("\n")
        # if(len(request)>1):
        # self.req_body=req

        reqHeader, reqBody = httprequest.split_by_header(req)
        #reqHeader = httprequest.split_by_header(req)

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
            response_obj=httpresponse()
            text = b"\r\n+Error"
            response_line=self.make_responseline(400)
            response_headers=self.add_header()
            blank_line = b"\r\n"
            body=b"Error"
            form_socket.mysend(b"".join([response_line, response_headers.encode(), blank_line, body]),client,addr)
            return
            
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
        if("Content-Type" in local_head):
            self.containt_type = local_head['Content-Type']
        if("Content-Length" in local_head):
            self.containt_length = local_head["Content-Length"]
        if("Accept-Encoding" in local_head):
         self.encoding = local_head['Accept-Encoding']
        if("Accept" in local_head):
         self.accept = local_head["Accept"]
       
        if("Cookie" in local_head):
            print("happy")
            self.cookie=local_head['Cookie']
        
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
            res_obj=httpresponse()
            res_obj.make_error_response(400,client,addr)
        # req_obj=httprequest(request)
        if(self.method == "GET"):
            response_obj = httpresponse()
            GET_response = httpresponse.get_method(
                response_obj, req, self, client, addr,head=False)
            if(GET_response!=None):
               print(GET_response.decode())
            # form_socket.mysend(GET_response,client,addr)

            # form_socket.mysend(GET_response,client,addr)
        if(self.method == "PUT"):
            response_obj = httpresponse()
            PUT_responce = httpresponse.put_method(
                response_obj, req, self, client, addr)
            form_socket.mysend(PUT_responce, client, addr)

        if(self.method == "POST"):
            print("################################# CALLING POST ########################################## ")
            response_obj = httpresponse()
            POST_responce = httpresponse.post_method(response_obj, req, self, client, addr)

            form_socket.mysend(POST_responce, client, addr)
        
        if(self.method=="DELETE"):
            response_obj=httpresponse()
            httpresponse.delete_method(response_obj,req,self,client,addr)
        if(self.method=="HEAD"):
            response_obj=httpresponse()
            httpresponse.get_method(response_obj,req,self,client,addr,head=True)




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
    def get_method(self,request,req_obj,client,addr,head):
       
        file_f=False
        read_p=False
        dir_f=False
        if(req_obj.uri=='/'):
            req_obj.uri='/index.html'
        if(req_obj.uri=='/favicon.ico'):
            req_obj.uri='/myimage.jpg'
        filen=req_obj.uri.strip("/")
        print("filen is",filen)
        
        if(len(req_obj.uri)>255):
            
            self.make_error_response(414,client,addr)
            return
        if(os.path.isdir(filen)):
            dir_f=True
        if(not os.path.exists(filen)):
            print("Not exists")
        if (os.path.exists(filen)):
          if(os.path.isfile(filen)):
              file_f=True
              print("file present")
              if(os.access(filen, os.R_OK)):
                  read_p=True
                  print("read permisson")
          
          
          
          if(read_p==False):
              self.make_error_response(403,client,addr)
          #if(mimetypes.guess_type(filen)[0] not in accept_val):
             # pass
          if(file_f==True and read_p==True):
            content_type = mimetypes.guess_type(filen)[0] #or 'text/html'
            extra_headers = {'Content-Type': " "+content_type}
            header.update(extra_headers)
            response_headers = self.add_header(extra_headers)

            
            size=os.path.getsize(filen)
            extra_headers = {'Content-length':" "+ str(size)}
            header.update(extra_headers)
            #print("content-length is",size)
            response_headers = self.add_header(extra_headers)
            
            extra_headers={'Accept-Ranges':' bytes'}
            header.update(extra_headers)
            response_headers = self.add_header(extra_headers)
            
            lastmodified=os.path.getmtime(filen)
            print(lastmodified)
            last_mod=format_date_time(lastmodified)
            extra_headers={'Last-modified':" "+last_mod}
            header.update(extra_headers)
            response_headers = self.add_header(extra_headers)


            
            format_m = "%a, %d %b %Y %H:%M:%S GMT"
            expires = datetime.utcnow() + timedelta(days=(365))
            expires = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
            extra_headers = {'Expires': " "+expires}
            header.update(extra_headers)
            response_headers = self.add_header(extra_headers)
            
            
            if req_obj.cookie!=None:
             print("ckiie")
             expire = datetime.utcnow() + timedelta(days=(1))
             expire = expire.strftime("%a, %d %b %Y %H:%M:%S GMT")
             cookie_id=config['http_server']['cookie_id']
             c="id="+str(cookie_id)+';'+'Expires='+expire+';'
             extra_headers = {'Set-Cookie': " "+c}
             header.update(extra_headers)
             response_headers = self.add_header(extra_headers)
             with open('server.cookie','a+') as f:
                towrite="".join(("IP ADDRESS=",str(addr),"|","COOKIE ID=",cookie_id))
                f.write(towrite)
                f.close()
             s=int(cookie_id)
             s=s+1
             config['http_server']['cookie_id']=str(s)
             with open('server_config.ini','w') as file:
                    config.write(file)
                    file.close() 
        
            if(req_obj.if_modified_since!=None):
               
                if self.header_to_time(req_obj.if_modified_since) >= self.header_to_time(last_mod) : #time.strptime(req_obj.if_modified_since,"%a, %d %b %Y %H:%M:%S GMT"):
                   print("compared")
                   print(self.header_to_time(req_obj.if_modified_since) >= self.header_to_time(last_mod))
                   self.make_error_response(304,client,addr)
                   return
                  # response_line=self.make_responseline(304)
                  # response_headers =self.add_header()
                  # body=b"<h1>304 Not modified</h1>"
                  # blank_line = b"\r\n"
                  # complete_resonse=b"".join([response_line, response_headers.encode(), blank_line])
                  # form_socket.mysend(complete_resonse,client,addr)
            encode_f=False
            gzip_f=False        
            if('Accept-Encoding' in local_head):
                 encode_f=True
                 if('gzip' in local_head['Accept-Encoding']):
                     gzip_f=True
                     extra_headers={'Content-Encoding':' gzip'}
                     header.update(extra_headers)
                     response_headers = self.add_header(extra_headers)
                     
            print("These are response headers")
            print(response_headers)
            with open(filen, 'rb') as f:
                  body = f.read()
            
            if(encode_f==True and  gzip_f==True):
                  body=gzip.compress(body)
            response_line = self.make_responseline(200)
            blank_line = b"\r\n"
            if(head==False):
                form_socket.mysend(b"".join([response_line, response_headers.encode(), blank_line, body]),client,addr)
            elif(head==True):
                form_socket.mysend(b"".join([response_line, response_headers.encode(), blank_line]),client,addr)
        else:
             response_headers =self.add_header()
             response_line=self.make_responseline(404)
             body=b"<h1>404 not found</h1>"
             blank_line = b"\r\n"
             form_socket.mysend(b"".join([response_line, response_headers.encode(), blank_line, body]),client,addr)
             return

        blank_line = b"\r\n"
        response_line=self.make_responseline(400)
        response_headers=self.add_header()
        body=b"Bad request"
        form_socket.mysend(b"".join([response_line, response_headers.encode(), blank_line, body]),client,addr) 
        return
        
    
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

    def post_method(self, request, req_obj, client, addr):
        #print(req_obj)
        #print(request)

        containt_type = (req_obj.containt_type).strip(" ")
        containt_type.strip(" ")
        print("PRINTING CONTAINT TYPE ")
        print(containt_type)
        body = req_obj.req_body
        print("Data is ____________")
        #print(body)
        print(req_obj.uri)
        if(str(containt_type) == "application/x-www-form-urlencoded"):
            print("inside application/x/www-form-urlencoded")
            respnceGot = self.post_encoded(body)
            filePath = "post1.json"

            if(os.path.exists(filePath)):
                status_code = 200

            elif(not(os.path.exists(filePath))):
                status_code = 201
                #create file

            f = open(filePath, 'w')
            f.write(str(respnceGot))
            f.close()
            
            response_headers = self.add_header()
            response_line = self.make_responseline(status_code)
            body = b"Request file added"
            blank_line = b"\r\n"
            return b"".join([response_line, response_headers.encode(), blank_line, body])
        
        elif(containt_type == "multipart/form-data"):
            print("**************************************************************************************************************8")
            post_uri = req_obj.uri
            if(str(post_uri) != "/"):
                post_uri = str(post_uri).strip("/")
                f = open(post_uri, 'w')
                f.write(body)
                f.close()

                response_headers = self.add_header()
                response_line = self.make_responseline(201)
                responce = post_uri + "Request file added"
                body = responce.encode()
                blank_line = b"\r\n"
                return b"".join([response_line, response_headers.encode(), blank_line, body])
            
            filePath = "post1.txt"
            status_code = 201
                #create file
            print(type(body))
            new_body = body.split("\r\n")
            print(len(new_body))
            #print(new_body)
            print(len(body))
            #print(body)
            entity_data = ""
            isbinary = False
            for i in range(1,len(new_body)):
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
            print("PRINTING ENTITY DATA FROM IN FUNCTION \n \n")
            print(entity_data)
            split_char = entity_data.split(':')[0]
            print("\n\n This is split_char\n\n")
            print(split_char)
            new_message = entity_data.split(split_char + ':' )
            print("\n\n This is new Message\n\n")
            print(new_message)
            new_message.pop(0)
            print(len(new_message))
            for z in range(0,len(new_message)):
                new_message[z] = new_message[z].lstrip(' name=')
            print("This is putside for loop")
            print(new_message)
            if_file_exist = 0
            count = 0
            for i in new_message:
                if 'filename' in i:
                    print("Got Filename")
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
            
            print(data)

            #if file exist write data into file:
            if(if_file_exist == 1):
                print("Comming in File Exist")
                filename = filedata.split("filename=")
                print("FILE NAME IS THIS -------" + filename)
                if(len(filename) >= 2):
                    fname = filename[1].split("\r\n")[0].strip('"')
                    # error handling required
                    if(isbinary):
                        temp = filename[1].split("\r\n")
                        fdata = ""
                        # print("TEAMP {} {}".format(temp,len(temp)))
                        for i in range(1,len(temp)):
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
                        result_str = ''.join(random.choice(letters) for i in range(5))
                        fname =  result_str+fname
                    fname = fname
                    if(isbinary):
                        fwrite = open(fname, "wb")
                        fwrite.write(fdata.encode("ISO-8859-1"))
                        fwrite.close()
                    else:
                        fwrite = open(fname,"w")
                        fwrite.write(fdata)
                        fwrite.close()
                else: 
                    pass
                data.append(new_message[count].split(' filename=')[0] + "filename=" + fname)
            #return data

            f = open(filePath, 'w')
            f.write(str(data))
            f.close()
            
            response_headers = self.add_header()
            response_line = self.make_responseline(status_code)
            body = b"Request file added"
            blank_line = b"\r\n"
            return b"".join([response_line, response_headers.encode(), blank_line, body])

        

        
        else: 
            status_code = 415
            response_headers = self.add_header()
            response_line = self.make_responseline(status_code)
            body = b"<h1>415 Unsupported Media Type </h1>"
            blank_line = b"\r\n"
            #print("sending responce")
            return b"".join([response_line, response_headers.encode(), blank_line, body])
        
        


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
        file_f=False
        filen=req_obj.uri.strip("/")
        file_uri=req_obj.uri
        path=req_obj.uri
        directory="Delete_method"
        try:
            os.mkdir(directory)
        except:
            pass
        
        if( not os.path.exists(filen)):
            self.make_error_response(404,client,addr)
            return
        if(os.path.isfile(filen)):
            file_f=True
            print("file_f is true")
        if(file_f):
            if(os.access(filen,os.R_OK and os.W_OK)):
                print("Have access")
                try:
                    os.remove(filen)
                    print("Deleted")
                except:
                    current_path=os.getcwd()
                    current_path=current_path+"\\"+filen
                    dest_path=os.getcwd()+"\\"+directory
                    print("cuurrent path",current_path)
                    print("destination path",dest_path)
                    shutil.move(current_path,dest_path)
                    print("moved to delete folder") 
                  
                self.make_error_response(200,client,addr)
                return   
                    
            else:
                self.make_error_response(403,client,addr)#permission denied
                return
        else:
         self.make_error_response(400,client,addr)#bad request
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


