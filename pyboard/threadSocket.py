'''
Clases para encapsular la recepción de mensajes a través de un 
puerto en localhost
'''

import socket

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)


import threading

import asyncio
import websockets
import time
import json

class ThreadSocket(threading.Thread):
    def __init__(self, threadID, name, host=HOST, port = PORT, cbkfunction=None):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.host = host
        self.port = port
        self.cbkfunction = cbkfunction
        self._parar=False
        self.loop=None

#    @property
#    def parar(self):
#        return self._parar
    
    
    
    def run(self):

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        async def consumer_handler(websocket, path):
            async for message in websocket:
                print('message...')
                data = json.loads(message)
                if self.cbkfunction != None:
                    if '@t' in data['msg'][-1]:
                        cmd = data['msg'][-1].replace('@t','')
                        try:
                            print("cmd:",cmd.strip())
                            self.cbkfunction(cmd.strip())
                        except:
                            print(" Imposible ejecutar:", cmd)


        #%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #%%% Función para detener
        
        def pararServidor():

            print("Inicia a cerrar")
            self.server.close()
            self.loop.stop()
            # Tareas pendientes
            #pending = asyncio.Task.all_tasks()
            
            # Run loop until tasks done:
            #self.loop.run_until_complete(asyncio.gather(*pending))

            print("Shutdown complete ...")    
            #self.loop.run_until_complete(self.server.wait_closed())
            
        self.parar = pararServidor
        self.ws_server=websockets.serve(consumer_handler, self.host, self.port)
        #asyncio.get_event_loop().run_until_complete(self.ws_server)
        #print("Server init")
        #asyncio.get_event_loop().run_forever()
        self.loop = asyncio.get_event_loop()
        if self.loop.is_running():
            self.loop.stop()
        
        
        self.server = self.loop.run_until_complete(self.ws_server)
        print("Server init")
        
        self.loop.run_forever()
        print ("Saliendo " + self.name)
        
    
#    async def parar(self):
#        self._parar=True
#        try:
#            await self.close()
#        except:
#            print("No se pudo cerrar")

#    async def close(self):
#        self.server.close()
#        self.loop.run_until_complete(self.server.wait_closed())
#        self.loop.stop()


