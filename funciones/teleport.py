from highrise import BaseBot, Position
from highrise.models import User

PREDEFINED_COORDINATES = {
    "paseito1": Position(0.5, 1.5, 29.5),
    "paseito2": Position(2.0, 0.0, 4.5),
    "paseito3": Position(9.5, 11.0, 7.5),
    "paseito4": Position(0.5, 8.25, 1.5),
    "paseito5": Position(16.5, 13.5, 19),
    "paseito7": Position(0.5, 6.75, 29.5),
    "paseito6": Position(14.5, 2.25, 17.5),
    "paseito8": Position(16.5, 5, 23.5),
    "paseito9": Position(11.0, 2.25, 9.0),
    "paseito10": Position(15.5, 12.0, 8.0),
    "paseito11": Position(16.5, 18.5, 2.0),
}


async def teleporter(self: BaseBot, user: User, message: str) -> None:
    user_privileges = await self.highrise.get_room_privilege(user.id)
    if (not user_privileges.moderator) and (user.username != "Joshe11"):
        await self.highrise.send_whisper(user.id, "Función sólo para moderadores.")
        return
    try:
        command_parts = message.strip().split()
        command = command_parts[0].lower()  # Convert command to lowercase

        if command in PREDEFINED_COORDINATES:
            dest = PREDEFINED_COORDINATES[command]

            if len(command_parts) == 1:
                await self.highrise.teleport(user_id=user.id, dest=dest)
                await self.highrise.send_whisper(user.id, f"Ooh!! Buen viaje {user.username}")

            elif len(command_parts) == 2 and command_parts[1].startswith("@"):
                username = command_parts[1][1:].lower(
                )  # Convert mentioned username to lowercase

                room_users = (await self.highrise.get_room_users()).content
                user_id = None

                for room_user, _ in room_users:
                    if room_user.username.lower() == username:
                        user_id = room_user.id
                        break

                if user_id is not None:
                    await self.highrise.teleport(user_id=user_id, dest=dest)
                    await self.highrise.send_whisper(user.id,
                        f"{username} ha sido teletransportado")
                else:
                    await self.highrise.send_whisper(user.id,
                        f"Usuario {username} no encontrado.")
            else:
                await self.highrise.send_whisper(user.id,
                    f"Comando '{command}' no reconocido o formato incorrecto. Usa '{command}' o '{command} @user'")

    except Exception as e:
        await self.highrise.chat(f"Ocurrió un error: {str(e)}")