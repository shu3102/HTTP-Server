# http-server



## Description
This is an implementation of an HTTP/1.1 complaint multi threaded web server to handle common web requests. This project was done as a part of the Computer Networks course.

## About
This project is aimed at the implementation of the HTTP/1.1 Protocol based on RFC 2616 and incorporates the basic HTTP methods of `GET`, `POST`, `PUT`, `DELETE` and `HEAD`.



## Steps to run the project:
```
0. Clone the Project
1. The main server file is server.py
2. Run python3 webserver.py
3. For testing, mytesting.py file is present
4. Configuration file of the server is server_config.ini
5. Log file of server is Access.log and will get updated as you make new requests.
6. Way to stop and restart the server by typing stop and restart respectively.
```


## Project features:
### 1. HTTP Request Methods Implemented:
* GET
* PUT
* POST
* HEAD
* DELETE


### 2. Config file:
Implemented configuration file with Document Root for some functionalities of server.


### 3. Multithreading in server:
Implemented multithreading in server to run multiple requests simultaneously


### 4. Logging:
* Levels of Logging - Implemented INFO and ERROR levels of logging for the log file
* Folder (Logfiles) - Compression of logfiles and moving them to a folder sequentially after a particular time


### 5. Automated Tests:
Implemented different tests using multithreading and requests module


### 6. Implemented Cookies and handled Persistent and non-Persistent connections


