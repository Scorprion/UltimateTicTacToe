from game_logic import UltimateTicTacToe
from agents import Human, MiniMax, Random
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import asyncio

app = FastAPI()
app.mount('/static', StaticFiles(directory='static', html=True), name='static')

# Create game board
bot = MiniMax(2, n_sims=250, verbose=False)

async def process_computer_move(websocket: WebSocket, uttt):
    # Calculate AI move in a separate task
    move = bot.get_move(uttt)
    uttt.play(*move)

    # Send AI move info and unlock the board to the user again
    await websocket.send_json({
        'action': 'computer_move',
        'board': move[0],
        'pos': move[1],
        'player': -uttt.get_turn(), 
        'valid_moves': uttt.get_legal_moves(uttt.current_board),
        'completed_boards': uttt.completed_boards(),
        'result': uttt.get_result(), 
        'win_chance': bot.win_percent,
        'locked': False
     })

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    uttt = UltimateTicTacToe()
    await websocket.accept()  # wait until the websocket connection has been established

    # Send initial message to instatiate the board
    # TODO: Send board representation to instantiate the board
    await websocket.send_json({'init': True, 'player': uttt.get_turn(), 'valid_moves': uttt.get_legal_moves(uttt.current_board)})
    while True:

        # update the board logic
        data = await websocket.receive_json()

        # If the board is locked, we are currently waiting for the AI to complete its move
        # This is a double safeguard since we check for it before sending the req as well
        if (data.get('locked', False)):
            continue

        move = (data['board'], data['pos'])
        
        uttt.play(*move);

        # notify the front end that the move was valid
        await websocket.send_json({'action': 'player_move', 
                                   'board': data['board'], 
                                   'pos': data['pos'], 
                                   'player': -uttt.get_turn(), 
                                   'valid_moves': uttt.get_legal_moves(uttt.current_board),
                                   'completed_boards': uttt.completed_boards(),
                                   'result': uttt.get_result(),
                                   'locked': True
                                   })
        
        # Run AI in background while we update the board
        asyncio.create_task(process_computer_move(websocket, uttt))
