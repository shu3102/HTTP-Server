from socket import *
from datetime import datetime
import calendar

class form_socket:
    header={'Server':'HTTP server','Content-Type':'text/html'}
    status_code={200:'OK',404:'NOT Found',400:'BAD REQUEST'}
    def __init__(self,servern,serverport):
        self.servern='127.0.0.1'
        self.serverport=10000
    def connect(self):
        sock=socket(AF_INET,SOCK_STREAM)
        sock.bind((self.servern,self.serverport))
        sock.listen(5)
        while 1:
            client,addr=sock.accept()
            print(addr,"is conneted")
            req=client.recv(1024)
            print(req.decode())
            msg=self.parse_request(req)
            client.sendto(msg,addr)
            return msg
    def parse_request(self,request):
        local_head={}
        request=request.decode()
        line=request.split("\r\n")#split and extract line
        for j in range(1,len(line)):
            word=line[j].split(":")#getting header and its value by splitting
            if(len(word)>1):
              m=word[0]
              local_head[m]=word[1]
            if(len(word)<1):
              n=word[0]
              local_head[n]=" "
      
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
                type_content,value_content=httprequest.check_accept(self,local_head["Accept"])
               
        if("Host" not in local_head):
            response_line=make_responseline(self,400)
            error_msg=response_line+form_socket.add_header(self)
            return error_msg.encode()
        reply=self.form_response(request)
        return reply

    def make_responseline(self,status_c):
        code=self.status_code[status_c]
        resp="HTTP/1.1 "+str(status_c)+" "+str(code)+"\r\n"
        return resp.encode()

    def add_date(self):
        datetime_obj=datetime.now()
        datestr=str(datetime_obj)
        time=datetime_obj.strftime("%H:%M:%S")
        timest=datetime.timestamp(datetime_obj)
        date_time=datetime.fromtimestamp(timest)
        d=date_time.strftime("%c")
        dt=str(d).split(" ")
        tosend=""
        tosend+=dt[0]+","+dt[2]+" "+dt[1]+" "+dt[4]+" "+dt[3]+" "+"GMT"
        return "Date:"+tosend+"\r\n"

    def last_modified():
        pass

    def add_header(self):
        head=""
        head+=self.add_date()
        for i in self.header:
            head+=str(i)+":"+str(self.header[i])+"\r\n"
        
        return head.encode()

    def form_response(self,req):
        response_line=self.make_responseline(200)
        res=self.add_header()
        blank="\r\n"
        body="Welcome to http"
        x="".join([response_line.decode(),res.decode(),blank,body])
        print(x)
        return x.encode()

class httprequest:
    
    def __init__(self,data):
        self.method=None
        self.uri=None
        self.version="1.1"
        self.parse_request(data)
    def parse_request(self,data):
        local_head={}
        d=data.split("\r\n")
        word=[]
        for j in range(0,len(line)):
            word=d[j].split(":")
            local_head[word[0]]=word[1] 

        req_line=d[0].split(" ")
        length=len(req_line)
        if(length>1):
           self.uri=req_line[1]
           self.method=req_line[0]
           if(self.method=="GET"):
               pass
           if(self.method=="PUT"):
                pass
           if(self.method=="POST"):
              pass
        if(length>2):
            self.version=req_line[2]
    def check_accept(self,req):
        word=req.split(",")
        type_content=[]
        value_content=[]
        for i in range(0,len(word)):
            sp=word[i]
            additional=sp.split(";")
            if(len(additional)==1):
                type_content.append(additional[0])
                value_content.append(1)
            elif(len(additional)>1):
                type_content.append(additional[0])
                qvalue=additional[1].split("=")
                value_content.append(float(qvalue[1]))
        print("Type content:",type_content)
        print("Value content",value_content)
        return type_content,value_content         
if __name__=='__main__':
 p=form_socket('127.0.0.1',10000)
 p.connect()
 
