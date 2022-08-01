
from socket import *
import time
from threading import Thread
import requests
from ntpath import join
import requests
import os
import string 
import random
from wsgiref.handlers import format_date_time


server_port=10000
server_ip='127.0.0.1'



def test_get_files():
    time.sleep(1)
    
    url=['cn.htm','mymusic.mp3','myimage.jpg','slick.bin']
    for i in url:
      response=requests.get(f'http://{server_ip}:{server_port}/{i}')
      print("\n***TEST OF FILES GET***")
      if(response.status_code==200):
            print(f"Received status code: {response.status_code}")
            try:
             with open(f"{i}",'rb') as file:
                   body=file.read()
             file.close()
             if(body==response.content):
                   print(f"GET request successful for {i} file")
            except:
                print("Can't open the file")
      else:
            print(f"Received {response.status_code} for {i} file")
def test_conditional_get(): 
    time.sleep(1)
    
    last_mod=os.path.getmtime('cn.htm')
    l_date=format_date_time(last_mod)
    extra_head={'If-Modified-Since':l_date}        
    response=requests.get(f'http://{server_ip}:{server_port}/cn.htm',headers=extra_head)   
    print("\n***Conditional GET***")     
    if(response.status_code==304):
            print(f"Received status code: {response.status_code}")
            print("Conditional GET--> successfull")
def test_cookie():
    time.sleep(1)
    
    extra_head={'Cookie':'1025'}
    response=requests.get(f'http://{server_ip}:{server_port}/cn.htm',headers=extra_head)
    print("\n***TEST OF COOKIE***")
    print("Sending Cookie header with request")
    if ('Set-Cookie' not in response.headers):
       print("Not received Cookie--> Successful")
    else :
       print("Received cookie")
    response=requests.get(f'http://{server_ip}:{server_port}/cn.htm')

    print("NOT Sending Cookie header with request")
    if ('Set-Cookie' in response.headers):
       print("Received Cookie--> Successful")
       print(f'Received cookie:{response.headers["Set-Cookie"]}')
    elif('Set-Cookie' not in response.headers):
       print("Cookie--> Unsuccessful")
def test_get_404():
    time.sleep(1)
    
    response=requests.get(f'http://{server_ip}:{server_port}/foo.txt')
    print("\n***TEST OF 404 GET***") #not found
    print(response)
    if(response.status_code==404):
            print(f"Received status code: {response.status_code}-->Successful")
    else:
            print(f"Received status code: {response.status_code}-->Unsuccessful")

def test_get_permission():
    time.sleep(1)
    
    response=requests.get(f'http://{server_ip}:{server_port}/index_404.txt')#take file here
    print("\n***TEST OF 403 GET***")  #forbidden file
    if(response.status_code==403):
            print(f"Received status code: {response.status_code}-->Successful")
    else:
            print(f"Received status code: {response.status_code}-->Unsuccessful")

def test_get_directory():
    time.sleep(1)
    
    response=requests.get(f'http://{server_ip}:{server_port}/Master')
    print("\n***TEST OF DIRECTORY GET***")
    if(response.status_code==200):
            print(f"Received status code: {response.status_code}-->Successful")
    else:
            print(f"Received status code: {response.status_code}-->Unsuccessful")

def test_head():
    time.sleep(1)
    
    response=requests.head(f'http://{server_ip}:{server_port}/index.html')
    print("\n***TEST OF HEAD***")
    if(response.status_code==200):
            print(f"Received status code: {response.status_code}-->Successful")
    else:
            print(f"Received status code: {response.status_code}-->Unsuccessful")

def test_max_uri():
    time.sleep(1)
    
    res=''.join(random.choices(string.ascii_lowercase,k=256))
    response=requests.get(f'http://{server_ip}:{server_port}/{res}')
    print("\n***TEST OF GET 414***")#request uri too long
    if(response.status_code==414):
            print(f"Received status code: {response.status_code}-->Successful")
    else:
            print(f"Received status code: {response.status_code}-->Unsuccessful")

def test_delete():  
    time.sleep(1)  
    
    try:
       f=open('for_delete.txt','w')
       print("sample file created for delete")
       f.write("hello this is for delete method")
       f.close()
       response=requests.delete(f'http://{server_ip}:{server_port}/for_delete.txt')
       print("\n***TEST OF DELETE***")
       if(response.status_code==200 or response.status_code==202 or response.status_code==204):
            print(f"Received status code: {response.status_code}-->Successful")
       else:
            print(f"Received status code: {response.status_code}-->Unsuccessful")
    except:
        print("Can't form sample file for delete")









def put_file(url,path,):
    time.sleep(1)
    print("\n***TEST OF PUT File***")
    x = requests.put(url, data=open(path, 'rb'))
    if(x.status_code==201 or x.status_code==202 or x.status_code==200):
        print(f"Received status code: {x.status_code}-->Successful")
    else:
        print(f"Received status code: {x.status_code}-->Unsuccessful")
    

def put(url,obj):
    time.sleep(1)
    
    try:
        x = requests.put(url, data = obj) 
        print("\n***TEST OF PUT ***")
        if(x.status_code==201 or x.status_code==202 or x.status_code==200):
            print(f"Received status code: {x.status_code}-->Successful")
        else:
            print(f"Received status code: {x.status_code}-->Unsuccessful")
    except:
        print("Unsuccesful ")


def post(url, obj):
    
    time.sleep(1)
    x = requests.post(url, data=obj)
    print("\n***TEST OF POST***")
    if(x.status_code==201 or x.status_code==202 or x.status_code==200):
        print(f"Received status code: {x.status_code}-->Successful")
    else:
        print(f"Received status code: {x.status_code}-->Unsuccessful")
    

def post_multipart(url,file):
    
    time.sleep(1)
    x = requests.post(url, files=file)
    print("\n***TEST OF POST Multipart***")
    if(x.status_code==201 or x.status_code==202 or x.status_code==200):
        print(f"Received status code: {x.status_code}-->Successful")
    else:
        print(f"Received status code: {x.status_code}-->Unsuccessful")
    



if(1):
    port = 10000
    host = '127.0.0.1'
    base_url = "http://" + 	str(host) + ":" + str(port) 

    '''
    GET
    '''

    Thread(target = test_get_files).start()
    Thread(target = test_conditional_get).start()
    Thread(target = test_cookie).start()
    Thread(target = test_get_404).start()
    Thread(target = test_get_permission).start()
    Thread(target = test_get_directory).start()
    Thread(target = test_head).start()
    Thread(target = test_max_uri).start()
    Thread(target = test_delete).start()
    #test_get_files()
    #test_conditional_get()
    #test_cookie()
    #test_get_404()
    #test_get_permission()
    #test_get_directory()

    

    '''
    HEAD
    '''










    '''
    PUT
    '''
    objput = {'put1': 'value1', 'put2': 'value2'}
    # already existing file
    url = base_url + "/dll.txt"
    Thread(target = put, args=(url,objput,)).start()
    #put(url,objput)

  
    

    time.sleep(1)
    print("started")
    #put with a text file
    url = base_url + "/myNew.txt" 
    path = "dll.txt"
    filename = "dll"
    #Thread(target = put_file, args=(url,path)).start()
    put_file(url, path)



    url = base_url + "/Master"
    obj = {'key1': 'value1', 'key2': 'value2'}
    #Thread(target = post, args=(url,obj,)).start()
    post(url, obj )


    
    
