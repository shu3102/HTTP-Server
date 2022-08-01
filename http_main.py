from socket import *
from datetime import datetime,timedelta
import calendar
import os
import mimetypes
import os.path, time 


class form_socket:
    global local_head
    
    header={'Server':'HTTP server','Content-Type':'text/html'}
    status_code={ 200: 'OK',
            404: 'NOT FOUND',
            501: 'Not Implemented',
            400: 'Bad Request',
            204: 'No Content',
            201: 'Created',
            304: 'Not Modified',
            401: 'Unauthorized',
            403: 'Forbidden'}
    local_head={}
    global CLIENTS
    CLIENTS=[]
    def __init__(self,servern,serverport):
        self.servern='127.0.0.1'
        self.serverport=10000
    def connect(self):
        sock=socket(AF_INET,SOCK_STREAM)
        sock.bind((self.servern,self.serverport))
        sock.listen(5)
        while 1:
            #client,addr=sock.accept()
            #print(addr,"is conneted")
            #req=client.recv(1024)
            #print(req.decode())
            #msg=self.parse_request(req)
            #print(msg.decode())
            #self.sendto(msg,addr)
            client,addr=sock.accept()
            print(addr,"is conneted")
            CLIENTS.append((client,addr))
            req=client.recv(2048)
            print(req.decode())
            msg = self.parse_request(req)
            print(msg.decode())
            self.mysend(msg,client,addr)
            return msg 
            
    def mysend(self, response, client,addr):
        for cli in CLIENTS:
            if(cli == (client,addr)):
                try:
                    client.sendto(response,addr)
                    client.close()
                except:
                    client.close()
                    self.remove(client)
    
    def remove(self,conn):
        if conn in CLIENTS:
            CLIENTS.remove(conn)
    
    def parse_request(self,req):
        global local_head
        local_head={}
        request=req.decode()
        
        line=request.split("\r\n")#split and extract line
        for j in range(1,len(line)):
            word=line[j].split(":")#getting header and its value by splitting
            if(len(word)>1):
              m=word[0]
              local_head[m]=word[1]
            if(len(word)<1):
              n=word[0]
              local_head[n]=" "
        #httpreq=httprequest(request)
        if("Connection" in local_head):
            if(local_head["Connection"]=="closed"):
                pass
                #non_persistent()
            if(local_head["Connection"]=="keep-alive"):
                pass
                #persistent()
        if("Connection" not in local_head):
                pass
                #non_persistent()
        if("Accept" in local_head):
                accept_values=httprequest.check_accept(self,local_head["Accept"])
               
        if("Host" not in local_head):
            response_line=self.make_responseline(self,400)
            error_msg=response_line+form_socket.add_header(self)
            return error_msg.encode()
        req_obj=httprequest(request)
        if(req_obj.method =="GET"):
              # pass
              GET_response=self.get_method(req,req_obj.uri,req_obj)
              return GET_response 
        if(self.method=="PUT"):
                pass
        if(self.method=="POST"):
              pass
        #if httpreq:
        #return httpreq
        #reply=self.form_response(request)
        #return reply
    def convert_to_gmt(self,date):
        dt=str(date).split(" ")
        tosend=""
        tosend+=dt[0]+", "+dt[2]+" "+dt[1]+" "+dt[4]+" "+dt[3]+" "+"GMT"
        return tosend
    def get_method(self, request,uri,req_obj):
        
        filen=uri.strip("/")
        print(filen)
        if (os.path.exists(filen)):
          print(uri)
          accept_val={}
          accept_val=req_obj.accept
         
          if(mimetypes.guess_type(filen)[0] not in accept_val):
              pass
          if(accept_val[mimetypes.guess_type(filen)[0]]==1):
            content_type = mimetypes.guess_type(filen)[0] #or 'text/html'
            extra_headers = {'Content-Type': content_type}
            response_headers = self.add_header(extra_headers)

            
            size=os.path.getsize(filen)
            extra_headers = {'Content-length': str(size)}
            self.header.update(extra_headers)
            #print("content-length is",size)
            response_headers = self.add_header(extra_headers)
            


            lastmodified=time.ctime(os.path.getmtime(filen))
            last_mod=self.convert_to_gmt(lastmodified)
            extra_headers={'Last-modified':last_mod}
            self.header.update(extra_headers)
            response_headers = self.add_header(extra_headers)


            
            format = "%a, %d %b %Y %H:%M:%S %Z"
            expires = datetime.utcnow() + timedelta(days=(365))
            expires = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
            extra_headers = {'Expires': expires}
            response_headers = self.add_header(extra_headers)
          
            
            if(req_obj.if_modified_since!=None):
                if datetime.strptime(last_mod, format) <= datetime.strptime(req_obj.if_modified_since, format):
                   response_line=form_socket.make_responseline(self,304)
                   response_headers =form_socket.add_header(self)
                   body=b"<h1>304 Not modified</h1>"
                   blank_line = b"\r\n"
                   return b"".join([response_line, response_headers.encode(), blank_line, body])
                
                    
            
            with open(filen, 'rb') as f:
                  body = f.read()
            response_line = form_socket.make_responseline(self,200)
        else:
            response_line = form_socket.make_responseline(self,404)
            response_headers =form_socket.add_header(self)
            body = b"<h1>404 Not Found</h1>"

        blank_line = b"\r\n"

        return b"".join([response_line, response_headers.encode(), blank_line, body])

    def make_responseline(self,status_c):
        code=self.status_code[status_c]
        resp="HTTP/1.1 "+str(status_c)+" "+str(code)+"\r\n"
        return resp.encode()

    def time_to_header(self,time_now):
        gmtdate=time.strftime("%a, %d %b %Y %H:%M:%S GMT",time_now)
        return gmtdate+"\r\n"
    def header_to_time(self,date_h):
        time_struct=time.strptime(date_h,"%a, %d %b %Y %H:%M:%S GMT")
        return time_struct
   

    def add_header(self,extra_headers=None):
       
        header_copy = self.header.copy() # make a local copy of headers
        
        if extra_headers:
           header_copy.update(extra_headers)
        
        head=""
        head+="Date:"+form_socket.time_to_header(self,time.localtime())
        for i in header_copy:
            head+=str(i)+":"+str(header_copy[i])+"\r\n"
        return head

    def form_response(self,req):
        response_line=self.make_responseline(200)
        res=self.add_header()
        blank="\r\n"
        body="Welcome to http"
        x="".join([response_line.decode(),res.decode(),blank,body])
        print(x)
        return x.encode()

class httprequest:
    header={'Server':'HTTP server','Content-Type':'text/html'}
    status_code={200: 'OK',
            404: 'NOT FOUND',
            501: 'Not Implemented',
            400: 'Bad Request',
            204: 'No Content',
            201: 'Created',
            304: 'Not Modified',
            401: 'Unauthorized',
            403: 'Forbidden'}
    
    global local_head
    def __init__(self,data):
        self.method=None
        self.uri=None
        self.version="1.1"
        self.accept=self.check_accept(local_head["Accept"])
        self.if_modified_since=None
        self.Range = None
        self.encoding = None
        self.user_agent=None
        self.parserequest(data)
        
    def parserequest(self,data):
        local_head={}
        line=data.split("\r\n")
        
        for j in range(0,len(line)):
            
            word=line[j].split(":")
            if(len(word)>1):
              local_head[word[0]]=word[1]
            else:
              local_head[word[0]]=" "

        req_line=line[0].split(" ")
        length=len(req_line)
        if("If-Modified-Since" in local_head):
            print("Prsent=============")
            self.if_modified_since=local_head["If-Modified-Since"]
        
        if(length>1):
           self.uri=req_line[1]
           self.method=req_line[0]
           
        if(length>2):
            self.version=req_line[2]
        self.user_agent= local_head['User-Agent']
        if("If-Modified-Since" in local_head):
            self.Range = local_head['Range']
        self.encoding = local_head['Accept-Encoding']

   
    def check_accept(self,req):
        
        word=req.split(",")
        accept_values={}
        
        for i in range(0,len(word)):
            sp=word[i]
            additional=sp.split(";")
            if(len(additional)==1):
                accept_values[additional[0].strip(" ")]=1
                #type_content.append(additional[0])
                #value_content.append(1)
            elif(len(additional)>1):
                #type_content.append(additional[0])
                qvalue=additional[1].split("=")
                #value_content.append(float(qvalue[1]))
                accept_values[additional[0].strip(" ")]=float(qvalue[1])
        print("Type content:",accept_values)
        return accept_values        
if __name__=='__main__':
 p=form_socket('127.0.0.1',10000)
 p.connect()
 
