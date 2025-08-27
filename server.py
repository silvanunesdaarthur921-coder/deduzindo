import asyncio
import websockets
import json
import os

jogadores = {}
moedas = {}
pontos = {}
escudo = {}

async def registrar(ws):
    nome = f"Jogador{len(jogadores)+1}"
    jogadores[ws] = nome
    moedas[nome] = 3
    pontos[nome] = 1
    escudo[nome] = False
    await ws.send(json.dumps({"msg": f"Bem-vindo {nome}!"}))
    return nome

async def servidor(ws):
    nome = await registrar(ws)
    try:
        async for msg in ws:
            data = json.loads(msg)
            
            if data["acao"] == "chat":
                for player in jogadores:
                    await player.send(json.dumps({"chat": f"{nome}: {data['texto']}"}))
            
            if data["acao"] == "escudo":
                if moedas[nome] > 0:
                    moedas[nome] -= 1
                    escudo[nome] = True
                    await ws.send(json.dumps({"msg": "Você ativou seu ESCUDO!"}))
                else:
                    await ws.send(json.dumps({"msg": "Sem moedas!"}))
            
            if data["acao"] == "comprar":
                if pontos[nome] > 0:
                    pontos[nome] -= 1
                    moedas[nome] += 1
                    await ws.send(json.dumps({"msg": "Você comprou 1 moeda!"}))
                else:
                    await ws.send(json.dumps({"msg": "Sem pontos para comprar!"}))

    except:
        print(f"{nome} saiu.")
        del jogadores[ws]

async def main():
    port = int(os.environ.get("PORT", 10000))  # Render usa a porta como variável
    async with websockets.serve(servidor, "0.0.0.0", port):
        print(f"Servidor rodando na porta {port}")
        await asyncio.Future()

asyncio.run(main())
