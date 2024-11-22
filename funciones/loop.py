from highrise import *
from highrise.models import *
import asyncio
from typing import List

xmin, xmax = 13.5, 15.5
ymin, ymax = 2.25, 2.25
zmin, zmax = 16.5, 19.5

# Emote específico
emote_id = 'emote-teleporting'

emote_list : list[tuple[str, str]] = [
("Abajo", "idle-wild"),#random
("acostado", "idle_layingdown"),#ocasional
("Angel", "emote-snowangel"),#ocasional
("Anime", "dance-anime"),#baile
("Bow", "emote-bow"),#ocasional#saludo
("Boxer", "emote-boxer"),#pelea
("Casual", "idle-dance-casual"),#baile
("Charging", "emote-charging"),#ocasional#ansiedad
("Confusion", "emote-confused"),#ocasional
("Curtsy", "emote-curtsy"),#ocasional
("Cute", "emote-cute"),#ocasional
("Cutey", "emote-cutey"),#ocasional
("Espada", "emote-swordfight"),#pelea
("Explosion", "emote-headblowup"),#random
("Fashionista", "emote-fashionista"),#ocasional
("float", "emote-float"),#volar
("flotar", "idle-floating"),#volar
("Frog", "emote-frog"),#random
("Gravity", "emote-gravity"),#volar
("HameHa", "emote-energyball"),#pelea
("Hello", "emote-hello"),#ocasional#saludo
("Hyped", "emote-hyped"),#ocasionar#ganador
("Ice", "dance-icecream"),#baile#hombre
("Jingle", "dance-jinglebell"),#baile
("Kawaii", "dance-kawai"),#baile
("KPop", "dance-blackpink"),#baile
("Maniac", "emote-maniac"),#random#ansiedad
("Model", "emote-model"),#ocasional
("Moto", "emote-sleigh"),#ocasional
("Nervous", "idle-nervous"),#ocasional
("Ño", "emote-creepycute"),#random#ansiedad
("Penguin", "dance-pinguin"),#baile
("Pose10", "emote-pose10"),#ocasional
("Pose3", "emote-pose3"),#ocasional#encantar
("Pose8", "emote-pose8"),#ocasional
("Punk", "emote-punkguitar"),#baile#hombre
("Push", "dance-employee"),#baile
("Regalo", "emote-gift"),#ocasional
("Russian", "dance-russian"),#baile
("shi", "emote-shy2"),#ocasional
("Shopping", "dance-shoppingcart"),#baile
("Singing", "idle_singing"),#baile
("Siuu", "emote-celebrationstep"),#random
("Skating", "emote-iceskating"),#random
("Snake", "emote-snake"),#random
("Sorpresa", "emote-pose6"),#random
("Telekinesis", "emote-telekinesis"),#randoom
("Thriller", "dance-creepypuppet"),#baile#hombre
("TikTok10", "dance-tiktok10"),#baile
("tiktok2", "dance-tiktok2"),#baile
("TikTok4", "idle-dance-tiktok4"),#baile#chico
("tiktok8", "dance-tiktok8"),#baile
("TikTok9", "dance-tiktok9"),#baile
("TimeJump", "emote-timejump"),#random
("Toilet", "idle-toilet"),#ocasional
("UwU", "idle-uwu"),#ocasional
("volar", "emote-looping"),#volar
("Weird", "dance-weird"),#baile#chico
("Wrong", "dance-wrong"),#baile
("Zero", "emote-astronaut"),#volar
('Ditzy', 'emote-pose9'),#ocasional
('Guitar','idle-guitar'),#baile#hombre
('Telepor', 'emote-teleporting'),#random
('Touch', 'dance-touch'),#baile
("cohete", "emote-launch"),#volar
("entusiasta", "idle-enthusiastic"),#ocasional
("Tiktok11", "dance-tiktok11"),#baile#hombre
("snowball", "emote-snowball"),#pelea
("Push", "dance-employee"),#baile#hombre
("Paz", "emote-peace"),#ocasional
]

# Loop emotes
async def loop_emote(self: BaseBot, user: User, emote_name: str) -> None:
    """Ejecuta un emote en bucle para un usuario."""
    try:
        emote_id = next((emote[1] for emote in emote_list if emote[0].lower() == emote_name.lower()), None)
        if emote_id is None:
            return

        await self.highrise.send_whisper(user.id, f"@{user.username} está repitiendo {emote_name}")

        while True:
            try:
                await self.highrise.send_emote(emote_id, user.id)
                await asyncio.sleep(8.3)

                # Verificar si el usuario sigue en la sala
                try:
                    room_users = (await self.highrise.get_room_users()).content
                    user_ids = [room_user.id for room_user, _ in room_users]
                    if user.id not in user_ids:
                        break
                except Exception as e:
                    if "Cannot write to closing transport" in str(e):
                        print("Conexión perdida, esperando reconexión...")
                        await asyncio.sleep(5)
                        continue
                    print(f"Error verificando usuarios: {e}")
                    continue

            except Exception as e:
                if "Cannot write to closing transport" in str(e):
                    print("Conexión perdida en loop_emote, esperando reconexión...")
                    await asyncio.sleep(5)
                    continue
                else:
                    await self.highrise.send_whisper(user.id, f"@{user.username}, este emote no está disponible.")
                    break

    except Exception as e:
        print(f"Error en loop_emote: {e}")
        try:
            await self.highrise.send_whisper(user.id, "Ocurrió un error. Por favor, intenta de nuevo.")
        except:
            print("No se pudo enviar mensaje de error")

# Iniciar loop de emotes
async def loop(self: BaseBot, user: User, emote_name: str) -> None:
    """Inicia un nuevo loop de emotes."""
    try:
        # Validar si el emote existe
        emote_id = next((emote[1] for emote in emote_list if emote[0].lower() == emote_name.lower()), None)
        if emote_id is None:
            return

        taskgroup = self.highrise.tg
        task_list: List[asyncio.Task] = list(taskgroup._tasks)

        # Cancelar loop existente
        for task in task_list:
            if task.get_name() == user.username:
                task.cancel()

        # Crear nueva tarea
        task = taskgroup.create_task(loop_emote(self, user, emote_name))
        task.set_name(user.username)

    except Exception as e:
        print(f"Error en loop: {e}")
        try:
            await self.highrise.chat("Ocurrió un error. Por favor, intenta de nuevo.")
        except:
            print("No se pudo enviar mensaje de error")

# Detener loop de emotes
async def stop_loop(self: BaseBot, user: User) -> None:
    """Detiene el loop de emotes de un usuario."""
    try:
        taskgroup = self.highrise.tg
        task_list: List[asyncio.Task] = list(taskgroup._tasks)

        for task in task_list:
            if task.get_name() == user.username:
                task.cancel()
                await self.highrise.send_whisper(user.id, f"@{user.username}, detuvo la repetición del emote.")
                return

        await self.highrise.send_whisper(user.id, f"@{user.username}, no estás repitiendo ningún emote.")

    except Exception as e:
        print(f"Error en stop_loop: {e}")
        try:
            await self.highrise.send_whisper(user.id, "Ocurrió un error. Por favor, intenta de nuevo.")
        except:
            print("No se pudo enviar mensaje de error")

# All emote
async def emote(self: BaseBot, user: User, message: str) -> None:
    try:
        splited_message = message.split(" ")
        emote_name = " ".join(splited_message[1:])
    except:
        await self.highrise.send_whisper(user.id, "Formato de comando inválido. Por favor, usa 'all <nombre del emote>'.")
        return

    emote_id = ""
    for emote in emote_list:
        if emote[0].lower() == emote_name.lower():
            emote_id = emote[1]
            break
    if emote_id == "":
        await self.highrise.send_whisper(user.id, "Emote inválido")
        return

    await self.highrise.send_whisper(user.id, f"Todos {emote_name}")

    room_users = (await self.highrise.get_room_users()).content
    for room_user, position in room_users:
        try:
            await self.highrise.send_emote(emote_id, room_user.id)
        except:
            await self.highrise.send_whisper(user.id, f"Lo siento, @{room_user.username}, este emote no está disponible o no lo posees.")

async def check_position_and_emote(self: BaseBot) -> None:
    while True:
        try:
            room_users = (await self.highrise.get_room_users()).content
            for room_user, position in room_users:
                # Asegurarse de que `position` sea una instancia de `Position`
                if isinstance(position, Position):
                    x, y, z = position.x, position.y, position.z
                else:
                    # Si `position` no es de tipo `Position`, se omite
                    continue

                # Verificar si la posición del usuario está dentro de los límites
                if (xmin <= x <= xmax) and (ymin <= y <= ymax) and (zmin <= z <= zmax):
                    try:
                        await self.highrise.send_emote(emote_id, room_user.id)
                    except Exception as e:
                        print(f"Error enviando el emote a {room_user.username}: {e}")

        except Exception as e:
            print(f"Error obteniendo usuarios de la sala: {e}")

        await asyncio.sleep(9.5)  # Verificar cada 5 segundos