import os
import json
import urllib.request
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ.get('API_ID'))
API_HASH = os.environ.get('API_HASH')
SESSION_STRING = os.environ.get('SESSION_STRING')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CANAL_ID = int(os.environ.get('CANAL_ID'))

PALABRAS_CLAVE = ["silla", "arrancador", "portatil", "aspiradora"]

def enviar_alerta_bot(texto_alerta):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    datos = {
        "chat_id": CANAL_ID,
        "text": texto_alerta
        # Quitamos parse_mode para evitar cualquier error de formato con caracteres especiales
    }
    datos_json = json.dumps(datos).encode('utf-8')
    peticion = urllib.request.Request(url, data=datos_json, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(peticion, timeout=5) as respuesta:
            if respuesta.status == 200:
                print("[ÉXITO] Alerta enviada al móvil.")
    except Exception as e:
        print(f"[ERROR BOT] {e}")

async def main():
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.start()
    
    print("Conectado a Telegram. Buscando chats...")
    
    async for dialog in client.iter_dialogs(limit=40):
        if dialog.id == CANAL_ID:
            continue
            
        print(f"Revisando chat: '{dialog.title}'")
            
        async for message in client.iter_messages(dialog.id, limit=10):
            if not message.message:
                continue
                
            texto_mensaje = message.message
            texto_minusculas = texto_mensaje.lower()
            
            palabras_encontradas = [p for p in PALABRAS_CLAVE if p in texto_minusculas]
            
            if palabras_encontradas:
                print(f"¡COINCIDENCIA ENCONTRADA en '{dialog.title}': {palabras_encontradas}!")
                nombre_canal_origen = dialog.title or "Canal/Grupo"
                coincidencias_str = ", ".join(palabras_encontradas)
                
                link_mensaje = ""
                if dialog.entity and hasattr(dialog.entity, 'username') and dialog.entity.username:
                    link_mensaje = f"https://t.me/{dialog.entity.username}/{message.id}"
                
                alerta = (
                    f"⚠️ ¡Palabra clave detectada!\n\n"
                    f"📌 Origen: {nombre_canal_origen}\n"
                    f"🔍 Encontrada(s): {coincidencias_str}\n"
                )
                if link_mensaje:
                    alerta += f"🔗 Ir al mensaje: {link_mensaje}\n\n"
                else:
                    alerta += f"🔒 (Chat privado)\n\n"
                
                alerta += f"💬 Mensaje:\n{texto_mensaje}"
                
                enviar_alerta_bot(alerta)
                break
                
    await client.disconnect()
    print("Revisión completada.")

if __name__ == '__main__':
    asyncio.run(main())
