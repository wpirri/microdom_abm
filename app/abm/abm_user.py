from app.log_utils import get_daily_logger
from app.mysql_utils import mysql_execute, mysql_query, mysql_next_id

logger = get_daily_logger()

def get_user_list():
    query_result = mysql_query("SELECT Id, Usuario, Nombre_Completo, Estado, Ultimo_Acceso FROM TB_DOM_USER ORDER BY Usuario ASC;");
    return {"error": 0, "message": "Ok", "response": query_result}

def get_user_list_all():
    query_result = mysql_query("SELECT * FROM TB_DOM_USER")
    return {"error": 0, "message": "Ok", "response": query_result}

def get_user(id):
    query_result = mysql_query(f"SELECT * FROM TB_DOM_USER WHERE Id = {id}")
    return {"error": 0, "message": "Ok", "response": query_result}

def add_user(data):
    next_id = mysql_next_id('TB_DOM_USER')
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
    query = f"INSERT INTO TB_DOM_USER ({campos_str}) VALUES ({valores_str})"

    #logger.info(f"[add_user] Insertando: {query}")
    mysql_execute(query)
    return {"error": 0, "message": "Ok", "Id": next_id}

def update_user(data):
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
    query = f"UPDATE TB_DOM_USER SET {campos_valores_str} WHERE Id = {Id}"

    #logger.info(f"[update_user] Actualizando: {query}")
    mysql_execute(query)
    return {"error": 0, "message": "Ok"}

def delete_user(Id):
    if not Id:
        return {"error": 1, "message": "Id es requerido"}

    query = f"DELETE FROM TB_DOM_USER WHERE Id = {Id}"
    #logger.info(f"[delete_user] Eliminando: {query}")
    mysql_execute(query)
    return {"error": 0, "message": "Ok"}

def check_card_auth(card):
    query = f"SELECT * FROM TB_DOM_USER WHERE Tarjeta = '{card}'"
    query_result = mysql_query(query)
    if query_result:
        for i in range(0, len(query_result)):
            nombre = query_result[i]['Nombre_Completo']
            logger.info(f"[check_card_auth] Tarjeta: {card} - Usuario; {nombre}")
            
        return True
    else:
        logger.info(f"[check_card_auth] Tarjeta: {card} - No válida")
        add_invalid_card(card)
    return False

def add_invalid_card(tarjeta):
    if mysql_execute(f"UPDATE TB_DOM_INVALID_CARD SET Time_Stamp = UNIX_TIMESTAMP() WHERE WHERE Tarjeta='{tarjeta}'") == 0:
        if mysql_execute(f"INSERT INTO TB_DOM_INVALID_CARD (Tarjeta, Time_Stamp) VALUES ({tarjeta}, UNIX_TIMESTAMP())") > 0:
            logger.info(f"Periferico desconocido agregado a la lista: {tarjeta}")

def get_invalid_card_list():
    mysql_execute(f"DELETE FROM TB_DOM_INVALID_CARD WHERE WHERE Time_Stamp < UNIX_TIMESTAMP() - 600")
    query_result = mysql_query("SELECT Tarjeta FROM TB_DOM_INVALID_CARD")
    return {"error": 0, "message": "Ok", "response": query_result}
