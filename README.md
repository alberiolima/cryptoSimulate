-=- PT-BR
Essa é a versão inicial para o desenvolvimento de um pool para mineradores IOT

minerSiriArduino (dispositivo IOT)
Esse é o código para Arduino, no qual será resolvido o algoritimo keccak, ele se comunica com o PC miner pela porta serial-usb

SiriCoinSerialMinerIOT (PC miner)
Essa aplicação roda no computador do minerador, ele será responsável pela comunicação entre o dispositivo IOT e o POOL, ele se comunica com o POOL por TCP e com o dispositivo IOT pela porta serial

SiriCoinPoolIOT (POOL)
Essa aplicação roda no servidor, ele será responsável por enviar os trabalhos para o o PC miner,ele se comunica com o PC miner por TCP

-=- EN
This is the initial version for the development of a pool for IOT miners

minerSiriArduino (IoT device)
This is the code for Arduino, in which the keccak algorithm will be solved, it communicates with the PC miner through the serial-usb port

SiriCoinSerialMinerIOT (PC miner)
This application runs on the miner's computer, it will be responsible for the communication between the IOT device and the POOL, it communicates with the POOL by TCP and with the IOT device by the serial port

SiriCoinPoolIOT (POOL)
This application runs on the server, it will be responsible for sending the jobs to the PC miner, it communicates with the PC miner by TCP
# cryptoSimulate
