# -*- coding: utf-8 -*-
"""
Created on Sat Feb 25 20:13:27 2017

@author: DELL API
"""
import sys
import socket
import re
import time
from multiprocessing import Process, Manager  #python libarary which manages multiple process concurrently

Ser_Address= (HOST, PORT) = '', 8820
Q_Size = 100  #server handles at most Q_Size requests
socket_pos = {} # dictionary containing conn_ID as key a socket object as a value
proc_pos = {} # dictionary containing conn_ID as key a process object (multiprocessing Process object) as a value
 
 #method which is run by Process class and for sending response after time completion
 #connId-the id given by client
 #time_out=the timeout given by client
 #Time_pos=dictionary for holding connId as key and time left as value
 #client_conn=socket object to send msg
 #socket_pos=above dictionary
def timesleep(connId,time_out,Time_pos,client_conn,socket_pos):
        print("in function")
        remain_time= int(time_out)
        # updating time status dictionary after every 1sec
        while remain_time >0:
           time.sleep(1)
           remain_time=remain_time-1
           Time_pos[connId]=remain_time
        msg = """\
        {"status":"OK"}
        """
        client_conn.sendall(msg.encode('utf-8'))
        del Time_pos[connId]  #deleting connId key from the dictionary
        client_conn.close() #closing the socket object
        sys.exit(0) #terminate the process


def server_always():
    #create an AF_INET, STREAM socket (TCP)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind(Ser_Address)
    s.listen(Q_Size)
    #creating python process manager which enables us to share dictionary among all process"
    M_ger = Manager()
    Time_pos = M_ger.dict()
    print("Serving HTTP on port "+str(PORT))
    #loop which run continuesly and wait for client to connect
    while True:
        client_conn, client_address = s.accept()
        request = client_conn.recv(2234867)
        data=request.decode()
        a=data.split(" ")
        

        #Checking GET or PUT request by checking the header of the recieved msg
        
        if a[0]=='GET':
            if 'connId' in a[1]:
                #Getting connId and timeout value from request
                req_regex = re.compile("(?<=connId=)(?P<value>.*?)(?=&)")
                matched = req_regex.search(a[1])
                connId =matched.group('value')
               
                p=a[1].split("&timeout=")
                
                
                Time_pos[connId]=p[1]
                # Using process such that for each connId it restarts
                p1 = Process(target=timesleep, args=(connId,p[1],Time_pos,client_conn,socket_pos))
                socket_pos[connId]=client_conn
                proc_pos[connId]=p1
                p1.start()
                
            elif 'api/serverStatus' in a[1]:
               
                msg="{"
                for key,value in Time_pos.items():
                    msg=msg+"'"+str(key)+"':"+"'" +str(value)+"',"
                msg=msg+"}"
                client_conn.sendall(msg.encode('utf-8'))
                client_conn.close() 


        
        elif a[1]=='/api/kill':
            # Getting payload value of connId from PUT request
            temp= a[7].split(":")
            temp=temp[1].split("}")
            connId = temp[0]
            if connId in Time_pos:
                    #Sending msg to running request and also current req
                    msg = """{"status":"killed"}"""
                    socket_pos[connId].sendall(msg.encode('utf-8'))
                    socket_pos[connId].close() 
                    proc_pos[connId].terminate()# terminate process corres. to given connId
                    del Time_pos[connId]
                    del socket_pos[connId]
                    del proc_pos[connId] 
                    msg= """{"status":"Ok"}"""
                    client_conn.sendall(msg.encode('utf-8'))
                    
                    client_conn.close()
                    
            else: 
                    msg = """{"status":"invaild connection Id" :"""+str(connId)+"}"
                    client_conn.sendall(msg.encode('utf-8'))
                    client_conn.close()
    s.close()
             
        
if __name__ == '__main__':
    server_always()
