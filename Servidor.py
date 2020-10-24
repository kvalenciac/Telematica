import socket
import threading
import sys
import pickle
import os
import shutil

class Servidor():

  def __init__(self, host='localhost', port=4000):
    self.crearBucket('Clientes')
    self.clientes = []

    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.bind((host, port))
    self.socket.listen(10)
    self.socket.setblocking(False)

    aceptar = threading.Thread(target=self.aceptar_conexion)
    procesar = threading.Thread(target=self.procesar_conexion)

    aceptar.daemon = True
    procesar.daemon = True

    aceptar.start()
    procesar.start()

    while True:
      msg = input('>')
      if msg == 'exit':
        self.socket.close()
        sys.exit()

  def ejecutar(self, data, clienteActual):
    for cliente in self.clientes:
      try:
        if cliente[0] == clienteActual[0]:
          if data[0] == 'ls':
            path = f'clientes/{clienteActual[1][1]}/{data[1] if len(data) > 1 else ""}'
            self.send_msg(clienteActual[0], self.list(path))
          elif data[0] == 'crear':
            if len(data) > 1:
              if data[1] not in self.list('clientes/'):
                self.crearBucket(f'clientes/{clienteActual[1][1]}/{data[1]}')
                self.send_msg(clienteActual[0], f'{data[1]} creado')
              else:
                self.send_msg(clienteActual[0], f'{data[1]} ya existe')
            else:
              self.send_msg(clienteActual[0], "No se puede crear un Bucket sin nombre")
          elif data[0] == 'delete':
            if len(data) > 1:
              self.deleteBucket(f'clientes/{clienteActual[1][1]}/{data[1]}')
              self.send_msg(clienteActual[0], f'{data[1]} eliminado')
            else:
              self.send_msg(clienteActual[0], "No se puede eliminar un Bucket sin un nombre")
          elif data[0] == 'cargar':
            with open(f'clientes/{clienteActual[1][1]}/{data[1]}/{data[3]["name"]}.KVC', 'wb') as file:
              pickle.dump(data[3], file)
              self.send_msg(clienteActual[0], f'{data[3]["name"]} cargado')
          elif data[0] == 'descargar':
            with open(f'clientes/{clienteActual[1][1]}/{data[1]}.KVC', 'rb') as file:
              file_data = pickle.load(file)
              self.send_msg(clienteActual[0], dict(file_data))
          elif data[0] == 'eliminar':
            self.eliminarArchivo(f'{self.pwd()}/clientes/{clienteActual[1][1]}/{data[1]}.KVC'.replace('/', '\\'))
            self.send_msg(clienteActual[0], 'Archivo eliminado')
        else:
          continue
      except:
        pass

  def send_msg(self, client, message):
    client.send(pickle.dumps(message))

  def aceptar_conexion(self):
    print('Aceptando Conexión...')
    while True:
      try:
        conn, address = self.socket.accept()
        conn.setblocking(False)
        self.crearBucket(f'clientes/{address[1]}')
        self.clientes.append((conn, address))
      except:
        pass

  def procesar_conexion(self):
    print('Procesando la conexión...')
    while True:
      if len(self.clientes) > 0:
        for client in self.clientes:
          try:
            data = pickle.loads(client[0].recv(1024))
            self.ejecutar(data, client) if data != None else None
          except:
            pass

  def list(self, address):
    try:
      lt = os.listdir(address)
      for i in range(len(lt)):
        lt[i] = lt[i].replace('.KVC', '')
      return lt
    except OSError as OSe:
      print(f'Error: {OSe.filename} - {OSe.strerror}')
      return False
  
  def crearBucket(self, name):
    try:
      os.mkdir(name)
      return True
    except OSError as OSe:
      return OSe.filename, OSe.strerror

  def eliminarArchivo(self, fileName):
    try:
      os.remove(fileName)
      return True
    except OSError as OSe:
      print(f'Error: {OSe.filename} - {OSe.strerror}')
      return False

  def deleteBucket(self, bucketName):
    try:
      shutil.rmtree(bucketName)
      return True
    except OSError as OSe:
      print(f'Error: {OSe.filename} - {OSe.strerror}')

  def pwd(self):
    return os.getcwd()

s = Servidor()