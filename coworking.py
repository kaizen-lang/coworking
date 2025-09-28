"""Script de coworking"""
import random
import datetime as dt
#Utilidades que se utilizarán en todo el código.
def generar_id()->int:
    """Genera un ID aleatorio de 7 carácteres.

    Returns:
        int: ID generado
    """
    caracteres = tuple("qwertyuiopasdfghjklzxcvbnm123456789")
    generacion = [random.choice(caracteres) for x in range(7)]
    id_generado = "".join(generacion)
    return id_generado

class ManejarReservaciones:
    lista = {
        "ejemploreserva": {
            "id_cliente":"ejemplo123",
            "fecha":"12/02/2025",
            "turno":"Matutino"
        }
    }
    turnos = ("Matutino", "Vespertino", "Nocturno")

    def __init__(self):
        pass

    def registrar_reservación(self, id_cliente:int, fecha, turno:str):
        folio = generar_id

        self.lista[folio] = {
            "id_cliente":id_cliente,
            "fecha":fecha,
            "turno":turno
        }

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
        self.lista[id_sala] = {"Nombre":nombre.strip, "Cupo":cupo}
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
        id_cliente = generar_id()
        self.lista[id_cliente] = {"Nombre":nombre.strip(), "Apellidos":apellidos.strip()}
        print(f"Cliente registrado satisfactoriamente con el ID: {id_cliente}")

    def mostrar_clientes(self):
        #Ordenamos por apellidos
        #El lambda hace que se tome en cuenta los apellidos como criterio para ordenar.
        ordenado = dict(sorted(self.lista.items(), key=lambda item: item[1]["Apellidos"]))

        for id_cliente, datos in ordenado.items():
            nombre, apellidos = datos.values()
            print(f"ID: {id_cliente}, Nombre: {nombre}, Apellidos: {apellidos}")

class Coworking:

    clientes = ManejarClientes()
    salas = ManejarSalas()

    def __init__(self):
        #TODO: Esto servirá para después.
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
                            fecha = dt.datetime.strptime(input("Escriba la fecha (dd/mm/aaaa): "), "%d/%m/&Y")
                        except ValueError:
                            print("Formato no válido. Por favor, escríbalo de nuevo usando el formato correcto.")




                case 2:
                    self.clientes.mostrar_clientes()
                case 3:
                    pass
                case 4:
                    print("Ha escogido la opción: Registrar a un nuevo cliente.")
                    try:
                        nombre = input("Escriba su nombre: ")
                        apellidos = input("Escriba sus apellidos: ")
                        self.clientes.registrar_cliente(nombre, apellidos)
                    except Exception:
                        pass
                case 5:
                    print("Ha escogido la opción: registrar nueva sala")
                    try:
                        nombre_sala = input("Escriba el nombre de la sala: ")
                        cupo = int(input("Escriba el cupo de la sala: "))
                        self.salas.registrar_sala(nombre_sala, cupo)
                    except Exception:
                        pass
                case 6:
                    break

if __name__ == "__main__":
    programa = Coworking()
    programa.mostrar_menu()
