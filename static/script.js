// JavaScript file that handles
// 1. Creation of the game board
// 2. Establishes the WebSocket conntection (to the Python app.py file) and displays the connection status
// 3. Handles click events (CSS takes care of the animations)

// 1. Create the game board
const boardElement = document.getElementById("totalBoard"); 

function createBoard() {
  for (let boardIndex = 0; boardIndex < 9; boardIndex++) {
    // Creates a container to hold the tic tac toe board in 
    const innerContainer = document.createElement("div");
    innerContainer.className = "boardContainer";
    innerContainer.id = `boardContainer${boardIndex}`;
    // Create smaller tic tac toe board
    const innerGrid = document.createElement("div");
    innerGrid.className = "innerBoard";
    innerGrid.dataset.board = boardIndex;

    for (let cellIndex = 0; cellIndex < 9; cellIndex++) {
      // Create a cell for the current inner_board
      const cellContainer = document.createElement("div");
      cellContainer.className = "cellContainer";

      const cell = document.createElement("div");
      cell.className = "cell";
      cell.id = `cell${boardIndex}${cellIndex}`;
      cell.setAttribute("board", boardIndex);
      cell.setAttribute("cell", cellIndex);
      cell.setAttribute("clickable", "True");
      cell.setAttribute("played", "False");

      cell.addEventListener("click", () => handleMoveAttempt(boardIndex, cellIndex));

      cellContainer.appendChild(cell);
      innerGrid.appendChild(cellContainer);
    }
    innerContainer.appendChild(innerGrid);
    boardElement.appendChild(innerContainer);
  }
}

// 2. Establish websocket connection
var ws = new WebSocket("ws://localhost:8000/ws");
var validMoves, player = 1;
var isLocked = false;  // lock on the board for when the AI is thinking
const header = document.getElementById("header");

ws.onopen = () => {
  console.log("WebSocket connection established");
}

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  // Check if there was an action sent in the data
  if (data.action) {

    // Check if the board is now complete
    console.log(data.result);
    if (!header.classList.contains("complete")) {
      validMoves = JSON.stringify(data.valid_moves);
      player = data.player;
      isLocked = data.locked;
      updateBoard(data.board, data.pos, data.player, data.valid_moves, data.completed_boards, data.locked, data.result);
    }

    if (data.result != null) {
      header.classList.add("complete");
      if (data.result == -1) {
        header.innerText = "Red has won";
      } else if (data.result == 1) {
        header.innerText = "Blue has won";
      } else {
        header.innerText = "The game is a draw";
      }
    }

  } else if (data.init) {
    validMoves = JSON.stringify(data.valid_moves);
  } else {
    alert("Unknwon error: " + data.error);
    console.log(data);
  }
}

ws.onerror = (error) => {
  console.error("Websocket error: ", error);
}

ws.onclose = () => {
  console.log("WebSocket connection closed");
}

function handleMoveAttempt(boardIndex, cellIndex) {
  // Only send if it is a valid move
  const move = JSON.stringify([boardIndex, cellIndex]);
  if (validMoves.indexOf(move) == -1) {
    console.log("Tried to move at an invalid spot");
    return;
  } else if (isLocked) {
    console.log("Attempted to move while the opponent is moving...");
    return;
  }

  // Send the move to the game_logic controller
  ws.send(JSON.stringify({board: boardIndex, pos: cellIndex, isLocked: isLocked}));
}

function updateBoard(boardIndex, cellIndex, player, legalMoves, completedBoards, locked, result) {
  // For all the cells in a completedBoard, mark them as played and make their background colored
  completedBoards.forEach((board) => {
    const completed = document.getElementById(`boardContainer${board[1]}`);
    const color = board[0] === 1 ? "#85ccff" : "#fc9d9d"; // "#c8e8ff" : "#ffc6c6";

    if (board[0] === 1) {
      completed.classList.add("blueWin");
    } else {
      completed.classList.add("redWin");
    }

    // Find all cells that were still playable and update them
    const emptyCells = completed.querySelectorAll(`.cell[played="False"]`);
    emptyCells.forEach((cell) => {
      cell.style.backgroundColor = color;
      cell.style.opacity = "1";
      cell.setAttribute("played", "True");
      cell.setAttribute("Clickable", "False");
    });
  });

  // Default all cells to white and unclickable
  const cannotPlayCells = document.querySelectorAll(`.cell[played="False"]`);
  cannotPlayCells.forEach((cell) => {
    cell.style.backgroundColor = "white";
    cell.style.opacity = "1";
    cell.setAttribute("Clickable", "False");
  });

  if (result == null) {
    // Loop over all legal moves and update their squares
    legalMoves.forEach((move) => {
      const cell = document.getElementById(`cell${move[0]}${move[1]}`);
      cell.style.backgroundColor = "yellow";
      cell.style.opacity = locked ? "0.4" : "1";
      cell.setAttribute("Clickable", locked ? "False" : "True");
    });
  }

  // For each completed board, mark all cells as finished
  // Paint the entire div with the player who won

  // Locate cell that was played
  const playedCell = document.querySelector(`.cell[board="${boardIndex}"][cell="${cellIndex}"]`);
  // Update cell appearance
  playedCell.setAttribute("played", "True");
  playedCell.style.backgroundColor = player === 1 ? "#46d7ff" : "#ff4646"; 
}

createBoard();
