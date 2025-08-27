import os
import asyncio
import websockets
import json

PORT = int(os.environ.get("PORT", 10000))
clientes = set()
jogadores = {}  # ws -> nome
moedas = {}
escudo = {}

async def handler(ws, path):
    nome = f"Jogador{len(clientes)+1}"
    clientes.add(ws)
    jogadores[ws] = nome
    moedas[nome] = 3
    escudo[nome] = False

    # Mensagem de boas-vindas
    await ws.send(json.dumps({"msg": f"Bem-vindo {nome}! Moedas: {moedas[nome]}"}))

    try:
        async for message in ws:
            data = json.loads(message)

            if data.get("acao") == "chat":
                await broadcast({"chat": f"{nome}: {data['texto']}"})

            elif data.get("acao") == "escudo":
                if moedas[nome] > 0:
                    moedas[nome] -= 1
                    escudo[nome] = True
                    await ws.send(json.dumps({"msg": "🛡️ Escudo ativado!"}))
                else:
                    await ws.send(json.dumps({"msg": "❌ Sem moedas para ativar escudo!"}))

            elif data.get("acao") == "comprar":
                moedas[nome] += 1
                await ws.send(json.dumps({"msg": f"💰 Você comprou 1 moeda! Total: {moedas[nome]}"}))

    except websockets.ConnectionClosedOK:
        pass
    except Exception as e:
        print("Erro:", e)
    finally:
        clientes.remove(ws)
        del jogadores[ws]
        del moedas[nome]
        del escudo[nome]

async def broadcast(msg):
    for c in list(clientes):
        try:
            await c.send(json.dumps(msg))
        except:
            clientes.remove(c)

async def main():
    print(f"Servidor rodando na porta {PORT}")
    async with websockets.serve(handler, "0.0.0.0", PORT):
        await asyncio.Future()

asyncio.run(main())
