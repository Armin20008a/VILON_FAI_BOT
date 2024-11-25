import json
import os
from typing import List, Dict
import asyncio
from datetime import datetime

class SubscriptionManager:
    def __init__(self):
        self.subscribers_file = "subscribers.json"
        self.subscribers = self.load_subscribers()
        
    def load_subscribers(self) -> Dict:
        """Carga la lista de suscriptores del archivo"""
        try:
            if os.path.exists(self.subscribers_file):
                with open(self.subscribers_file, 'r') as file:
                    return json.load(file)
            return {"subscribers": [], "admin": "Joshe11"}
        except Exception as e:
            print(f"Error loading subscribers: {e}")
            return {"subscribers": [], "admin": "Joshe11"}
    
    def save_subscribers(self) -> None:
        """Guarda la lista de suscriptores en el archivo"""
        try:
            with open(self.subscribers_file, 'w') as file:
                json.dump(self.subscribers, file, indent=4)
        except Exception as e:
            print(f"Error saving subscribers: {e}")

    async def show_menu(self, bot, user_id: str, conversation_id: str) -> None:
        """Muestra el menú de opciones al usuario"""
        menu = """
        🌟 ¡Bienvenido al Sistema de Suscripción! 🌟
        
        Comandos disponibles:
        /sub - Suscribirse para recibir noticias
        /unsub - Cancelar suscripción
        /status - Ver estado de suscripción
        
        ¡Suscríbete para no perderte ninguna novedad!
        """
        await bot.highrise.send_message(conversation_id, menu)

    async def handle_subscription(self, bot, user_id: str, conversation_id: str) -> None:
        """Maneja la suscripción de un usuario"""
        if user_id not in self.subscribers["subscribers"]:
            self.subscribers["subscribers"].append(user_id)
            self.save_subscribers()
            await bot.highrise.send_message(conversation_id, "¡Te has suscrito exitosamente! 🎉")
        else:
            await bot.highrise.send_message(conversation_id, "¡Ya estás suscrito! 📫")

    async def handle_unsubscription(self, bot, user_id: str, conversation_id: str) -> None:
        """Maneja la cancelación de suscripción"""
        if user_id in self.subscribers["subscribers"]:
            self.subscribers["subscribers"].remove(user_id)
            self.save_subscribers()
            await bot.highrise.send_message(conversation_id, "Has cancelado tu suscripción. ¡Esperamos verte pronto! 👋")
        else:
            await bot.highrise.send_message(conversation_id, "No estabas suscrito. 🤔")

    async def handle_admin_message(self, bot, user_id: str, conversation_id: str) -> None:
        """Maneja el envío de mensajes administrativos"""
        if user_id == self.subscribers["admin"]:
            await bot.highrise.send_message(conversation_id, "Por favor, ingresa el mensaje que quieres enviar a todos los suscriptores:")
            # Aquí necesitaremos implementar la lógica para esperar la respuesta
        else:
            await bot.highrise.send_message(conversation_id, "No tienes permisos de administrador. 🚫")

    async def broadcast_message(self, bot, message: str) -> None:
        """Envía un mensaje a todos los suscriptores"""
        for subscriber_id in self.subscribers["subscribers"]:
            try:
                # Aquí necesitaremos implementar la lógica para crear conversaciones
                # y enviar mensajes a cada suscriptor
                pass
            except Exception as e:
                print(f"Error sending message to {subscriber_id}: {e}")