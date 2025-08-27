import os
import asyncio
import websockets
import json

PORT = int(os.environ.get("PORT", 10000))  # Render escolhe a porta

clientes = set()

async def handler(ws, path):
    clientes.add(ws)
    try:
        async for message in ws:
            data = json.loads(message)
            
            if data.get("acao") == "chat":
                await broadcast({"chat": f"Jogador: {data['texto']}"})
            
            elif data.get("acao") == "escudo":
                await ws.send(json.dumps({"msg": "🛡️ Escudo ativado!"}))
            
            elif data.get("acao") == "comprar":
                await ws.send(json.dumps({"msg": "💰 Você comprou moedas!"}))
    
    except Exception as e:
        print("Erro:", e)
    
    finally:
        clientes.remove(ws)

async def broadcast(msg):
    for c in list(clientes):
        try:
            await c.send(json.dumps(msg))
        except:
            clientes.remove(c)

async def main():
    print(f"Servidor iniciado na porta {PORT}")
    async with websockets.serve(handler, "0.0.0.0", PORT):
        await asyncio.Future()  # roda para sempre

asyncio.run(main())
