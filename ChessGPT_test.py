#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import chess
import chess.svg
from stockfish import Stockfish
import streamlit.components.v1 as components


# In[2]:


# Initialize Stockfish (adjust path as needed)
try:
    stockfish = Stockfish(path="C:/Users/prash/Python Projects/Python/ChessGpt/stockfish.exe")
    stockfish_available = True
except:
    stockfish_available = False
    st.warning("Stockfish not found. Download from https://stockfishchess.org/ and update the path")

st.title("Chess AI Trainer")


# In[3]:


# Initialize session state
if 'board' not in st.session_state:
    st.session_state.board = chess.Board()
if 'selected_square' not in st.session_state:
    st.session_state.selected_square = None


# In[4]:


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

def create_interactive_board():
    # Convert chess board to FEN and create board state
    fen = st.session_state.board.fen()
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
            .piece {{
                transition: all 0.2s ease;
            }}
            .piece:hover {{
                transform: scale(1.1);
            }}
        </style>
    </head>
    <body>
        <div class="chess-board" id="board"></div>

        <script>
            // Unicode chess pieces
            const pieceSymbols = {{
                'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
                'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
            }};

            function fenToBoard(fen) {{
                const position = fen.split(' ')[0];
                const rows = position.split('/');
                const board = [];

                for (let row of rows) {{
                    const boardRow = [];
                    for (let char of row) {{
                        if (isNaN(char)) {{
                            boardRow.push(char);
                        }} else {{
                            for (let i = 0; i < parseInt(char); i++) {{
                                boardRow.push(null);
                            }}
                        }}
                    }}
                    board.push(boardRow);
                }}
                return board;
            }}

            function renderBoard() {{
                const board = fenToBoard('{fen}');
                const boardElement = document.getElementById('board');
                boardElement.innerHTML = '';

                for (let row = 0; row < 8; row++) {{
                    for (let col = 0; col < 8; col++) {{
                        const square = document.createElement('div');
                        square.className = 'square ' + ((row + col) % 2 === 0 ? 'light' : 'dark');

                        const piece = board[row][col];
                        if (piece) {{
                            square.innerHTML = `<span class="piece">${{pieceSymbols[piece] || piece}}</span>`;
                        }}

                        boardElement.appendChild(square);
                    }}
                }}
            }}

            renderBoard();
        </script>
    </body>
    </html>
    '''
    return board_html


# In[5]:


# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Chess Board")

    # Choose display method
    display_method = st.radio("Board Display:", ["SVG (Static)", "HTML (Interactive)"], horizontal=True)

    if display_method == "SVG (Static)":
        # Display using chess.svg
        board_svg = chess.svg.board(board=st.session_state.board, size=400)
        st.image(board_svg, width=400)
    else:
        # Display using interactive HTML
        board_html = create_interactive_board()
        components.html(board_html, height=600)

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


# In[6]:


# Simple chat interface
st.subheader("Chat with Chess AI")
user_question = st.text_input("Ask me about chess:")
if user_question:
    st.write(f"AI: You asked about '{user_question}'. I'll be able to answer chess questions in the next phase!")

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




