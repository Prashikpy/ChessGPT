

import streamlit as st
import chess
import chess.svg
from stockfish import Stockfish





# Initialize Stockfish (adjust path as needed)
try:
    stockfish = Stockfish(path="C:/Users/prash/Python Projects/Python/ChessGpt/stockfish.exe")
    stockfish_available = True
except:
    stockfish_available = False
    st.warning("Stockfish not found. Download from https://stockfishchess.org/ and update the path")

st.title("Chess AI Trainer")


# In[16]:


st.title("Chess AI Trainer")

# Initialize session state
if 'board' not in st.session_state:
    st.session_state.board = chess.Board()
if 'selected_square' not in st.session_state:
    st.session_state.selected_square = None


# In[17]:


# Position analysis functions
def get_position_analysis():
    if not stockfish_available:
        return "Stockfish not available"

    stockfish.set_fen_position(st.session_state.board.fen())
    evaluation = stockfish.get_evaluation()

    if evaluation['type'] == 'cp':  # centipawn
        score = evaluation['value'] / 100
        if score > 0:
            return f"White is better by {score:.2f} pawns"
        elif score < 0:
            return f"Black is better by {abs(score):.2f} pawns"
        else:
            return "Position is equal"
    elif evaluation['type'] == 'mate':
        mate_in = evaluation['value']
        if mate_in > 0:
            return f"White has mate in {mate_in}"
        else:
            return f"Black has mate in {abs(mate_in)}"

    return "Position analysis unavailable"

def get_best_move():
    if not stockfish_available:
        return None

    stockfish.set_fen_position(st.session_state.board.fen())
    best_move = stockfish.get_best_move()
    return best_move

def get_top_moves(num_moves=3):
    if not stockfish_available:
        return []

    stockfish.set_fen_position(st.session_state.board.fen())
    top_moves = stockfish.get_top_moves(num_moves)
    return top_moves


# In[18]:


# Interactive chess board with drag and drop
def create_interactive_board():
    board_html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Interactive Chess Board</title>
        <style>
            .chess-board {{
                border: 2px solid #333;
                width: 480px;
                height: 480px;
                margin: 20px auto;
                display: grid;
                grid-template-columns: repeat(8, 1fr);
                grid-template-rows: repeat(8, 1fr);
            }}
            .square {{
                width: 60px;
                height: 60px;
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 40px;
                cursor: pointer;
                user-select: none;
            }}
            .light {{ background-color: #f0d9b5; }}
            .dark {{ background-color: #b58863; }}
            .selected {{ background-color: #ffff00 !important; }}
            .legal-move {{ background-color: #90EE90 !important; }}
            .last-move {{ background-color: #ffff99 !important; }}
            .piece {{
                transition: all 0.2s ease;
            }}
            .piece:hover {{
                transform: scale(1.1);
            }}
            #move-input {{
                margin: 20px;
                padding: 10px;
                font-size: 16px;
                width: 200px;
            }}
            #status {{
                text-align: center;
                font-size: 18px;
                margin: 10px;
                font-weight: bold;
            }}
            .button {{
                margin: 5px;
                padding: 10px 20px;
                font-size: 16px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }}
            .button:hover {{
                background-color: #45a049;
            }}
        </style>
    </head>
    <body>
        <div id="status">White to move</div>
        <div class="chess-board" id="board"></div>
        <div style="text-align: center;">
            <input type="text" id="move-input" placeholder="Enter move (e.g., e2e4)" />
            <button class="button" onclick="makeTextMove()">Make Move</button>
            <button class="button" onclick="resetBoard()">Reset</button>
            <button class="button" onclick="undoMove()">Undo</button>
        </div>

        <script>
            let board = new Array(8).fill().map(() => new Array(8).fill(null));
            let selectedSquare = null;
            let gameHistory = [];
            let currentPlayer = 'white';

            // Initialize board with starting position
            const startingPosition = [
                ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
                ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
                [null, null, null, null, null, null, null, null],
                [null, null, null, null, null, null, null, null],
                [null, null, null, null, null, null, null, null],
                [null, null, null, null, null, null, null, null],
                ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
                ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
            ];

            // Unicode chess pieces
            const pieceSymbols = {{
                'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
                'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
            }};

            function initializeBoard() {{
                board = JSON.parse(JSON.stringify(startingPosition));
                renderBoard();
                updateStatus();
            }}

            function renderBoard() {{
                const boardElement = document.getElementById('board');
                boardElement.innerHTML = '';

                for (let row = 0; row < 8; row++) {{
                    for (let col = 0; col < 8; col++) {{
                        const square = document.createElement('div');
                        square.className = 'square ' + ((row + col) % 2 === 0 ? 'light' : 'dark');
                        square.dataset.row = row;
                        square.dataset.col = col;

                        const piece = board[row][col];
                        if (piece) {{
                            square.innerHTML = `<span class="piece">${{pieceSymbols[piece] || piece}}</span>`;
                        }}

                        square.addEventListener('click', () => handleSquareClick(row, col));
                        boardElement.appendChild(square);
                    }}
                }}
            }}

            function handleSquareClick(row, col) {{
                const square = document.querySelector(`[data-row="${{row}}"][data-col="${{col}}"]`);

                if (selectedSquare) {{
                    const fromRow = selectedSquare.row;
                    const fromCol = selectedSquare.col;

                    if (fromRow === row && fromCol === col) {{
                        // Deselect
                        clearSelection();
                        return;
                    }}

                    // Try to make move
                    if (isValidMove(fromRow, fromCol, row, col)) {{
                        makeMove(fromRow, fromCol, row, col);
                        clearSelection();
                    }} else {{
                        clearSelection();
                        if (board[row][col]) {{
                            selectSquare(row, col);
                        }}
                    }}
                }} else {{
                    if (board[row][col]) {{
                        selectSquare(row, col);
                    }}
                }}
            }}

            function selectSquare(row, col) {{
                selectedSquare = {{row, col}};
                const square = document.querySelector(`[data-row="${{row}}"][data-col="${{col}}"]`);
                square.classList.add('selected');

                // Highlight possible moves (basic implementation)
                highlightLegalMoves(row, col);
            }}

            function clearSelection() {{
                document.querySelectorAll('.square').forEach(square => {{
                    square.classList.remove('selected', 'legal-move');
                }});
                selectedSquare = null;
            }}

            function highlightLegalMoves(row, col) {{
                // Basic move highlighting - can be enhanced
                const piece = board[row][col];
                if (!piece) return;

                // Simple pawn moves
                if (piece === 'P') {{
                    if (row > 0 && !board[row-1][col]) {{
                        highlightSquare(row-1, col);
                        if (row === 6 && !board[row-2][col]) {{
                            highlightSquare(row-2, col);
                        }}
                    }}
                }} else if (piece === 'p') {{
                    if (row < 7 && !board[row+1][col]) {{
                        highlightSquare(row+1, col);
                        if (row === 1 && !board[row+2][col]) {{
                            highlightSquare(row+2, col);
                        }}
                    }}
                }}
            }}

            function highlightSquare(row, col) {{
                const square = document.querySelector(`[data-row="${{row}}"][data-col="${{col}}"]`);
                if (square) {{
                    square.classList.add('legal-move');
                }}
            }}

            function isValidMove(fromRow, fromCol, toRow, toCol) {{
                // Basic validation - can be enhanced with proper chess rules
                const piece = board[fromRow][fromCol];
                if (!piece) return false;

                // Check if it's the right player's turn
                const isWhitePiece = piece === piece.toUpperCase();
                if ((currentPlayer === 'white' && !isWhitePiece) || (currentPlayer === 'black' && isWhitePiece)) {{
                    return false;
                }}

                // Basic move validation for pawns
                if (piece === 'P') {{
                    if (fromCol === toCol && fromRow > toRow && !board[toRow][toCol]) {{
                        return fromRow - toRow === 1 || (fromRow === 6 && toRow === 4);
                    }}
                }} else if (piece === 'p') {{
                    if (fromCol === toCol && fromRow < toRow && !board[toRow][toCol]) {{
                        return toRow - fromRow === 1 || (fromRow === 1 && toRow === 3);
                    }}
                }}

                return true; // Simplified - accept other moves for now
            }}

            function makeMove(fromRow, fromCol, toRow, toCol) {{
                const piece = board[fromRow][fromCol];
                gameHistory.push(JSON.parse(JSON.stringify(board)));

                board[toRow][toCol] = piece;
                board[fromRow][fromCol] = null;

                currentPlayer = currentPlayer === 'white' ? 'black' : 'white';
                renderBoard();
                updateStatus();

                // Send move to Streamlit (if needed)
                const move = String.fromCharCode(97 + fromCol) + (8 - fromRow) + 
                            String.fromCharCode(97 + toCol) + (8 - toRow);
                window.parent.postMessage({{type: 'chess_move', move: move}}, '*');
            }}

            function makeTextMove() {{
                const moveInput = document.getElementById('move-input');
                const move = moveInput.value.toLowerCase();

                if (move.length === 4) {{
                    const fromCol = move.charCodeAt(0) - 97;
                    const fromRow = 8 - parseInt(move[1]);
                    const toCol = move.charCodeAt(2) - 97;
                    const toRow = 8 - parseInt(move[3]);

                    if (isValidMove(fromRow, fromCol, toRow, toCol)) {{
                        makeMove(fromRow, fromCol, toRow, toCol);
                        moveInput.value = '';
                    }} else {{
                        alert('Invalid move!');
                    }}
                }}
            }}

            function resetBoard() {{
                board = JSON.parse(JSON.stringify(startingPosition));
                gameHistory = [];
                currentPlayer = 'white';
                clearSelection();
                renderBoard();
                updateStatus();
            }}

            function undoMove() {{
                if (gameHistory.length > 0) {{
                    board = gameHistory.pop();
                    currentPlayer = currentPlayer === 'white' ? 'black' : 'white';
                    clearSelection();
                    renderBoard();
                    updateStatus();
                }}
            }}

            function updateStatus() {{
                const status = document.getElementById('status');
                status.textContent = currentPlayer === 'white' ? 'White to move' : 'Black to move';
            }}

            // Initialize the board
            initializeBoard();

            // Handle text input
            document.getElementById('move-input').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') {{
                    makeTextMove();
                }}
            }});
        </script>
    </body>
    </html>
    '''
    return board_html


# In[21]:


# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Chess Board")


    # Move input
    move_input = st.text_input("Enter your move (e.g., e2e4):", key="move_input")

    if st.button("Make Move"):
        try:
            move = chess.Move.from_uci(move_input)
            if move in st.session_state.board.legal_moves:
                st.session_state.board.push(move)
                st.success(f"Move {move_input} played!")
                st.rerun()
            else:
                st.error("Invalid move!")
        except:
            st.error("Invalid move format! Use format like 'e2e4'")

    if st.button("Reset Game"):
        st.session_state.board = chess.Board()
        st.rerun()

with col2:
    st.subheader("Game Info")
    st.write(f"Turn: {'White' if st.session_state.board.turn else 'Black'}")
    st.write(f"Move number: {st.session_state.board.fullmove_number}")

    if st.session_state.board.is_check():
        st.warning("Check!")

    if st.session_state.board.is_checkmate():
        st.error("Checkmate!")
    elif st.session_state.board.is_stalemate():
        st.info("Stalemate!")

    # Show last move
    if st.session_state.board.move_stack:
        last_move = st.session_state.board.move_stack[-1]
        st.write(f"Last move: {last_move}")

    # Position Analysis
    st.subheader("Position Analysis")
    if stockfish_available:
        analysis = get_position_analysis()
        st.write(f"Evaluation: {analysis}")

        best_move = get_best_move()
        if best_move:
            st.write(f"Best move: {best_move}")

        # Show top 3 moves
        if st.button("Show Top 3 Moves"):
            top_moves = get_top_moves(3)
            st.write("**Top Moves:**")
            for i, move_info in enumerate(top_moves, 1):
                move = move_info['Move']
                centipawn = move_info['Centipawn']
                st.write(f"{i}. {move} ({centipawn/100:.2f})")
    else:
        st.write("Install Stockfish for position analysis")

    # Quick actions
    st.subheader("Quick Actions")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Undo Move") and st.session_state.board.move_stack:
            st.session_state.board.pop()
            st.rerun()
    with col_b:
        if st.button("Computer Move") and stockfish_available:
            best_move = get_best_move()
            if best_move:
                move = chess.Move.from_uci(best_move)
                st.session_state.board.push(move)
                st.rerun()


# In[14]:


# Simple chat interface
st.subheader("Chat with Chess AI")
user_question = st.text_input("Ask me about chess:")
if user_question:
    # For now, just echo back - we'll add real AI in Phase 2
    st.write(f"AI: You asked about '{user_question}'. I'll be able to answer chess questions in the next phase!")


# In[19]:


# Game History
st.subheader("Game History")
col_hist1, col_hist2 = st.columns(2)

with col_hist1:
    st.write("**Move History:**")
    moves = []
    temp_board = chess.Board()
    for i, move in enumerate(st.session_state.board.move_stack):
        if i % 2 == 0:
            move_num = (i // 2) + 1
            moves.append(f"{move_num}. {temp_board.san(move)}")
        else:
            moves[-1] += f" {temp_board.san(move)}"
        temp_board.push(move)

    for move in moves:
        st.write(move)

with col_hist2:
    st.write("**Game PGN:**")
    if st.session_state.board.move_stack:
        game = chess.pgn.Game()
        game.setup(chess.Board())
        node = game
        for move in st.session_state.board.move_stack:
            node = node.add_variation(move)

        pgn_string = str(game)
        st.text_area("PGN:", pgn_string, height=100)
    else:
        st.write("No moves yet")


# In[ ]:





# In[ ]:




