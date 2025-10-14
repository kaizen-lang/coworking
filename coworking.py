"""Script de coworking."""

import datetime as dt
import json
import csv
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side

class ManejarReservaciones:

    """Clase para manejar reservaciones.

    Estructura de un registro promedio
        lista = {
            folio: {
                id_cliente: str,
                fecha: dt.date,
                turno: str,
                id_sala: str,
                nombre_evento: str
            }
        }
    """

    def __init__(self, lista: dict = None):
        #En caso de que no se pase una lista, se crea una vacía, para evitar que se comparta entre instancias.
        self.lista = lista or {}
        self.turnos = ("Matutino", "Vespertino", "Nocturno")

        if self.lista:
            try:
                self.contador_folio = max(map(int, self.lista.keys()))
            except ValueError:
                self.contador_folio = 0
        else:
            self.contador_folio = 0

    def registrar_reservacion(self, id_cliente: str, fecha: dt.date, turno: str, id_sala: str, nombre_evento: str) -> None:
        """Registra una reservación nueva en la lista.

        Args:
            id_cliente (str): ID del cliente que hace la reservación.
            fecha (dt.date): Fecha de la reservación.
            turno (str): Turno de la reservación.
            id_sala (str): ID de la sala a reservar.
            nombre_evento (str): Nombre del evento a realizar.
        """

        self.contador_folio += 1
        folio = str(self.contador_folio)

        self.lista[folio] = {
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

    def verificar_disponibilidad(self, fecha: dt.date, id_sala: str, turno: str)->bool:
        """Verifica si una sala está disponible en una fecha, sala y turno específicos.

        Args:
            fecha (date): Fecha a consultar.
            id_sala (str): ID de la sala a consultar.
            turno (str): Turno a consultar.

        Returns:
            bool: True si está disponible, False si no lo está.
        """

        for reservacion in self.lista.values():  #Iteramos por cada reservación para realizar el filtro
            fecha_reservacion, turno_reservacion, id_sala_reservada = reservacion["fecha"], reservacion["turno"], reservacion["id_sala"]

            if (fecha_reservacion == fecha) and (turno_reservacion == turno) and (id_sala_reservada == id_sala):
                return False

        return True

    def mostrar_reservaciones_por_fecha(self, fecha: dt.date, lista_salas: dict, lista_clientes: dict) -> bool:
        """Muestra las reservaciones por fecha en formato tabular.

        Args:
            fecha (dt.date): Fecha a consultar.
            lista_salas (dict): Lista con las salas disponibles.
            lista_clientes (dict): Lista con los clientes registrados.

        Returns:
            bool: True si se encontraron reservaciones, False si no.
        """

        print(f"\nReporte de reservaciones para la fecha {fecha}:")
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

    def editar_nombre_evento(self, folio: str, nuevo_nombre: str) -> None:
        """Edita el nombre de un evento ya existente.

        Args:
            folio (str): Folio del evento.
            nuevo_nombre (str): Nuevo nombre que tendrá el evento.
        """

        if folio in self.lista:
            self.lista[folio]["nombre_evento"] = nuevo_nombre
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

    def __init__(self, lista = None):
        #En caso de que no se pase una lista, se crea una vacía, para evitar que se comparta entre instancias.
        self.lista = lista or {}

        if self.lista:
            try:
                self.contador_salas = max(map(int, self.lista.keys()))
            except ValueError:
                self.contador_salas = 0
        else:
            self.contador_salas = 0

    def registrar_sala(self, nombre: str, cupo: int) -> None:
        """Registra una sala dentro de la lista.

        Args:
            nombre (str): Nombre de la sala.
            cupo (int): Cupo de la sala.
        """

        self.contador_salas += 1
        id_sala = str(self.contador_salas)

        self.lista[id_sala] = {"Nombre": nombre.strip(), "Cupo": cupo}

        print(f"Sala registrada exitosamente con el ID: {id_sala}")

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

    def __init__(self, lista = None):
        #En caso de que no se pase una lista, se crea una vacía, para evitar que se comparta entre instancias.
        self.lista = lista or {}
        if self.lista:
            try:
                self.contador_clientes = max(map(int, self.lista.keys()))
            except ValueError:
                self.contador_clientes = 0
        else:
            self.contador_clientes = 0

    def registrar_cliente(self, nombre: str, apellidos: str) -> bool:
        """Registra un cliente dentro de la lista.

        Args:
            nombre (str): Nombre del cliente.
            apellidos (str): Apellidos del cliente.

        Returns:
            bool: True si el cliente se registró de manera exitosa.
        """

        self.contador_clientes += 1
        id_cliente = str(self.contador_clientes)

        self.lista[id_cliente] = {"Nombre": nombre, "Apellidos": apellidos}

        print(f"Cliente registrado satisfactoriamente con el ID: {id_cliente}")

        return True

    def mostrar_clientes(self) -> None:
        """Muestra los clientes registrados en formato tabular."""

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
    """Clase principal del coworking."""

    def __init__(self, clientes: ManejarClientes = None, salas: ManejarSalas = None, reservaciones: ManejarReservaciones = None):
        #En caso de que no se pasen argumentos, se crean las clases con listas vacías.
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
                    return #Salir de la función, regresa al menú principal
                continue

            break

        while True:
            try:
                fecha_str = self.__pedir_string("Escriba la fecha (dd/mm/aaaa): ")
                fecha = dt.datetime.strptime(fecha_str, "%d/%m/%Y").date()

                #Validando si la reservación es mínimo dos días posteriores al día actual
                fecha_minima = dt.date.today() + dt.timedelta(days=2)

                if fecha < fecha_minima:
                    print("La reservación debe ser por lo menos con dos días de anticipación.")
                    continue

                break
            except ValueError:
                print("Formato no válido. Por favor, escríbalo de nuevo usando el formato correcto.")

                if self.__verificar_salida():
                    return #Salir de la función, regresa al menú principal

                continue

        while True:
            self.reservaciones.mostrar_salas_disponibles(self.salas.lista, fecha)
            try:
                id_sala = self.__pedir_string("Escriba el ID de la sala a escoger: ")

                if id_sala not in self.salas.lista:
                    print("ID de sala no válido.")

                    if self.__verificar_salida():
                        return #Salir de la función, regresa al menú principal

                break

            except ValueError:
                print("Error: Formato inválido")

                if self.__verificar_salida():
                    return #Salir de la función, regresa al menú principal

                continue

        while True:
            turno = input("Escriba el turno a escoger (Matutino, Vespertino, Nocturno): ").capitalize()

            if turno not in self.reservaciones.turnos:
                print("Turno no válido.")

                if self.__verificar_salida():
                    return #Salir de la función, regresa al menú principal

                continue

            if not self.reservaciones.verificar_disponibilidad(fecha, id_sala, turno):
                print("No hay disponibilidad en ese turno para esta sala.")

                if self.__verificar_salida():
                    return #Salir de la función, regresa al menú principal

                continue

            break

        print("Hay disponibilidad.")

        while True:
            nombre_evento = input("Escriba el nombre del evento: ").strip()

            if not nombre_evento or len(nombre_evento) < 3:
                print("Escriba un nombre válido (mínimo 3 caracteres).")

                if self.__verificar_salida():
                    return #Salir de la función, regresa al menú principal

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
                fecha_inicio_str = input("Escriba la fecha de inicio del rango (dd/mm/aaaa): ")
                fecha_inicio = dt.datetime.strptime(fecha_inicio_str, "%d/%m/%Y").date()

                fecha_fin_str = input("Escriba la fecha de fin del rango (dd/mm/aaaa): ")
                fecha_fin = dt.datetime.strptime(fecha_fin_str, "%d/%m/%Y").date()

                if fecha_inicio > fecha_fin:
                    print("La fecha de inicio no puede ser posterior a la de fin.")
                    continue

                folios_validos = self.reservaciones.mostrar_reservaciones_en_rango(fecha_inicio, fecha_fin)

                if not folios_validos:
                    print("No hay eventos en este rango de fechas.")

                    if self.__verificar_salida():
                        return #Salir de la función, regresa al menú principal

                    continue

                break
            except ValueError:
                print("Formato no válido. Por favor, escríbalo de nuevo usando el formato correcto.")

                if self.__verificar_salida():
                    return #Salir de la función, regresa al menú principal

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
                    return #Salir de la función, regresa al menú principal
                continue


        while True:
            try:
                nuevo_nombre = self.__pedir_string("Escriba el nuevo nombre del evento: ")
                break
            except ValueError:
                if self.__verificar_salida():
                    return #Salir de la función, regresa al menú principal
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
                fecha_str = self.__pedir_string("Escriba la fecha a consultar (dd/mm/aaaa): ")
                fecha = dt.datetime.strptime(fecha_str, "%d/%m/%Y").date()
                break
            except ValueError:
                print("Formato no válido. Por favor, escríbalo de nuevo usando el formato correcto.")

                if self.__verificar_salida():
                    return #Salir de la función, regresa al menú principal
                continue

        encontrados = self.reservaciones.mostrar_reservaciones_por_fecha(fecha, self.salas.lista, self.clientes.lista)

        if encontrados:
            # Bloque agregado para exportar reservaciones
            exportar = input("¿Desea exportar estas reservaciones? (SI/NO): ").upper()
            if exportar == "SI":
                # Preguntar el formato
                formato = input("Seleccione el formato de exportación: JSON, CSV o EXCEL: ").upper()

                # Filtrar las reservaciones por la fecha seleccionada
                reservaciones_fecha = {
                    folio: datos
                    for folio, datos in self.reservaciones.lista.items()
                    if datos["fecha"] == fecha
                }

                # JSON
                if formato == "JSON":
                    for datos in reservaciones_fecha.values():
                        datos["fecha"] = datos["fecha"].isoformat()
                    with open(f"reservaciones_{fecha.isoformat()}.json", "w", encoding="utf-8") as archivo:
                        json.dump(reservaciones_fecha, archivo, indent=2, ensure_ascii=False)
                    print(f"Reservaciones exportadas correctamente a 'reservaciones_{fecha.isoformat()}.json'")

                # CSV
                elif formato == "CSV":
                  with open(f"reservaciones_{fecha.isoformat()}.csv", "w", newline="", encoding="utf-8") as archivo:
                    manejar_csv = csv.writer(archivo)
                    manejar_csv.writerow(("Folio", "ID Cliente", "Fecha", "Turno", "ID Sala", "Nombre Evento"))

                    for folio, datos in reservaciones_fecha.items():
                      manejar_csv.writerow((datos['id_cliente'], datos['fecha'].isoformat(), datos['turno'], datos['id_sala'], datos['nombre_evento']))

                # Excel
                elif formato == "EXCEL":
                  reservaciones_filtradas = {
                    folio: datos
                    for folio, datos in self.reservaciones.lista.items()
                    if datos["fecha"] == fecha
                  }

                  libro = openpyxl.Workbook()
                  hoja = libro.active
                  hoja.title = f"Reservaciones_{fecha.isoformat()}"

                  # Estilos
                  negrita = Font(bold=True)
                  centrado = Alignment(horizontal="center", vertical="center")
                  borde_grueso = Border(bottom=Side(border_style="thick"))

                  # Encabezados
                  encabezados = ["Folio", "ID Cliente", "Fecha", "Turno", "ID Sala", "Nombre Evento"]
                  for columna, titulo in enumerate(encabezados, start=1):
                    celda = hoja.cell(row=1, column=columna, value=titulo)
                    celda.font = negrita
                    celda.alignment = centrado
                    celda.border = borde_grueso

                  # Datos
                  for renglon, (folio, datos) in enumerate(reservaciones_filtradas.items(), start=2):
                    hoja.cell(row=renglon, column=1, value=folio).alignment = centrado
                    hoja.cell(row=renglon, column=2, value=datos["id_cliente"]).alignment = centrado
                    hoja.cell(row=renglon, column=3, value=datos["fecha"].isoformat()).alignment = centrado
                    hoja.cell(row=renglon, column=4, value=datos["turno"]).alignment = centrado
                    hoja.cell(row=renglon, column=5, value=datos["id_sala"]).alignment = centrado
                    hoja.cell(row=renglon, column=6, value=datos["nombre_evento"]).alignment = centrado

                  # Guardar archivo
                  libro.save(f"reservaciones_{fecha.isoformat()}.xlsx")
                  print(f"Reservaciones exportadas correctamente a 'reservaciones_{fecha.isoformat()}.xlsx'")

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
                    return #Salir de la función, regresa al menú principal
                continue

        while True:
            try:
                apellidos = self.__pedir_string("Escriba sus apellidos: ")
                break
            except ValueError:
                if self.__verificar_salida():
                    return #Salir de la función, regresa al menú principal
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
                    return #Salir de la función, regresa al menú principal
                continue

        while True:
            try:
                cupo_str = self.__pedir_string("Escriba el cupo de la sala: ")
                cupo = int(cupo_str)
                break
            except ValueError:
                print("Valor inválido")
                if self.__verificar_salida():
                    return #Salir de la función, regresa al menú principal
                continue

        self.salas.registrar_sala(nombre_sala, cupo)

    def guardar_datos(self) -> None:
        """Guarda las listas actuales en archivos JSON para persistencia."""

        with open("reservaciones.json", "w") as archivo:
            lista_exportada = self.reservaciones.lista.copy()
            for id, datos in lista_exportada.items():
                lista_exportada[id]["fecha"] = datos["fecha"].isoformat()
            json.dump(lista_exportada, archivo, indent=2)

        with open("clientes.json", "w") as archivo:
            json.dump(self.clientes.lista, archivo, indent=2)

        with open("salas.json", "w") as archivo:
            json.dump(self.salas.lista, archivo, indent=2)

        print("Datos guardados correctamente en formato JSON.")

    def cargar_datos(self) -> tuple[ManejarClientes, ManejarSalas, ManejarReservaciones]:
        """Carga las listas desde archivos JSON para persistencia. Retorna las instancias cargadas.

        Returns:
            tuple[ManejarClientes, ManejarSalas, ManejarReservaciones]: Tupla con instancias de ManejarClientes, ManejarSalas y ManejarReservaciones.
        """

        try:
            with open("reservaciones.json", "r") as archivo:
                lista_importada = json.load(archivo)
                for id, datos in lista_importada.items():
                    lista_importada[id]["fecha"] = dt.date.fromisoformat(datos["fecha"])
                reservaciones = ManejarReservaciones(lista_importada)
        except FileNotFoundError:
            reservaciones = ManejarReservaciones()

        try:
            with open("clientes.json", "r") as archivo:
                lista_importada = json.load(archivo)
                clientes = ManejarClientes(lista_importada)
        except FileNotFoundError:
            clientes = ManejarClientes()

        try:
            with open("salas.json", "r") as archivo:
                lista_importada = json.load(archivo)
                salas = ManejarSalas(lista_importada)
        except FileNotFoundError:
            salas = ManejarSalas()

        return clientes, salas, reservaciones

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
                #En lugar de meter toda la lógica en el menú, se llama a métodos privados que manejan cada opción.
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
                    print("Saliendo del programa... ¿Quiere guardar su progreso?")

                    while True:
                        guardar = input("Escriba S para guardar o N para salir sin guardar: ").upper()

                        if guardar == "N":
                            break

                        if guardar == "S":
                            self.guardar_datos()
                            break

                    break

if __name__ == "__main__":
    #Este código solo se ejecuta si el script es el programa principal.

    # Crear una instancia temporal para llamar al método de carga
    temp = Coworking()
    clientes, salas, reservaciones = temp.cargar_datos()

    #Le pasamos las instancias generadas al programa.
    programa = Coworking(clientes, salas, reservaciones)

    programa.mostrar_menu()
