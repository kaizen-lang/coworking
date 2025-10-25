"""Script de coworking."""

import datetime as dt
import json
import csv
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side

import sqlite3
import os

def inicializar_base_datos():
    """Crea coworking.db y las tablas básicas si no existen."""
    with sqlite3.connect("coworking.db") as conn:
        cursor = conn.cursor()


        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id_cliente INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                apellidos TEXT NOT NULL
            );
        """)


        cursor.execute("""
            CREATE TABLE IF NOT EXISTS salas (
                id_sala INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                cupo INTEGER NOT NULL
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservaciones (
                folio INTEGER PRIMARY KEY,
                id_cliente INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                turno TEXT NOT NULL,
                id_sala INTEGER NOT NULL,
                nombre_evento TEXT NOT NULL,
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
                FOREIGN KEY (id_sala) REFERENCES salas(id_sala)
            );
        """)

class ManejarReservaciones:
    """Clase para manejar reservaciones."""

    def __init__(self):
        self.lista = self._load_from_db()
        self.turnos = ("Matutino", "Vespertino", "Nocturno")

    def _load_from_db(self) -> dict:
        """Carga las reservaciones desde la base de datos."""
        lista = {}
        with sqlite3.connect("coworking.db") as conn:
            c = conn.cursor()
            c.execute("SELECT folio, id_cliente, fecha, turno, id_sala, nombre_evento FROM reservaciones ORDER BY folio")
            for row in c.fetchall():
                folio, id_c, fecha_str, turno, id_s, nom_ev = row
                fecha = dt.datetime.strptime(fecha_str, '%m-%d-%Y').date()
                lista[str(folio)] = {
                    "id_cliente": str(id_c),
                    "fecha": fecha,
                    "turno": turno,
                    "id_sala": str(id_s),
                    "nombre_evento": nom_ev
                }
        return lista

    def registrar_reservacion(self, id_cliente: str, fecha: dt.date, turno: str, id_sala: str, nombre_evento: str) -> None:
        """Registra una reservación nueva en la base de datos y en la lista local.

        Args:
            id_cliente (str): ID del cliente que hace la reservación.
            fecha (dt.date): Fecha de la reservación.
            turno (str): Turno de la reservación.
            id_sala (str): ID de la sala a reservar.
            nombre_evento (str): Nombre del evento a realizar.
        """
        fecha_str = fecha.strftime('%m-%d-%Y')
        with sqlite3.connect("coworking.db") as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO reservaciones (id_cliente, fecha, turno, id_sala, nombre_evento)
                VALUES (?, ?, ?, ?, ?)
            """, (int(id_cliente), fecha_str, turno, int(id_sala), nombre_evento))
            folio = c.lastrowid
        self.lista[str(folio)] = {
            "id_cliente": id_cliente,
            "fecha": fecha,
            "turno": turno,
            "id_sala": id_sala,
            "nombre_evento": nombre_evento
        }
        print(f"Evento registrado de manera exitosa con el folio: {folio}")

    def mostrar_salas_disponibles(self, lista_salas: dict, fecha:dt.date)->bool:
        """Muestra las salas disponibles en formato tabular.

        Args:
            lista_salas (dict): Lista que contiene las salas registradas.
            fecha (dt.date): Fecha a consultar.

        Returns:
            bool: True si hay salas disponibles, False si no las hay.
        """

        print(f"\nSalas disponibles para la fecha {fecha.strftime('%m-%d-%Y')}:")
        print(f"{'ID Sala':<15} {'Nombre':<20} {'Cupo':<10} {'Turnos Disponibles':<30}")
        print("-" * 75)

        salas_disponibles = False
        for id_sala, datos_sala in lista_salas.items():

            nombre, cupo = datos_sala["Nombre"], datos_sala["Cupo"]
            turnos_disponibles = [turno for turno in self.turnos if self.verificar_disponibilidad(fecha, id_sala, turno)]

            if turnos_disponibles:
                salas_disponibles = True
                print(f"{id_sala:<15} {nombre:<20} {cupo:<10} {', '.join(turnos_disponibles):<30}")

        if not salas_disponibles:
            print("No hay salas ni turnos disponibles para esta fecha.")
            return False

        return True

    def verificar_disponibilidad(self, fecha: dt.date, id_sala: str, turno: str)->bool:
        """Verifica si una sala está disponible en una fecha, sala y turno específicos.

        Args:
            fecha (date): Fecha a consultar.
            id_sala (str): ID de la sala a consultar.
            turno (str): Turno a consultar.

        Returns:
            bool: True si está disponible, False si no lo está.
        """

        fecha_str = fecha.strftime('%m-%d-%Y')
        with sqlite3.connect("coworking.db") as conn:
            c = conn.cursor()
            c.execute("""
                SELECT 1 FROM reservaciones
                WHERE fecha = ? AND id_sala = ? AND turno = ?
                LIMIT 1
            """, (fecha_str, int(id_sala), turno))
            return c.fetchone() is None

    def mostrar_reservaciones_por_fecha(self, fecha: dt.date, lista_salas: dict, lista_clientes: dict) -> bool:
        """Muestra las reservaciones por fecha en formato tabular.

        Args:
            fecha (dt.date): Fecha a consultar.
            lista_salas (dict): Lista con las salas disponibles.
            lista_clientes (dict): Lista con los clientes registrados.

        Returns:
            bool: True si se encontraron reservaciones, False si no.
        """

        print(f"\nReporte de reservaciones para la fecha {fecha.strftime('%m-%d-%Y')}:")
        print(f"{'Sala':<15} {'Cliente':<20} {'Evento':<30} {'Turno':<15}")
        print("-" * 80)

        encontrados = False

        for datos in self.lista.values():
            if datos["fecha"] == fecha:
                encontrados = True

                sala_nombre = lista_salas.get(datos['id_sala'], {"Nombre": "Desconocida"})['Nombre']
                cliente_datos = lista_clientes.get(datos['id_cliente'], {"Nombre": "Desconocido", "Apellidos": ""})
                cliente = f"{cliente_datos['Nombre']} {cliente_datos['Apellidos']}"

                print(f"{sala_nombre:<15} {cliente:<20} {datos['nombre_evento']:<30} {datos['turno']:<15}")

        if not encontrados:
            print("No hay reservaciones para esta fecha.")

        return encontrados

    def mostrar_reservaciones_en_rango(self, fecha_inicio: dt.date, fecha_fin: dt.date) -> list:
        """Muestra las reservaciones como formato tabular dentro de un rango de fechas definido.

        Args:
            fecha_inicio (date): Fecha de inicio a consultar.
            fecha_fin (date): Fecha fin a consultar.

        Returns:
            list: Lista de folios válidos en el rango.
        """

        print(f"\nEventos en el rango de fechas {fecha_inicio.strftime('%m-%d-%Y')} a {fecha_fin.strftime('%m-%d-%Y')}:")
        print(f"{'Folio':<15} {'Nombre Evento':<30} {'Fecha':<15}")
        print("-" * 60)

        lista_eventos = []

        for folio, datos in self.lista.items():
            if fecha_inicio <= datos["fecha"] <= fecha_fin:
                lista_eventos.append((folio, datos["nombre_evento"], datos["fecha"]))

        lista_eventos.sort(key=lambda x: x[2])

        for folio, evento, fecha in lista_eventos:
            print(f"{folio:<15} {evento:<30} {fecha.strftime('%m-%d-%Y'):<15}")

        return [folio for folio, _, _ in lista_eventos]

    def editar_nombre_evento(self, folio: str, nuevo_nombre: str) -> None:
        """Edita el nombre de un evento ya existente.

        Args:
            folio (str): Folio del evento.
            nuevo_nombre (str): Nuevo nombre que tendrá el evento.
        """

        if folio in self.lista:
            self.lista[folio]["nombre_evento"] = nuevo_nombre
            with sqlite3.connect("coworking.db") as conn:
                c = conn.cursor()
                c.execute("""
                    UPDATE reservaciones
                    SET nombre_evento = ?
                    WHERE folio = ?
                """, (nuevo_nombre, int(folio)))
            print(f"Nombre del evento actualizado exitosamente para el folio {folio}.")
        else:
            print("Folio no encontrado.")

class ManejarSalas:
    """Clase para el manejo de salas.

        Estructura de un registro promedio:

        lista = {
            id_sala: {
                Nombre: str,
                Cupo: int
            }
        }
    """

    def __init__(self):
        self.lista = self._load_from_db()

    def _load_from_db(self) -> dict:
        """Carga las salas desde la base de datos."""
        lista = {}
        with sqlite3.connect("coworking.db") as conn:
            c = conn.cursor()
            c.execute("SELECT id_sala, nombre, cupo FROM salas")
            for row in c.fetchall():
                id_s, nom, cup = row
                lista[str(id_s)] = {"Nombre": nom, "Cupo": cup}
        return lista

    def registrar_sala(self, nombre: str, cupo: int) -> None:
        """Registra una sala dentro de la base de datos y en la lista local.

        Args:
            nombre (str): Nombre de la sala.
            cupo (int): Cupo de la sala.
        """

        with sqlite3.connect("coworking.db") as conn:
            c = conn.cursor()
            c.execute("INSERT INTO salas (nombre, cupo) VALUES (?, ?)", (nombre, cupo))
            id_s = c.lastrowid

        self.lista[str(id_s)] = {"Nombre": nombre.strip(), "Cupo": cupo}

        print(f"Sala registrada exitosamente con el ID: {id_s}")

class ManejarClientes:
    """Clase para el manejo de clientes.

        Estructura de registro promedio:
        lista = {
            id_cliente: {
                Nombre: str,
                Apellidos: str
            }
        }
    """

    def __init__(self):
        self.lista = self._load_from_db()

    def _load_from_db(self) -> dict:
        """Carga los clientes desde la base de datos."""
        lista = {}
        with sqlite3.connect("coworking.db") as conn:
            c = conn.cursor()
            c.execute("SELECT id_cliente, nombre, apellidos FROM clientes")
            for row in c.fetchall():
                id_c, nom, apell = row
                lista[str(id_c)] = {"Nombre": nom, "Apellidos": apell}
        return lista

    def registrar_cliente(self, nombre: str, apellidos: str) -> bool:
        """Registra un cliente dentro de la base de datos y en la lista local.

        Args:
            nombre (str): Nombre del cliente.
            apellidos (str): Apellidos del cliente.

        Returns:
            bool: True si el cliente se registró de manera exitosa.
        """

        with sqlite3.connect("coworking.db") as conn:
            c = conn.cursor()
            c.execute("INSERT INTO clientes (nombre, apellidos) VALUES (?, ?)", (nombre, apellidos))
            id_c = c.lastrowid

        self.lista[str(id_c)] = {"Nombre": nombre, "Apellidos": apellidos}

        print(f"Cliente registrado satisfactoriamente con el ID: {id_c}")

        return True

    def mostrar_clientes(self) -> None:
        """Muestra los clientes registrados en formato tabular."""

        ordenado = dict(sorted(self.lista.items(), key=lambda item: (item[1]["Apellidos"], item[1]["Nombre"])))

        print("\nListado de clientes registrados:")
        print(f"{'ID':<15} {'Nombre':<20} {'Apellidos':<20}")
        print("-" * 55)

        for id_cliente, datos in ordenado.items():
            nombre, apellidos = datos.values()
            print(f"{id_cliente:<15} {nombre:<20} {apellidos:<20}")

class Coworking:
    """Clase principal del coworking."""

    def __init__(self, clientes: ManejarClientes = None, salas: ManejarSalas = None, reservaciones: ManejarReservaciones = None):
        self.clientes = clientes or ManejarClientes()
        self.salas = salas or ManejarSalas()
        self.reservaciones = reservaciones or ManejarReservaciones()

    def __verificar_salida(self) -> bool:
        """Verifica si el usuario quiere salir de la operación actual.
        De esta forma evitamos repetir las validaciones flag.

        Returns:
            bool: True si el usuario quiere salir, False si quiere continuar.
        """

        confirmar_salida = input("¿Quiere cancelar la operación? Escriba S para salir o cualquier tecla para continuar: ")
        return True if confirmar_salida.upper() == "S" else False

    def __pedir_string(self, mensaje: str) -> str:
        """Pide una cadena no vacía al usuario y la devuelve en caso de que sea válida.

        Args:
            mensaje (str): Mensaje que se mostrará al usario para la entrada.

        Raises:
            ValueError: El usuario mandó un valor vacío.

        Returns:
            str: Entrada ya validada.
        """

        while True:
            entrada = input(mensaje).strip()
            if not entrada:
                print("El campo no puede estar vacío.")
                raise ValueError
            return entrada

    def __registrar_reservacion_sala(self) -> None:
        """Opción #1 del menú. Permite registrar la reservación de una sala.

        Returns:
            None: Usado para salir de la función en caso de que el usuario lo decida.
        """

        print("Ha escogido la opción: Registrar reservación de sala")

        while True:
            self.clientes.mostrar_clientes()

            try:
                id_cliente = self.__pedir_string("Escriba su ID de cliente: ")

                if id_cliente not in self.clientes.lista:
                    print("Por favor escriba un ID válido.")
                    raise ValueError

            except ValueError:
                if self.__verificar_salida():
                    return
                continue

            break

        while True:
            try:
                fecha_str = self.__pedir_string("Escriba la fecha (mm-dd-yyyy): ")
                fecha = dt.datetime.strptime(fecha_str, "%m-%d-%Y").date()

                fecha_minima = dt.date.today() + dt.timedelta(days=2)

                if fecha < fecha_minima:
                    print("La reservación debe ser por lo menos con dos días de anticipación.")
                    continue

                if fecha.weekday() == 6:
                    print("La fecha solicitada es domingo. No se permiten reservaciones en domingos.")
                    fecha_propuesta = fecha + dt.timedelta(days=1)
                    while fecha_propuesta.weekday() == 6:
                        fecha_propuesta += dt.timedelta(days=1)
                    aceptar = input(f"Se propone la fecha {fecha_propuesta.strftime('%m-%d-%Y')}. ¿Acepta? (S/N): ").upper()
                    if aceptar == 'S':
                        fecha = fecha_propuesta
                    else:
                        continue

                break
            except ValueError:
                print("Formato no válido. Por favor, escríbalo de nuevo usando el formato correcto.")

                if self.__verificar_salida():
                    return

                continue

        while True:
            self.reservaciones.mostrar_salas_disponibles(self.salas.lista, fecha)
            try:
                id_sala = self.__pedir_string("Escriba el ID de la sala a escoger: ")

                if id_sala not in self.salas.lista:
                    print("ID de sala no válido.")

                    if self.__verificar_salida():
                        return
                break

            except ValueError:
                print("Error: Formato inválido")

                if self.__verificar_salida():
                    return 

                continue

        while True:
            turno = input("Escriba el turno a escoger (Matutino, Vespertino, Nocturno): ").capitalize()

            if turno not in self.reservaciones.turnos:
                print("Turno no válido.")

                if self.__verificar_salida():
                    return

                continue

            if not self.reservaciones.verificar_disponibilidad(fecha, id_sala, turno):
                print("No hay disponibilidad en ese turno para esta sala.")

                if self.__verificar_salida():
                    return

                continue

            break

        print("Hay disponibilidad.")

        while True:
            nombre_evento = input("Escriba el nombre del evento: ").strip()

            if not nombre_evento:
                print("Escriba un nombre válido (no puede estar vacío).")

                if self.__verificar_salida():
                    return

                continue

            break

        self.reservaciones.registrar_reservacion(id_cliente, fecha, turno, id_sala, nombre_evento)

    def __editar_nombre_reservacion(self) -> None:
        """Opción #2 del menú. Permite editar el nombre de una reservación ya hecha.

        Returns:
            None: Usado para salir de la función en caso de que el usuario lo decida.
        """

        print("Ha escogido la opción: Editar el nombre de una reservación ya hecha")

        while True:
            try:
                fecha_inicio_str = input("Escriba la fecha de inicio del rango (mm-dd-yyyy): ")
                fecha_inicio = dt.datetime.strptime(fecha_inicio_str, "%m-%d-%Y").date()

                fecha_fin_str = input("Escriba la fecha de fin del rango (mm-dd-yyyy): ")
                fecha_fin = dt.datetime.strptime(fecha_fin_str, "%m-%d-%Y").date()

                if fecha_inicio > fecha_fin:
                    print("La fecha de inicio no puede ser posterior a la de fin.")
                    continue

                folios_validos = self.reservaciones.mostrar_reservaciones_en_rango(fecha_inicio, fecha_fin)

                if not folios_validos:
                    print("No hay eventos en este rango de fechas.")

                    if self.__verificar_salida():
                        return

                    continue

                break
            except ValueError:
                print("Formato no válido. Por favor, escríbalo de nuevo usando el formato correcto.")

                if self.__verificar_salida():
                    return

                continue

        while True:
            try:
                folio_str = self.__pedir_string("Escriba el folio del evento a modificar: ")
                folio = folio_str

                if folio not in folios_validos:
                    print("Folio no válido en este rango. Por favor, seleccione uno de la lista.")
                    raise ValueError

                break
            except ValueError:
                if self.__verificar_salida():
                    return
                continue


        while True:
            try:
                nuevo_nombre = self.__pedir_string("Escriba el nuevo nombre del evento: ")
                break
            except ValueError:
                if self.__verificar_salida():
                    return
                continue

        self.reservaciones.editar_nombre_evento(folio, nuevo_nombre)

    def __consultar_reservaciones_fecha(self) -> None:
        """Opción #3 del menú. Permite consultar las reservaciones de una fecha específica.

        Returns:
            None: Usado para salir de la función en caso de que el usuario lo decida.
        """

        print("Ha escogido la opción: Consultar reservaciones de una fecha específica")

        while True:
            try:
                fecha_str = input("Escriba la fecha a consultar (mm-dd-yyyy) o presione Enter para la fecha actual: ").strip()
                if not fecha_str:
                    fecha = dt.date.today()
                    break
                fecha = dt.datetime.strptime(fecha_str, "%m-%d-%Y").date()
                break
            except ValueError:
                print("Formato no válido. Por favor, escríbalo de nuevo usando el formato correcto.")

                if self.__verificar_salida():
                    return
                continue

        encontrados = self.reservaciones.mostrar_reservaciones_por_fecha(fecha, self.salas.lista, self.clientes.lista)

        if encontrados:
            exportar = input("¿Desea exportar estas reservaciones? (SI/NO): ").upper()
            if exportar == "SI":
                formato = input("Seleccione el formato de exportación: JSON, CSV o EXCEL: ").upper()

                reservaciones_fecha = {
                    folio: datos
                    for folio, datos in self.reservaciones.lista.items()
                    if datos["fecha"] == fecha
                }

                fecha_str = fecha.strftime('%m-%d-%Y')

                if formato == "JSON":
                    export_data = {
                        folio: {**datos, "fecha": datos["fecha"].strftime('%m-%d-%Y')}
                        for folio, datos in reservaciones_fecha.items()
                    }
                    with open(f"reservaciones_{fecha_str}.json", "w", encoding="utf-8") as archivo:
                        json.dump(export_data, archivo, indent=2, ensure_ascii=False)
                    print(f"Reservaciones exportadas correctamente a 'reservaciones_{fecha_str}.json'")

                elif formato == "CSV":
                  with open(f"reservaciones_{fecha_str}.csv", "w", newline="", encoding="utf-8") as archivo:
                    manejar_csv = csv.writer(archivo)
                    manejar_csv.writerow(("Folio", "ID Cliente", "Fecha", "Turno", "ID Sala", "Nombre Evento"))

                    for folio, datos in reservaciones_fecha.items():
                      manejar_csv.writerow((folio, datos['id_cliente'], datos['fecha'].strftime('%m-%d-%Y'), datos['turno'], datos['id_sala'], datos['nombre_evento']))

                elif formato == "EXCEL":
                  reservaciones_filtradas = {
                    folio: datos
                    for folio, datos in self.reservaciones.lista.items()
                    if datos["fecha"] == fecha
                  }

                  libro = openpyxl.Workbook()
                  hoja = libro.active
                  hoja.title = f"Reservaciones_{fecha_str}"

                  negrita = Font(bold=True)
                  centrado = Alignment(horizontal="center", vertical="center")
                  borde_grueso = Border(bottom=Side(border_style="thick"))

                  encabezados = ["Folio", "ID Cliente", "Fecha", "Turno", "ID Sala", "Nombre Evento"]
                  for columna, titulo in enumerate(encabezados, start=1):
                    celda = hoja.cell(row=1, column=columna, value=titulo)
                    celda.font = negrita
                    celda.alignment = centrado
                    celda.border = borde_grueso

                  for renglon, (folio, datos) in enumerate(reservaciones_filtradas.items(), start=2):
                    hoja.cell(row=renglon, column=1, value=folio).alignment = centrado
                    hoja.cell(row=renglon, column=2, value=datos["id_cliente"]).alignment = centrado
                    hoja.cell(row=renglon, column=3, value=datos["fecha"].strftime('%m-%d-%Y')).alignment = centrado
                    hoja.cell(row=renglon, column=4, value=datos["turno"]).alignment = centrado
                    hoja.cell(row=renglon, column=5, value=datos["id_sala"]).alignment = centrado
                    hoja.cell(row=renglon, column=6, value=datos["nombre_evento"]).alignment = centrado

                  libro.save(f"reservaciones_{fecha_str}.xlsx")
                  print(f"Reservaciones exportadas correctamente a 'reservaciones_{fecha_str}.xlsx'")

                else:
                    print("Formato no válido. Opciones disponibles: JSON, CSV, EXCEL.")

    def __registrar_nuevo_cliente(self) -> None:
        """Opción #4 del menú. Permite registrar a un nuevo cliente.

        Returns:
            None: Usado para salir de la función en caso de que el usuario lo decida.
        """

        print("Ha escogido la opción: Registrar a un nuevo cliente.")

        while True:
            try:
                nombre = self.__pedir_string("Escriba su nombre: ")
                break
            except ValueError:
                if self.__verificar_salida():
                    return
                continue

        while True:
            try:
                apellidos = self.__pedir_string("Escriba sus apellidos: ")
                break
            except ValueError:
                if self.__verificar_salida():
                    return
                continue

        self.clientes.registrar_cliente(nombre, apellidos)

    def __registrar_nueva_sala(self) -> None:
        """Opción #5 del menú. Registra una nueva sala.

        Returns:
            None: Usado para salir de la función en caso de que el usuario lo decida.
        """

        print("Ha escogido la opción: registrar nueva sala")

        while True:
            try:
                nombre_sala = self.__pedir_string("Escriba el nombre de la sala: ")
                break
            except ValueError:
                if self.__verificar_salida():
                    return
                continue

        while True:
            try:
                cupo_str = self.__pedir_string("Escriba el cupo de la sala: ")
                cupo = int(cupo_str)
                break
            except ValueError:
                print("Valor inválido")
                if self.__verificar_salida():
                    return
                continue

        self.salas.registrar_sala(nombre_sala, cupo)

    def mostrar_menu(self) -> None:
        """Muestra al usuario una interfaz de texto para poder realizar diversas acciones dentro del coworking."""

        while True:
            print("\nBienvenido al programa del coworking.")
            print("Opciones disponibles:")
            print("(1) - Registrar reservación de sala")
            print("(2) - Editar el nombre de una reservación ya hecha")
            print("(3) - Consultar reservaciones de una fecha específica")
            print("(4) - Registrar a un nuevo cliente")
            print("(5) - Registrar una sala")
            print("(6) - Salir del programa\n")

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
                    self.__registrar_reservacion_sala()
                case 2:
                    self.__editar_nombre_reservacion()
                case 3:
                    self.__consultar_reservaciones_fecha()
                case 4:
                    self.__registrar_nuevo_cliente()
                case 5:
                    self.__registrar_nueva_sala()
                case 6:
                    confirmar = input("¿Desea salir del programa, los datos se guardaran en la base de datos? (S/N): ").upper()
                    if confirmar == "S":
                        print("Saliendo del programa...")
                        break

if __name__ == "__main__":

    if not os.path.exists("coworking.db"):
        inicializar_base_datos()

    programa = Coworking()
    if not programa.clientes.lista and not programa.salas.lista and not programa.reservaciones.lista:
        print("Se inicia con un estado inicial vacío.")

    programa.mostrar_menu()