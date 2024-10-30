from datetime import datetime
import mysql.connector

class ReportManager:
    def __init__(self, connection):
        self.connection = connection

    # Método para guardar o actualizar el reporte basado en la probabilidad
    def save_report(self, probability, time_taken):
        # Obtener la fecha actual
        fecha_actual = datetime.now().date()

        # Determinar si el sitio es fraudulento/dudoso o aceptable/legítimo
        if probability > 0.75:  # Sitio fraudulento
            detections = 1
            update_time = time_taken  # Solo acumulamos el tiempo si es fraudulento o dudoso
        elif probability > 0.5:  # Sitio dudoso
            detections = 1
            update_time = time_taken  # Solo acumulamos el tiempo si es fraudulento o dudoso
        else:  # Sitio aceptable o legítimo
            detections = 0
            update_time = 0  # No acumulamos tiempo para sitios aceptables o legítimos

        # Siempre incrementamos el número de sitios evaluados
        sites = 1

        cursor = self.connection.cursor()

        # Verificar si ya existe un reporte con la fecha actual
        query_select = "SELECT id, sites, detections, time FROM Detections WHERE fecha = %s"
        cursor.execute(query_select, (fecha_actual,))
        result = cursor.fetchone()

        if result:
            # Asegurarse de consumir los resultados completamente antes de continuar
            cursor.fetchall()

            # Si ya existe un registro para la fecha actual, acumulamos los valores
            report_id, current_sites, current_detections, current_time = result
            new_sites = current_sites + sites
            new_detections = current_detections + detections  # Acumular detecciones solo si es fraudulento o dudoso
            new_time = current_time + update_time  # Acumular el tiempo solo si es fraudulento o dudoso

            # Actualizar el registro existente
            query_update = """
                UPDATE Detections
                SET sites = %s, detections = %s, time = %s
                WHERE id = %s
            """
            cursor.execute(query_update, (new_sites, new_detections, new_time, report_id))
        else:
            # Si no existe un registro para la fecha actual, insertamos uno nuevo
            query_insert = """
                INSERT INTO Detections (fecha, sites, detections, time)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query_insert, (fecha_actual, sites, detections, update_time))

        self.connection.commit()
        cursor.close()
        print("Reporte guardado o actualizado exitosamente.")