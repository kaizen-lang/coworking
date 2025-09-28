"""Script de coworking"""

import random
import datetime as dt
#Utilidades que se utilizarán en todo el código.
def generar_id()->int:
    """Genera un ID aleatorio de 7 carácteres.

    Returns:
        int: ID generado
    """
    #Generamos una tupla con carácteres, los cuales usaremos para generar el ID.
    caracteres = tuple("qwertyuiopasdfghjklzxcvbnm123456789")

    #Se escoge un carácter aleatorio 7 veces.
    generacion = [random.choice(caracteres) for x in range(7)]

    id_generado = "".join(generacion) #Unimos la lista generada en un string.

    return id_generado

class ManejarReservaciones:
#TODO: Sistema de reservaciones. Buscar por fecha, etc.
    lista = {
        "ejemploreserva": {
            "id_cliente":"ejemplo123",
            "fecha":dt.date(2025,10,1), #Resultado del strptime, se puede convertir de nuevo en string después. Objeto date.
            "turno":"Matutino",
            "id_sala":"ejemplosala1"
        }
    }
    turnos = ("Matutino", "Vespertino", "Nocturno")

    def __init__(self):
        pass

    def registrar_reservacion(self, id_cliente:int, fecha, turno:str, id_sala:str, nombre_evento:str):
        folio = generar_id()

        self.lista[folio] = {
            "id_cliente":id_cliente,
            "fecha":fecha,
            "turno":turno,
            "id_sala":id_sala,
            "nombre_evento":nombre_evento
        }

        print(f"Evento registrado de manera exitosa con el folio: {folio}")

    #FUNCIÓN MOSTRAR RESERVACIONES -> CICLAR EL DICCIONARIO, REALIZAR COMPROBACIÓN (¿HA SIDO RESERVADO?), MOSTRAR SALAS NO RESERVADAS
    def mostrar_salas_disponibles(self, lista_salas, fecha):
        #TODO: Registro tabular

        for id_sala, datos_sala in lista_salas.items():
            nombre, cupo = datos_sala.values()
            for reservacion in self.lista.values(): #Iteramos por cada reservación para realizar el filtro
                fecha_reservacion, turno_reservacion = reservacion["fecha"], reservacion["turno"]
                for turno_disponible in self.turnos:
                    if (fecha_reservacion == fecha) and (turno_reservacion != turno_disponible):
                        print(f"Fecha: {fecha}, Sala: {nombre}, Cupo: {cupo}, Turno: {turno_disponible}, ID sala: {id_sala}")

    def verificar_disponibilidad(self, fecha, id_sala, turno):
        for reservacion in self.lista.values(): #Iteramos por cada reservación para realizar el filtro
            fecha_reservacion, turno_reservacion, id_sala_reservada = reservacion["fecha"], reservacion["turno"], reservacion["id_sala"]
            if (fecha_reservacion == fecha) and (turno_reservacion == turno.capitalize()) and (id_sala_reservada == id_sala):
                return False
        return True

class ManejarSalas:
    lista = {
        "ejemplosala1": {
            "Nombre":"Salauno",
            "Cupo":20
        }
    }

    def __init__(self):
        pass

    def registrar_sala(self, nombre:str, cupo:int):
        id_sala = generar_id()
        self.lista[id_sala] = {"Nombre":nombre.strip(), "Cupo":cupo}
        print(f"Sala registrada exitosamente con el ID: {id_sala}")


class ManejarClientes:
    lista = {
        "ejemplo123": {
            "Nombre":"Manuel",
            "Apellidos":"Garza"
        }
    }

    def __init__(self):
        pass

    def registrar_cliente(self, nombre:str, apellidos:str):
        #TODO: Añadir validaciones

        if not nombre.strip() or not apellidos.strip():
            print("Error, el nombre y apellidos no pueden estar vacios")
            return
        id_cliente = generar_id()
        self.lista[id_cliente] = {"Nombre":nombre.strip(), "Apellidos":apellidos.strip()}
        print(f"Cliente registrado satisfactoriamente con el ID: {id_cliente}")

    def mostrar_clientes(self):
        #Ordenamos por apellidos
        #El lambda hace que se tome en cuenta los apellidos como criterio para ordenar.
        #TODO: Registro Tabular
        ordenado = dict(sorted(self.lista.items(), key=lambda item: item[1]["Apellidos"]))

        for id_cliente, datos in ordenado.items():
            nombre, apellidos = datos.values()
            print(f"ID: {id_cliente}, Nombre: {nombre}, Apellidos: {apellidos}")

class Coworking:
    clientes = ManejarClientes()
    salas = ManejarSalas()
    reservaciones = ManejarReservaciones()

    def __init__(self):
        #TODO: Esto servirá para después, en caso de que queramos pasar una lista ya hecha.
        #self.clientes = clientes
        #self.salas = salas
        pass

    def mostrar_menu(self):
        opcion = 0
        while True:
            print("Bienvenido al programa del coworking.")
            print("Opciones disponibles:")
            print("(1) - Registrar reservación de sala")
            print("(2) - Editar el nombre de una reservación ya hecha")
            print("(3) - Consultar reservaciones de una fecha específica")
            print("(4) - Registrar a un nuevo cliente")
            print("(5) - Registrar una sala")
            print("(6) - Salir del programa")

            while True:
                try:
                    opcion = int(input("Escribe el número de la opción que vas a escoger: "))
                except ValueError:
                    print("ERROR: Escribe un número válido.")
                    continue
                else:
                    break

            match opcion:
                case 1:
                    print("Ha escogido la opción: Registrar reservación de sala")

                    while True:
                        #TODO: Validaciones
                        self.clientes.mostrar_clientes()
                        id_cliente = input("Escriba su ID de cliente: ")

                        if id_cliente not in self.clientes.lista:
                            print("Por favor escriba un ID válido.")
                            continuar = input("¿Quiere cancelar la operación? Escriba S para salir o cualquier tecla para continuar: ")
                            if continuar.upper() == "S":
                                break
                            continue #Lo mandamos de nuevo al ciclo
                        break

                    while True:
                        try:
                            fecha = dt.datetime.strptime(input("Escriba la fecha (dd/mm/aaaa): "), "%d/%m/%Y").date()
                            break
                        except ValueError:
                            print("Formato no válido. Por favor, escríbalo de nuevo usando el formato correcto.")

                    #Validando si la reservación es mínimo dos días posteriores al día actual
                    fecha_minima = dt.date.today() + dt.timedelta(days=2)

                    if fecha < fecha_minima:
                        print("La reservación debe ser por lo menos con dos días de anticipación.")
                        raise ValueError("Fecha no válida")

                    while True:
                        self.reservaciones.mostrar_salas_disponibles(self.salas.lista, fecha)
                        id_sala = input("Escriba el ID de la sala a escoger: ")
                        turno = input("Escriba el turno a escoger: ")
                        if self.reservaciones.verificar_disponibilidad(fecha, id_sala, turno):
                            print("Hay disponibilidad")
                            break
                        print("No hay disponibilidad")

                    while True:
                        nombre_evento = input("Escriba el nombre del evento: ")
                        if nombre_evento.strip() == "":
                            print("Escriba un nombre válido.")
                            continue
                        break

                    self.reservaciones.registrar_reservacion(id_cliente, fecha, turno.capitalize(), id_sala, nombre_evento)

                case 2:
                    pass

                case 3:
                    pass

                case 4:
                    print("Ha escogido la opción: Registrar a un nuevo cliente.")
                    while True:
                        nombre = input("Escriba su nombre: ")
                        if nombre.strip == "":
                            print("Error: el nombre no puede estar vacío.")
                            continue

                        apellidos = input("Escriba sus apellidos: ")
                        if apellidos.strip() == "":
                            print("Error: los apellidos no pueden estar vacíos.")
                            continue

                        self.clientes.registrar_cliente(nombre, apellidos)
                        break

                case 5:
                    print("Ha escogido la opción: registrar nueva sala")
                    while True:
                        try:
                            nombre_sala = input("Escriba el nombre de la sala: ")

                            if nombre_sala.strip() == "":
                                print("Error, el nombre de la sala no puede estar vacio.")
                                continue

                            cupo = int(input("Escriba el cupo de la sala: "))
                            if cupo <= 0:
                                print("Error, el cupo debe ser mayor a 0.")
                                continue

                            self.salas.registrar_sala(nombre_sala, cupo)

                            break
                        except ValueError:
                            print("Valor inválido")
                            continue
                case 6:
                    break

if __name__ == "__main__":
    programa = Coworking()
    programa.mostrar_menu()
