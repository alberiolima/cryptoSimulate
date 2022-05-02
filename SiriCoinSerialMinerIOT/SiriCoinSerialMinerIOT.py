import time, serial
import socket
import sys
from colorama import Fore
import os.path 
from threading import Thread
import configparser

configMinerName = 'config.ini'
configMiner = configparser.ConfigParser()

#change usb-serial port (baud=115200)
serialPorts = ""

#miner id
minerAddr = ""
minerDiff = 1000

#client TCP
HOST, PORT = "192.168.1.33", 9999

results_good = 0

def readConfigMiner():
    configMiner['DEFAULT'] = {'miner_addr': '', 'serial_ports': '','time_work': 20 }
    if (os.path.exists(configMinerName) is False):
        writeConfigMiner()
    global minerAddr,serialPorts,tempoTrabalhar
    try:        
        configMiner.read(configMinerName)
        def_config = configMiner["DEFAULT"]
        minerAddr = def_config["miner_addr"]
        serialPorts = def_config["serial_ports"]
        tempoTrabalhar = int(def_config["time_work"])
    except:
        print("error read config file") 

def writeConfigMiner():
    def_config = configMiner["DEFAULT"]
    def_config["miner_addr"] = minerAddr
    def_config["serial_ports"] = serialPorts
    try:
        with open(configMinerName, 'w') as configfile:
            configMiner.write(configfile)
    except:
        print("error write config file") 

def miner( ith, s_port ):
  global results_good
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
    print("Connecting serial", s_port)
    try:
        ser = serial.Serial(f"{s_port}", baudrate=115200, timeout=2.5)
        time.sleep(2)
        serial_connected = True
        print("Serial connetecd")
    except:
        print("Serial error")
        break
    
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

if __name__ == '__main__':
	#Read config
    readConfigMiner()
    
    #Get SiriCoin address
    if ( minerAddr == "" ):
        minerAddr = input(f"{Fore.YELLOW}Enter SiriCoin address: {Fore.WHITE}")
    else:
        print(f"{Fore.YELLOW}SiriCoin address:{Fore.WHITE}", minerAddr )
        t_minerAddr = input(f"{Fore.YELLOW}Enter new SiriCoin address or ENTER to continue: {Fore.WHITE}")
        if (t_minerAddr != ""):
            minerAddr = t_minerAddr
    
    #Get list of serial ports
    if ( serialPorts == "" ):
        serialPorts = input(f"{Fore.YELLOW}Enter list serial ports: {Fore.WHITE}")
    else:
        print(f"{Fore.YELLOW}List serial ports:{Fore.WHITE}", serialPorts )
        t_serialPorts = input(f"{Fore.YELLOW}Enter new list serial ports or ENTER to continue: {Fore.WHITE}")
        if (t_serialPorts != ""):
            serialPorts = t_serialPorts
    
    #Write config
    writeConfigMiner()
    
    listPorts = serialPorts.split(',')
    real_ports = list()
    for port in listPorts:
        if os.path.exists(port):
            real_ports.append(port)
    #Threads
    index = 0
    for port in real_ports:
      Thread(target=miner, args=(index, port)).start()
      index += 1
