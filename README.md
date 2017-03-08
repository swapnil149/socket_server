Platform Used for creating the Server:Python 3.6
I have tested my server using curl.  

Server runs from cmd as
python server.py


Implementation of Server:-
I have created a socket which is bind with address as localhost:8820. Now we need to connect 
our socket with client, so my socket is waiting for client collection. When server gets 
any connection request, it accept it & take the header of the client request. 
Now my server has to decide the type of request i.e PUT or GET, so by parsing the header it access the type.After 
deciding it takes  action accordingly. My server also runs for new connection given by client request
with some connection-Id & timeout and then allocate them a new process for the given time.
After completion of time, server respond them & process get terminated by server.

For tracking the current status of server I have created Time_pos dictionary which is shared
among all process and updated every second.I have also created socket_pos &
process_pos dictionary which is useful to kill any process or close any connection.


Output when we send request
Test Client 1: curl 'http://localhost:8820/api/request?connId=12&timeout=120'
   Output After 120 second {"status":"OK"}

Test Client 2: curl 'http://localhost:8820/api/request?connId=19&timeout=170'
   

Test Client 3: curl http://localhost:8820/api/serverStatus
   Output {'12':'85','19':'149',}

Test  Client 4: curl -H 'Content-Type: application/json' -X PUT -d '{"connId":9}' 
                http://localhost:8820/api/kill
   Output {"status":"invaild connection Id" :9}

Test Client 5: curl -H 'Content-Type: application/json' -X PUT -d '{"connId":19}' 
                     http://localhost:8820/api/kill
   Output {"status":"killed"} for Test Client 2
          {"status":"OK"} for test client 5

Understanding Test:

If my client request is PUT request and PUT API as "api/kill" with payload as {"connId":19},then
my Test client 2 returns {"status":"killed"} and the current request(Test Client 5) will 
return {"status":"ok"}. Also if no running request found with the provided connId on the server 
then the current request(Test Client 4) return {"status":"invalid connection Id" : 9"}.
