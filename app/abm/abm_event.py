from app.log_utils import get_daily_logger
from app.mysql_utils import mysql_execute, mysql_query, mysql_next_id

logger = get_daily_logger()

def get_event_list():
    query = """SELECT EV.Id, EV.Evento, EV.ON_a_OFF AS \'OFF\', EV.OFF_a_ON AS \'ON\', ASS.Objeto AS Origen 
                FROM TB_DOM_EVENT AS EV, TB_DOM_ASSIGN AS ASS 
                WHERE EV.Objeto_Origen = ASS.Id 
                ORDER BY EV.Evento ASC;"""
    query_result = mysql_query(query);
    return {"error": 0, "message": "Ok", "response": query_result}

def get_event_list_all():
    query_result = mysql_query("SELECT * FROM TB_DOM_EVENT")
    return {"error": 0, "message": "Ok", "response": query_result}

def get_event(id):
    query_result = mysql_query(f"SELECT * FROM TB_DOM_EVENT WHERE Id = {id}")
    return {"error": 0, "message": "Ok", "response": query_result}

def add_event(data):
    next_id = mysql_next_id('TB_DOM_EVENT')
    if next_id in (None, ''):
        next_id = 1
    data['Id'] = next_id

    campos = []
    valores = []
    for key, value in data.items():
        campos.append(key)
        if isinstance(value, str):
            escaped_value = value.replace("'", "''")
            valores.append(f"'{escaped_value}'")
        else:
            valores.append(str(value))

    campos_str = ', '.join(campos)
    valores_str = ', '.join(valores)
    query = f"INSERT INTO TB_DOM_EVENT ({campos_str}) VALUES ({valores_str})"

    #logger.info(f"[add_event] Insertando: {query}")
    mysql_execute(query)
    return {"error": 0, "message": "Ok", "Id": next_id}

def update_event(data):
    Id = data.get('Id')
    if not Id:
        return {"error": 1, "message": "Id es requerido"}

    campos_valores = []
    for key, value in data.items():
        if key == 'Id':
            continue
        if isinstance(value, str):
            escaped_value = value.replace("'", "''")
            campos_valores.append(f"{key} = '{escaped_value}'")
        else:
            campos_valores.append(f"{key} = {value}")

    campos_valores_str = ', '.join(campos_valores)
    query = f"UPDATE TB_DOM_EVENT SET {campos_valores_str} WHERE Id = {Id}"

    #logger.info(f"[update_event] Actualizando: {query}")
    mysql_execute(query)
    return {"error": 0, "message": "Ok"}

def delete_event(Id):
    if not Id:
        return {"error": 1, "message": "Id es requerido"}

    query = f"DELETE FROM TB_DOM_EVENT WHERE Id = {Id}"
    #logger.info(f"[delete_event] Eliminando: {query}")
    mysql_execute(query)
    return {"error": 0, "message": "Ok"}
