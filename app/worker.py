import asyncio
from datetime import datetime
from app.log_utils import get_daily_logger
from app.mysql_utils import mysql_execute, mysql_query

logger = get_daily_logger()

async def task_tabla_TB_DOM_INVALID_PERIF():
    return mysql_execute("DELETE FROM TB_DOM_INVALID_PERIF WHERE Ultimo < (UNIX_TIMESTAMP()-(60*10));")  # Eliminar registros más antiguos que 10 min

async def worker_loop():

    while True:
        await task_tabla_TB_DOM_INVALID_PERIF()

        await asyncio.sleep(60)  # Espera 1 minuto entre iteraciones
