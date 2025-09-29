
"""Script de coworking"""

import random
import datetime as dt

#Utilidades que se utilizarán en todo el código.
def generar_id() -> str:
    """Genera un ID aleatorio de 7 carácteres.

    Returns:
        str: ID generado
    """
    #Generamos una tupla con carácteres, los cuales usaremos para generar el ID.
    caracteres = tuple("qwertyuiopasdfghjklzxcvbnm123456789")

    #Se escoge un carácter aleatorio 7 veces.
    generacion = [random.choice(caracteres) for x in range(7)]

    id_generado = "".join(generacion)  #Unimos la lista generada en un string.

    return id_generado

class ManejarReservaciones:
    #Sistema de reservaciones, buscar por fecha, etc.
    lista = {
        "ejemploreserva": {
            "id_cliente": "ejemplo123",
            "fecha": dt.date(2025, 10, 1),  #Resultado del strptime, se puede convertir de nuevo en string después. Objeto date.
            "turno": "Matutino",
            "id_sala": "ejemplosala1",
            "nombre_evento": "Ejemplo Evento"
        }
    }
    turnos = ("Matutino", "Vespertino", "Nocturno")

    def __init__(self):
        pass

    def registrar_reservacion(self, id_cliente: str, fecha, turno: str, id_sala: str, nombre_evento: str):
        folio = generar_id()

        self.lista[folio] = {
            "id_cliente": id_cliente,
            "fecha": fecha,
            "turno": turno,
            "id_sala": id_sala,
            "nombre_evento": nombre_evento
        }

        print(f"Evento registrado de manera exitosa con el folio: {folio}")

    def mostrar_salas_disponibles(self, lista_salas: dict, fecha):
        #Mostrar las salas con turnos disponibles en formato tabular
        print(f"\nSalas disponibles para la fecha {fecha}:")
        print(f"{'ID Sala':<15} {'Nombre':<20} {'Cupo':<10} {'Turnos Disponibles':<15}")
        print("-" * 60)

        salas_disponibles = False
        for id_sala, datos_sala in lista_salas.items():
            nombre, cupo = datos_sala["Nombre"], datos_sala["Cupo"]
            turnos_disponibles = [turno for turno in self.turnos if self.verificar_disponibilidad(fecha, id_sala, turno)]
            if turnos_disponibles:
                salas_disponibles = True
                print(f"{id_sala:<15} {nombre:<20} {cupo:<10} {', '.join(turnos_disponibles):<15}")

        if not salas_disponibles:
            print("No hay salas ni turnos disponibles para esta fecha.")
            return False
        return True

    def verificar_disponibilidad(self, fecha, id_sala, turno):
        for reservacion in self.lista.values():  #Iteramos por cada reservación para realizar el filtro
            fecha_reservacion, turno_reservacion, id_sala_reservada = reservacion["fecha"], reservacion["turno"], reservacion["id_sala"]
            if (fecha_reservacion == fecha) and (turno_reservacion == turno) and (id_sala_reservada == id_sala):
                return False
        return True

    def mostrar_reservaciones_por_fecha(self, fecha):
        #Mostrar en formato tabular
        print(f"\nReporte de reservaciones para la fecha {fecha}:")
        print(f"{'Sala':<15} {'Cliente':<20} {'Evento':<30} {'Turno':<15}")
        print("-" * 80)

        encontrados = False
        for folio, datos in self.lista.items():
            if datos["fecha"] == fecha:
                encontrados = True
                sala_nombre = Coworking.salas.lista.get(datos["id_sala"], {"Nombre": "Desconocida"})["Nombre"]
                cliente_datos = Coworking.clientes.lista.get(datos["id_cliente"], {"Nombre": "Desconocido", "Apellidos": ""})
                cliente = f"{cliente_datos['Nombre']} {cliente_datos['Apellidos']}"
                print(f"{sala_nombre:<15} {cliente:<20} {datos['nombre_evento']:<30} {datos['turno']:<15}")

        if not encontrados:
            print("No hay reservaciones para esta fecha.")

    def mostrar_reservaciones_en_rango(self, fecha_inicio, fecha_fin):
        #Mostrar en formato tabular: folio, nombre evento, fecha
        print(f"\nEventos en el rango de fechas {fecha_inicio} a {fecha_fin}:")
        print(f"{'Folio':<15} {'Nombre Evento':<30} {'Fecha':<15}")
        print("-" * 60)

        lista_eventos = []
        for folio, datos in self.lista.items():
            if fecha_inicio <= datos["fecha"] <= fecha_fin:
                lista_eventos.append((folio, datos["nombre_evento"], datos["fecha"]))

        #Ordenar por fecha usando lambda: extrae el tercer elemento (fecha) de cada tupla para comparación
        lista_eventos.sort(key=lambda x: x[2])  #Aquí el lambda recibe 'x' (tupla) y retorna x[2] (fecha) como clave del sort

        for folio, evento, fecha in lista_eventos:
            print(f"{folio:<15} {evento:<30} {fecha.strftime('%d-%m-%Y'):<15}")

        #Retorna lista de folios válidos usando list comprehension: extrae solo el primer elemento (folio) de cada tupla, ignorando los otros con '_'
        return [folio for folio, _, _ in lista_eventos]  #Esto genera una lista plana de folios para validaciones en edición

    def editar_nombre_evento(self, folio: str, nuevo_nombre: str):
        if folio in self.lista:
            self.lista[folio]["nombre_evento"] = nuevo_nombre
            print(f"Nombre del evento actualizado exitosamente para el folio {folio}.")
        else:
            print("Folio no encontrado.")

class ManejarSalas:
    lista = {
        "ejemplosala1": {
            "Nombre": "Salauno",
            "Cupo": 20
        }
    }

    def __init__(self):
        pass

    def registrar_sala(self, nombre: str, cupo: int):
        id_sala = generar_id()
        self.lista[id_sala] = {"Nombre": nombre.strip(), "Cupo": cupo}
        print(f"Sala registrada exitosamente con el ID: {id_sala}")

class ManejarClientes:
    lista = {
        "ejemplo123": {
            "Nombre": "Manuel",
            "Apellidos": "Garza"
        }
    }

    def __init__(self):
        pass

    def registrar_cliente(self, nombre: str, apellidos: str) -> bool:
        #Añadir las validaciones
        nombre = nombre.strip()
        apellidos = apellidos.strip()

        if not nombre or not apellidos:
            print("Error, el nombre y apellidos no pueden estar vacios")
            return False

        if not nombre.replace(" ", "").isalpha() or not apellidos.replace(" ", "").isalpha():
            print("Error, el nombre y apellidos deben contener solo caracteres alfabéticos y espacios.")
            return False

        if len(nombre) < 2 or len(nombre) > 50 or len(apellidos) < 2 or len(apellidos) > 50:
            print("Error, el nombre y apellidos deben tener entre 2 y 50 caracteres.")
            return False

        id_cliente = generar_id()
        self.lista[id_cliente] = {"Nombre": nombre, "Apellidos": apellidos}
        print(f"Cliente registrado satisfactoriamente con el ID: {id_cliente}")
        return True

    def mostrar_clientes(self):
        #Ordenamos por apellidos y luego por nombres
        #El lambda hace que se tome en cuenta los apellidos y nombres como criterio para ordenar.
        ordenado = dict(sorted(self.lista.items(), key=lambda item: (item[1]["Apellidos"], item[1]["Nombre"])))

        #Registro tabular
        print("\nListado de clientes registrados:")
        print(f"{'ID':<15} {'Nombre':<20} {'Apellidos':<20}")
        print("-" * 55)

        for id_cliente, datos in ordenado.items():
            nombre, apellidos = datos.values()
            print(f"{id_cliente:<15} {nombre:<20} {apellidos:<20}")

class Coworking:
    clientes = ManejarClientes()
    salas = ManejarSalas()
    reservaciones = ManejarReservaciones()

    def __init__(self):
        #Esto servirá para después, en caso de que queramos pasar una lista ya hecha.
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
                    if opcion < 1 or opcion > 6:
                        print("ERROR: Opción no válida. Escoge entre 1 y 6.")
                        continue
                except ValueError:
                    print("ERROR: Escribe un número válido.")
                    continue
                else:
                    break

            match opcion:
                case 1:
                    print("Ha escogido la opción: Registrar reservación de sala")

                    id_cliente = None
                    while True:
                        #Validaciones
                        self.clientes.mostrar_clientes()
                        id_cliente = input("Escriba su ID de cliente: ")

                        if id_cliente not in self.clientes.lista:
                            print("Por favor escriba un ID válido.")
                            continuar = input("¿Quiere cancelar la operación? Escriba S para salir o cualquier tecla para continuar: ")
                            if continuar.upper() == "S":
                                break
                            continue  #Lo mandamos de nuevo al ciclo
                        break

                    if id_cliente not in self.clientes.lista:
                        continue  #Se cancela para regresar al menú principal

                    while True:
                        try:
                            fecha_str = input("Escriba la fecha (dd/mm/aaaa): ")
                            fecha = dt.datetime.strptime(fecha_str, "%d/%m/%Y").date()
                            break
                        except ValueError:
                            print("Formato no válido. Por favor, escríbalo de nuevo usando el formato correcto.")

                    #Validando si la reservación es mínimo dos días posteriores al día actual
                    fecha_minima = dt.date.today() + dt.timedelta(days=2)

                    if fecha < fecha_minima:
                        print("La reservación debe ser por lo menos con dos días de anticipación.")
                        continue

                    while True:
                        self.reservaciones.mostrar_salas_disponibles(self.salas.lista, fecha)
                        id_sala = input("Escriba el ID de la sala a escoger: ")

                        if id_sala not in self.salas.lista:
                            print("ID de sala no válido.")
                            continue

                        turno = input("Escriba el turno a escoger (Matutino, Vespertino, Nocturno): ").capitalize()

                        if turno not in self.reservaciones.turnos:
                            print("Turno no válido.")
                            continue

                        if self.reservaciones.verificar_disponibilidad(fecha, id_sala, turno):
                            print("Hay disponibilidad")
                            break
                        print("No hay disponibilidad en ese turno para esta sala.")

                    while True:
                        nombre_evento = input("Escriba el nombre del evento: ").strip()
                        if not nombre_evento or len(nombre_evento) < 3:
                            print("Escriba un nombre válido (mínimo 3 caracteres).")
                            continue
                        break

                    self.reservaciones.registrar_reservacion(id_cliente, fecha, turno, id_sala, nombre_evento)

                case 2:
                    print("Ha escogido la opción: Editar el nombre de una reservación ya hecha")

                    while True:
                        try:
                            fecha_inicio_str = input("Escriba la fecha de inicio del rango (dd/mm/aaaa): ")
                            fecha_inicio = dt.datetime.strptime(fecha_inicio_str, "%d/%m/%Y").date()
                            fecha_fin_str = input("Escriba la fecha de fin del rango (dd/mm/aaaa): ")
                            fecha_fin = dt.datetime.strptime(fecha_fin_str, "%d/%m/%Y").date()
                            if fecha_inicio > fecha_fin:
                                print("La fecha de inicio no puede ser posterior a la de fin.")
                                continue
                            break
                        except ValueError:
                            print("Formato no válido. Por favor, escríbalo de nuevo usando el formato correcto.")

                    folios_validos = self.reservaciones.mostrar_reservaciones_en_rango(fecha_inicio, fecha_fin)

                    if not folios_validos:
                        print("No hay eventos en este rango de fechas.")
                        continue

                    folio = None
                    while True:
                        folio = input("Escriba el folio del evento a modificar: ")
                        if folio not in folios_validos:
                            print("Folio no válido en este rango. Por favor, seleccione uno de la lista.")
                            continuar = input("¿Quiere cancelar la operación? Escriba S para salir o cualquier tecla para continuar: ")
                            if continuar.upper() == "S":
                                break
                            continue
                        break

                    if folio not in folios_validos:
                        continue  # Cancelado, volver al menú principal

                    while True:
                        nuevo_nombre = input("Escriba el nuevo nombre del evento: ").strip()
                        if not nuevo_nombre or len(nuevo_nombre) < 3:
                            print("Escriba un nombre válido (mínimo 3 caracteres).")
                            continue
                        break

                    self.reservaciones.editar_nombre_evento(folio, nuevo_nombre)

                case 3:
                    print("Ha escogido la opción: Consultar reservaciones de una fecha específica")

                    while True:
                        try:
                            fecha_str = input("Escriba la fecha a consultar (dd/mm/aaaa): ")
                            fecha = dt.datetime.strptime(fecha_str, "%d/%m/%Y").date()
                            break
                        except ValueError:
                            print("Formato no válido. Por favor, escríbalo de nuevo usando el formato correcto.")

                    self.reservaciones.mostrar_reservaciones_por_fecha(fecha)

                case 4:
                    print("Ha escogido la opción: Registrar a un nuevo cliente.")
                    while True:
                        nombre = input("Escriba su nombre: ")
                        apellidos = input("Escriba sus apellidos: ")
                        if self.clientes.registrar_cliente(nombre, apellidos):
                            break

                case 5:
                    print("Ha escogido la opción: registrar nueva sala")
                    while True:
                        try:
                            nombre_sala = input("Escriba el nombre de la sala: ")

                            if nombre_sala.strip() == "" or len(nombre_sala.strip()) < 2:
                                print("Error, el nombre de la sala no puede estar vacio o tener menos de 2 caracteres.")
                                continue

                            cupo = int(input("Escriba el cupo de la sala: "))
                            if cupo <= 0 or cupo > 1000:
                                print("Error, el cupo debe ser un número positivo entre 1 y 1000.")
                                continue

                            self.salas.registrar_sala(nombre_sala, cupo)

                            break
                        except ValueError:
                            print("Valor inválido")

                case 6:
                    print("Saliendo del programa...")
                    break

if __name__ == "__main__":
    programa = Coworking()
    programa.mostrar_menu()
