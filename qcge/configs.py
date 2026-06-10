ASSETS_PATH = 'graphics'

GATES = {
    'EMPTY': 0,
    'IDENTITY': 1,
    'X': 2,
    'Y': 3,
    'Z': 4,
    'S': 5,
    'SDG': 6,
    'T': 7,
    'TDG': 8,
    'H': 9,
    'SWAP': 10,
    'CTRL': 11, # "control" part of multi-qubit gate
    'CTRL_LINE': 12 # The Vertical Line between a gate part and a "control" or "swap" part
}

# Tokens accepted by QuantumCircuitGrid(allowed_gates=...) to restrict the player's
# gate palette. "CTRL" = the control modifier (makes a gate controlled); "ROTATE" =
# turning X/Y/Z into RX/RY/RZ via the rotate keys.
SUPPORTED_INPUT_GATES = {
    'X', 'Y', 'Z', 'H', 'S', 'SDG', 'T', 'TDG', 'SWAP', 'CTRL', 'ROTATE',
}

QUANTUM_CIRCUIT_MARKER_MOVE_LEFT = 1
QUANTUM_CIRCUIT_MARKER_MOVE_RIGHT = 2
QUANTUM_CIRCUIT_MARKER_MOVE_UP = 3
QUANTUM_CIRCUIT_MARKER_MOVE_DOWN = 4

# Sizes
QUANTUM_CIRCUIT_TILE_SIZE = 36
GATE_TILE_WIDTH = 24
GATE_TILE_HIEGHT = 24
WIRE_LINE_WIDTH = 1

# Colors 
QUANTUM_CIRCUIT_BG_COLOR = '#444654'
QUANTUM_CIRCUIT_WIRE_COLOR = '#ffffff'
QUANTUM_GATE_PHASE_COLOR = '#97ad40'