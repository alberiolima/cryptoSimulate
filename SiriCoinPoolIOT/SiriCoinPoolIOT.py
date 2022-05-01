import socket
import threading
import time
from web3.auto import w3
from random import randrange
from colorama import Fore #Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.

# Create the server, binding to localhost on port 9999
HOST, PORT = "localhost", 9999

def slocalIP():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ret = s.getsockname()[0]
        s.close()
    except:
        ret = socket.gethostbyname(socket.gethostname())
    return ret

def handle_client(conn, address):
    print(Fore.GREEN,"Connected to {}".format(address[0]),threading.active_count())
    connTemp = time.time()
    miner_id = "None"
    miner_diff = 1000
    block_nonce = 0
    conn.settimeout(5.0)
    while ((time.time() - connTemp) < 60):
        try:
          data = str(conn.recv(300).strip(), "utf-8")        
        except:
          data = ""
        if (len(data) > 10):
            connTemp = time.time()
            data = data.splitlines()[0]
            #print("{} wrote: ".format(address[0])+data)            
            cmd = data.split(',')
            if (cmd[0] == "$REQJOB"):
                if ( cmd[1] != miner_id ):
                    if ( len(cmd[1]) > 10 ):
                        print("Miner id: ",cmd[1])
                        miner_id = cmd[1]
                block_nonce = randrange(miner_diff)
                block_temp = int(time.time() * 1000)
                block_rand1 = randrange(4294967295)
                block_rand2 = randrange(4294967295)
                block_rand3 = randrange(4294967295)
                block_rand4 = randrange(4294967295)                
                block_last = w3.keccak(b"".join([block_temp.to_bytes(16, "big"),block_rand1.to_bytes(4, "big"), block_rand2.to_bytes(4, "big"), block_rand3.to_bytes(4, "big"), block_rand4.to_bytes(4, "big")]))                
                block_target = w3.keccak(b"".join([block_last,block_nonce.to_bytes(32, "big")]))
                print(Fore.YELLOW,"Send job",block_nonce,"to {}".format(address[0]))
                pacq = block_last.hex() + "," + block_target.hex() + ",3600,"+str(miner_diff)+"\n"
                conn.sendall(bytes(pacq,"utf-8"))
            elif (cmd[0] == "$RESULT"):				
                print(Fore.YELLOW,"Recv result from {} ".format(address[0]) + data )
                temp_nonce = 0
                try:
                    temp_nonce = int(cmd[1])
                    tempo_decorrido = round(int(cmd[2]) * 0.000001)
                except:
                    print("Invalid data:",data)
                pacq = "BAD\n"
                if ( temp_nonce == block_nonce):
                    pacq = "GOOD\n"
                block_nonce = 0
                conn.sendall(bytes(pacq,"utf-8"))
    print(Fore.RED,"{} closed".format(address[0]))
    try:
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
    except:
        print("close except")
      

def server():
    HOST = slocalIP()
    print("Starting SiriCoin POOL IOT")
    print("Listen:", HOST, "port:", PORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    
        
    s.bind((HOST, PORT))
    s.listen(5)
    while True:		
        (conn, address) = s.accept()
        t = threading.Thread(target=handle_client, args=(conn, address))
        t.daemon = True
        t.start() 

if __name__ == '__main__':
    try:
        server()
    except KeyboardInterrupt:
        print("Keyboard interrupt")
