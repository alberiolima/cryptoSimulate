import time, serial
import socket
import sys
from colorama import Fore

#change usb-serial port (baud=115200)
serialPort = "/dev/ttyACM0"

#miner id
minerAddr = "0x0E9b419F7Cd861bf86230b124229F9a1b6FF9674"
minerDiff = 1000

#client TCP
HOST, PORT = "192.168.1.36", 9999

results_good = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
	#Conecta com servidor TCP
    tcp_connected = False
    print("Connecting", HOST, PORT)
    try:
      sock.connect((HOST, PORT))
      sock.settimeout(5.0)
      tcp_connected = True
      print("TCP connetecd")
    except:
      print("TCP error")		
    
    #Conecta com iot via serial
    serial_connected = False
    print("Connecting serial", serialPort)
    try:
        ser = serial.Serial(f"{serialPort}", baudrate=115200, timeout=2.5)
        time.sleep(2)
        serial_connected = True
        print("Serial connetecd")
    except:
        print("Serial error")
    
    time_wait = time.time() + 240
    while (time.time() < time_wait):
        #Solicita trabalho
        print("Request job")
        sock.sendall(bytes("$REQJOB,"+minerAddr+","+str(minerDiff)+"\n", "utf-8"))
    
        #Recebe trabalho 
        job_received = sock.recv(300)
        if len(job_received)>32:
            print("Received job")
            print("Send job to IOT")
            ser.flush()            
            ser.write(job_received)
        
        #aguarda resposta do iot       
        iot_received = b""        
        while (time.time() < time_wait):            
            if (ser.in_waiting>0):
                byte_lido = ser.read()
                iot_received = iot_received + byte_lido
                if (byte_lido == b'\n'):        
                    break;

        #envia resultado recebido para o TCP
        hashrate = 0
        if (len(iot_received)>32):
            ress = str(iot_received.strip(),"utf-8").split(',')
            try:
                n = int(ress[0].rstrip())
                t = int(ress[1].rstrip()) * 0.000001
                hashrate = round(n / t,2)
            except:
                print(f"invalid data: {iot_received}")
            print("Serial IOT response")
            print("Send result")
            sock.sendall(b"".join([b"$RESULT,",iot_received]))
            time_wait = time.time() + 240
        #recebe resposta
        time.sleep(2)
        result_response = str(sock.recv(300).strip(),"utf-8")
        if (len(result_response)>3):
            if (result_response=="GOOD"):
                results_good += 1
            print(result_response, results_good, hashrate )
