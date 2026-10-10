from app.log_utils import get_daily_logger
from app.mysql_utils import mysql_execute, mysql_query, mysql_next_id

logger = get_daily_logger()

def get_touch_list(id, pantalla):
    if id:
        if pantalla:
            query =  ("SELECT T.Boton, T.Boton AS Nro, T.Texto, Evento, A.Objeto "
                "FROM TB_DOM_TOUCH AS T, TB_DOM_ASSIGN AS A "
                "WHERE T.Objeto = A.Id "
                f"AND T.Dispositivo = {id} AND T.Pantalla = {pantalla} "
                "ORDER BY Boton;")
        else:
            query = ("SELECT Pantalla, Pantalla AS Nro, COUNT(*) AS Botones "
                "FROM TB_DOM_TOUCH "
                f"WHERE Dispositivo = {id} "
                "GROUP BY Pantalla ORDER BY Pantalla;")
    else:
        query = """SELECT Id, Dispositivo, Direccion_IP, Estado 
            FROM TB_DOM_PERIF 
            WHERE Id > 0 AND Tipo = 5 
            ORDER BY Dispositivo ASC;"""
    #logger.info(f"[get_touch_list] Ejecutando: {query}")
    query_result = mysql_query(query);
    return {"error": 0, "message": "Ok", "response": query_result}  

def get_touch_list_all():
    query_result = mysql_query("SELECT * FROM TB_DOM_TOUCH")
    return {"error": 0, "message": "Ok", "response": query_result}

def get_touch(id, pantalla, boton):
    query_result = mysql_query(f"SELECT * FROM TB_DOM_TOUCH WHERE Dispositivo = {id} AND Pantalla = {pantalla} AND Boton = {boton};")
    return {"error": 0, "message": "Ok", "response": query_result}

def add_touch(id, pantalla, boton):
    query = f"INSERT INTO TB_DOM_TOUCH(Dispositivo, Pantalla, Boton) VALUES({id}, {pantalla}, {boton})"
    #logger.info(f"[add_touch] Insertando: {query}")
    mysql_execute(query)
    return {"error": 0, "message": "Ok"}

def update_touch(data):
    Dispositivo = data.get('Dispositivo')
    Pantalla = data.get('Pantalla')
    Boton = data.get('Boton')
    if not Dispositivo:
        return {"error": 1, "message": "Dispositivo es requerido"}
    if not Pantalla:
        return {"error": 1, "message": "Pantalla es requerida"}
    if not Boton:
        return {"error": 1, "message": "Boton es requerido"}

    campos_valores = []
    for key, value in data.items():
        if key == 'Id' or key == 'Dispositivo' or key == 'Pantalla' or key == 'Boton':
            continue
        if isinstance(value, str):
            escaped_value = value.replace("'", "''")
            campos_valores.append(f"{key} = '{escaped_value}'")
        else:
            campos_valores.append(f"{key} = {value}")

    campos_valores_str = ', '.join(campos_valores)
    query = f"UPDATE TB_DOM_TOUCH SET {campos_valores_str} WHERE Dispositivo = {Dispositivo} AND Pantalla = {Pantalla} AND Boton = {Boton}"
    #logger.info(f"[update_touch] Query: {query}")
    mysql_execute(query)
    return {"error": 0, "message": "Ok"}

def delete_touch(Id, pantalla, boton):
    if Id:
        if pantalla:
            if boton:
                query = f"DELETE FROM TB_DOM_TOUCH WHERE Dispositivo = {Id} AND Pantalla = {pantalla} AND Boton = {boton}"
            else:
                query = f"DELETE FROM TB_DOM_TOUCH WHERE Dispositivo = {Id} AND Pantalla = {pantalla}"
        else:
            query = f"DELETE FROM TB_DOM_TOUCH WHERE Dispositivo = {Id}"
    else:
        return {"error": 1, "message": "Id es requerido"}
    #logger.info(f"[delete_touch] Eliminando: {query}")
    mysql_execute(query)
    return {"error": 0, "message": "Ok"}
