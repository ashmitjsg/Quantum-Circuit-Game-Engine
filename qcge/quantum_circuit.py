import math

import pygame

from pygame.image import load as loadImage
from qcge import configs
from qcge.configs import *
from qcge.ir import CircuitIR
from qcge.backends import get_backend


class QuantumCircuitGridBackground(pygame.sprite.Sprite):
    def __init__(self, qc_grid_model, background_color, wire_color, tile_size, wire_line_width):
        super().__init__()
        self.qc_grid_model = qc_grid_model
        self.tile_size = tile_size 
        self.wire_color = wire_color
        self.wire_line_width = wire_line_width
        self.background_color = background_color
        self.width = self.tile_size * (self.qc_grid_model.num_columns + 2)
        self.height = self.tile_size * (self.qc_grid_model.num_qubits + 1)

        # BACKGROUND SURFACE
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.background_color)
        self.rect = self.image.get_rect()
        self.rect.inflate_ip(-self.wire_line_width, -self.wire_line_width)

        self.run()

    def draw_qubit_wires(self):
        for wire in range(self.qc_grid_model.num_qubits):
            x_start = self.tile_size * 0.5
            x_end = self.width - (self.tile_size * 0.5)
            y = (wire + 1) * self.tile_size 
            pygame.draw.line(
                self.image, 
                self.wire_color, 
                (x_start, y), 
                (x_end, y),
                self.wire_line_width
            )

    def run(self):
        # Drawing
        pygame.draw.rect(self.image, self.wire_color, self.rect, self.wire_line_width)
        self.draw_qubit_wires()

class QuantumCircuitGridMarker(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = loadImage(f"{configs.ASSETS_PATH}/circuit-grid-cursor.png").convert_alpha()
        self.rect = self.image.get_rect()

class QuantumCircuitGridNode:
    def __init__(self, gate_type, rotation_angle = 0.0, first_ctrl = -1, second_ctrl = -1, swap = -1):
        self.gate_type = gate_type # What Gate is at this node
        self.rotation_angle = rotation_angle # If radian != 0 then this node have a U(theta) gate; Ex:- RX, RY, RZ
        self.first_ctrl = first_ctrl # If first_ctrl > 0; then this node is a controlled gate with one control node # It's value will be the wire number on which the first control is placed
        self.second_ctrl = second_ctrl # If second_ctrl > 0; then this node is a controlled gate with two control nodes # It's value will be the wire number on which the second control is placed
        self.swap = swap # If swap != -1 then this node have a swap gate

    def __str__(self):
        string = "Type: " + str(self.gate_type)
        string += ", rotation_angle: " + str(self.rotation_angle) if self.rotation_angle != 0 else ""
        string += ", ctrl_a: " + str(self.first_ctrl) if self.first_ctrl != -1 else ""
        string += ", ctrl_b: " + str(self.second_ctrl) if self.second_ctrl != -1 else ""
        return string

class QuantumCircuitGridGate(pygame.sprite.Sprite):
    def __init__(self, qc_grid_model, wire, column, gate_dimensions, gate_phase_angle_color):
        super().__init__()
        self.qc_grid_model = qc_grid_model
        
        # Gate Position
        self.wire = wire
        self.column = column

        self.gate_dimensions = gate_dimensions
        self.gate_phase_angle_color = gate_phase_angle_color

        self.run()
    
    def import_gate(self, gate_name, colorkey = None):
        gate_image_folder = configs.ASSETS_PATH
        gate_image = loadImage(f"{gate_image_folder}/{gate_name}")
        if colorkey is not None:
            if colorkey == -1:
                colorkey = gate_image.get_at((0,0))
            gate_image.set_colorkey(colorkey)
        return gate_image, gate_image.get_rect()
    
    def load_gate(self):
        gate = self.qc_grid_model.get_gate_at_node(self.wire, self.column)
        
        if gate == GATES['IDENTITY']:
            self.image, self.rect = self.import_gate("iden_gate.png", -1)    
        
        elif gate == GATES['X']:
            node = self.qc_grid_model.get_node(self.wire, self.column)
            # Check if this is a CNOT Gate
            if node.first_ctrl >= 0 or node.second_ctrl >= 0:
                ctrl_wires = [c for c in (node.first_ctrl, node.second_ctrl) if c >= 0]
                if self.wire > max(ctrl_wires): # If target wire is below control wire
                    self.image, self.rect = self.import_gate("not_gate_below_ctrl.png", -1)
                else: # If target wire is above control wire
                    self.image, self.rect = self.import_gate("not_gate_above_ctrl.png", -1)
            elif node.rotation_angle != 0: # Else If this is a RX Gate
                self.image, self.rect = self.import_gate("rx_gate.png", -1)
                # Draw the value of theta as an arc of a circle 
                pygame.draw.arc(self.image, self.gate_phase_angle_color, self.rect, 0, node.rotation_angle % (2 * math.pi), 4)
            else: # Else if this is a normal X Gate
                self.image, self.rect = self.import_gate("x_gate.png", -1)
        
        elif gate == GATES['Y']:
            node = self.qc_grid_model.get_node(self.wire, self.column)
            # Check if this is a RY Gate
            if node.rotation_angle != 0:
                self.image, self.rect = self.import_gate("ry_gate.png", -1)
                # Draw the value of theta as an arc of a circle 
                pygame.draw.arc(self.image, self.gate_phase_angle_color, self.rect, 0, node.rotation_angle % (2 * math.pi), 4)
            else: # Else if this is a normal Y Gate
                self.image, self.rect = self.import_gate("y_gate.png", -1)
        
        elif gate == GATES['Z']:
            node = self.qc_grid_model.get_node(self.wire, self.column)
            # Check if this is a RY Gate
            if node.rotation_angle != 0:
                self.image, self.rect = self.import_gate("rz_gate.png", -1)
                # Draw the value of theta as an arc of a circle 
                pygame.draw.arc(self.image, self.gate_phase_angle_color, self.rect, 0, node.rotation_angle % (2 * math.pi), 4)
            else: # Else if this is a normal Y Gate
                self.image, self.rect = self.import_gate("z_gate.png", -1)
        
        elif gate == GATES['S']:
            self.image, self.rect = self.import_gate("s_gate.png", -1)
        
        elif gate == GATES['SDG']:
            self.image, self.rect = self.import_gate("sdg_gate.png", -1)
        
        elif gate == GATES['T']:
            self.image, self.rect = self.import_gate("t_gate.png", -1)
        
        elif gate == GATES['TDG']:
            self.image, self.rect = self.import_gate("tdg_gate.png", -1)
        
        elif gate == GATES['H']:
            self.image, self.rect = self.import_gate("h_gate.png", -1)
        
        elif gate == GATES['SWAP']:
            self.image, self.rect = self.import_gate("swap_gate.png", -1)
        
        elif gate == GATES['CTRL']:
            # Check if the target wire is above the control wire
            if self.wire > self.qc_grid_model.get_wire_for_control_node_at(self.wire, self.column):
                self.image, self.rect = self.import_gate("ctrl_gate_bottom_wire.png", -1)
            else: # if the target wire is above the control wire
                self.image, self.rect = self.import_gate("ctrl_gate_top_wire.png", -1)
        
        elif gate == GATES['CTRL_LINE']:
            self.image, self.rect = self.import_gate("ctrl_line_gate.png", -1)
        
        else: # If the node is empty
            # Draw a transparent block, i.e., empty gate/node
            self.image = pygame.Surface([self.gate_dimensions[0], self.gate_dimensions[1]])
            self.image.set_alpha(0)
            self.rect = self.image.get_rect()
        
        self.image.convert()

    def run(self):
        self.load_gate()

    def update(self):
        # Re-read this cell's node and refresh the sprite image every frame, so
        # gates placed/removed after construction actually render. (pygame's
        # Group.update() calls this; without it the image would never change.)
        self.load_gate()

class QuantumCircuitGridModel():
    def __init__(self, num_qubits, num_columns):
        self.num_qubits = num_qubits
        self.num_columns = num_columns
        # 2D grid of nodes; 0 marks an empty cell (kept numpy-free so the engine
        # imports cleanly in a pygbag/WebAssembly build, where loading numpy
        # breaks the SDL display).
        self.nodes = [[0 for _ in range(self.num_columns)] for _ in range(self.num_qubits)]
    
    def __str__(self):
        string = "CircuitGridModel:\n"
        for wire in range(self.num_qubits):
            row_values = [str(self.get_gate_at_node(wire, column)) for column in range(self.num_columns)]
            string += ", ".join(row_values) + "\n"
        return string

    def set_node(self, wire, column, qc_grid_node):
        self.nodes[wire][column] = QuantumCircuitGridNode(
            qc_grid_node.gate_type,
            qc_grid_node.rotation_angle,
            qc_grid_node.first_ctrl,
            qc_grid_node.second_ctrl,
            qc_grid_node.swap
        )
    
    def get_node(self, wire, column):
        return self.nodes[wire][column]

    def get_gate_at_node(self, wire, column):
        node = self.nodes[wire][column]
        
        if node and node.gate_type != GATES['EMPTY']: # If the node is already occupied
            return node.gate_type # Return the gate occupying the node
        
        column_nodes = [self.nodes[w][column] for w in range(self.num_qubits)]
        for index, other_node in enumerate(column_nodes):
            if index != wire and other_node:
                # Check if the other_node is a control node
                if other_node.first_ctrl == wire or other_node.second_ctrl == wire:
                    return GATES['CTRL']
                # Or if it is a swap node
                elif other_node.swap == wire:
                    return GATES['SWAP']
        
        # If no gate is present at the node return 'EMPTY'
        return GATES['EMPTY']

    def get_wire_for_control_node_at(self, control_wire, column):
        # Return the wire of the gate controlled by control_wire in this column
        # (i.e. the gate node whose first/second control points back here), or -1.
        column_nodes = [self.nodes[w][column] for w in range(self.num_qubits)]

        for index in range(self.num_qubits):
            other_node = column_nodes[index]
            if other_node and (other_node.first_ctrl == control_wire or other_node.second_ctrl == control_wire):
                return index

        return -1

    def to_ir(self):
        """Emit a backend-agnostic :class:`~qcge.ir.CircuitIR` from the grid.

        This is the single source of truth for the circuit's semantics; every
        execution backend (numpy, qiskit, ...) consumes it. The UI never builds a
        framework-specific circuit directly, which is what keeps qcge runnable in a
        browser build where Qiskit is unavailable.
        """
        ir = CircuitIR(self.num_qubits)

        for column in range(self.num_columns):
            for wire in range(self.num_qubits):
                node = self.nodes[wire][column]
                if not node:
                    continue

                controls = tuple(c for c in (node.first_ctrl, node.second_ctrl) if c != -1)
                gate = node.gate_type

                if gate == GATES["IDENTITY"]:
                    ir.add("i", (wire,))
                elif gate == GATES["X"]:
                    if node.rotation_angle != 0:  # parameterised RX (controls not modelled by the grid)
                        ir.add("rx", (wire,), param=node.rotation_angle)
                    else:  # Pauli-X / CX / Toffoli depending on number of controls
                        ir.add("x", (wire,), controls=controls)
                elif gate == GATES["Y"]:
                    ir.add("y", (wire,), controls=controls)
                elif gate == GATES["Z"]:
                    ir.add("z", (wire,), controls=controls)
                elif gate == GATES["S"]:
                    ir.add("s", (wire,))
                elif gate == GATES["SDG"]:
                    ir.add("sdg", (wire,))
                elif gate == GATES["T"]:
                    ir.add("t", (wire,))
                elif gate == GATES["TDG"]:
                    ir.add("tdg", (wire,))
                elif gate == GATES["H"]:
                    ir.add("h", (wire,), controls=controls)
                elif gate == GATES["SWAP"]:
                    # a swap spans two wires; emit once, from the lower wire, so the
                    # partner node does not double-apply it
                    if node.swap != -1 and wire < node.swap:
                        ir.add("swap", (wire, node.swap), controls=controls)

        return ir

    def create_quantum_circuit(self):
        """Build a ``qiskit.QuantumCircuit`` from the grid (compatibility shim).

        Retained for callers of the v1 API. Requires the optional Qiskit extra
        (``pip install qcge[qiskit]``); prefer :meth:`to_ir` plus a backend.
        """
        from qcge.backends.qiskit_backend import QiskitBackend

        return QiskitBackend().to_qiskit(self.to_ir())

class QuantumCircuitGrid(pygame.sprite.RenderPlain):
    def __init__(self, position, num_qubits, num_columns, background_color=QUANTUM_CIRCUIT_BG_COLOR, wire_color=QUANTUM_CIRCUIT_WIRE_COLOR, gate_phase_angle_color=QUANTUM_GATE_PHASE_COLOR, tile_size=QUANTUM_CIRCUIT_TILE_SIZE, gate_dimensions=[GATE_TILE_WIDTH, GATE_TILE_HIEGHT], wire_line_width=WIRE_LINE_WIDTH, backend="auto", assets_path=None, movement_keys="both", allowed_gates=None):
        super().__init__()

        ## Gate-image folder; set before any sprite (which loads images) is created.
        if assets_path is not None:
            configs.ASSETS_PATH = assets_path

        ## Which keys move the cursor: "wasd", "arrows", or "both" (default). Using
        ## "arrows" frees the letter keys (notably S) for gate placement.
        self._move_keys = self._build_move_keys(movement_keys)

        ## Which gates the player may place. None (default) = all. Otherwise an
        ## iterable of tokens from SUPPORTED_INPUT_GATES, e.g. ["H", "X", "CTRL"].
        self._allowed_gates = self._build_allowed_gates(allowed_gates)

        ## Props
        self.background_color = background_color
        self.wire_color = wire_color
        self.gate_phase_angle_color = gate_phase_angle_color
        self.tile_size = tile_size
        self.gate_dimensions = gate_dimensions
        self.wire_line_width = wire_line_width

        ## Execution backend ("auto" picks Qiskit if installed, else the numpy sim)
        self._backend = get_backend(backend)

        ## State
        self.position = position
        self.current_wire = 0
        self.current_column = 0

        self.qc_grid_model = QuantumCircuitGridModel(num_qubits, num_columns)
        self.qc_grid_background = QuantumCircuitGridBackground(self.qc_grid_model, background_color=self.background_color, wire_color=self.wire_color, tile_size=self.tile_size, wire_line_width=self.wire_line_width)
        self.qc_grid_marker = QuantumCircuitGridMarker()

        self.gate_tiles = [
            [0 for _ in range(self.qc_grid_model.num_columns)]
            for _ in range(self.qc_grid_model.num_qubits)
        ]

        # build gate-tile sprites and register them in the render group
        self.build_tiles()

    ## SUPPORT FUNCTIONS
    def highlight_current_node(self, wire, column):
        self.current_wire = wire
        self.current_column = column
        # centre the cursor on the same point the gate tile is centred on, so the
        # highlight and the gate it sits over are aligned
        self.qc_grid_marker.rect.center = (
            self.position[0] + self.tile_size * (self.current_column + 1.5),
            self.position[1] + self.tile_size * (self.current_wire + 1)
        )
    
    def get_gate_at_current_node(self):
        return self.qc_grid_model.get_gate_at_node(self.current_wire, self.current_column)

    ## QUANTUM EXECUTION (backend-agnostic)
    def to_ir(self):
        """Backend-agnostic IR of the current grid."""
        return self.qc_grid_model.to_ir()

    def set_backend(self, name):
        """Switch execution backend at runtime ("auto"/"qiskit"/"numpy"/"sim")."""
        self._backend = get_backend(name)

    @property
    def backend(self):
        return self._backend

    def run(self):
        """Simulate the current circuit, returning a :class:`SimulationResult`."""
        return self._backend.run(self.to_ir())

    def get_statevector(self):
        """Complex amplitude vector of the current circuit (little-endian)."""
        return self.run().statevector

    def get_counts(self, shots=1024):
        """Sampled measurement counts ``{bitstring: count}`` over ``shots`` shots."""
        return self.run().sample_counts(shots)

    def create_quantum_circuit(self):
        """Compatibility shim: a ``qiskit.QuantumCircuit`` (needs the qiskit extra)."""
        return self.qc_grid_model.create_quantum_circuit()
    
    ## HANDLE UPDATES    
    def update_sprites(self):
        for sprite in self.sprites():
            sprite.update()
    
    def update_qc_grid_background(self):
        self.qc_grid_background.rect.topleft = self.position
    
    def update_gate_tiles(self):
        for wire in range(self.qc_grid_model.num_qubits):
            for column in range(self.qc_grid_model.num_columns):
                gate_tile = self.gate_tiles[wire][column]
                gate_tile.rect.center = (
                    self.position[0] + self.tile_size * (column + 1.5),
                    self.position[1] + self.tile_size * (wire + 1)
                )
    
    def update(self):
        self.update_sprites()
        self.update_qc_grid_background()
        self.update_gate_tiles()
        self.highlight_current_node(self.current_wire, self.current_column)
    
    ## HANDLE INPUTS
    def move_to_adjacent_node(self, direction):
        if(direction == QUANTUM_CIRCUIT_MARKER_MOVE_LEFT and self.current_column > 0):
            self.current_column -= 1
        elif (direction == QUANTUM_CIRCUIT_MARKER_MOVE_RIGHT and self.current_column < self.qc_grid_model.num_columns - 1):
            self.current_column += 1
        elif (direction == QUANTUM_CIRCUIT_MARKER_MOVE_UP and self.current_wire > 0):
            self.current_wire -= 1
        elif (direction == QUANTUM_CIRCUIT_MARKER_MOVE_DOWN and self.current_wire < self.qc_grid_model.num_qubits - 1):
            self.current_wire += 1

        self.highlight_current_node(self.current_wire, self.current_column)

    def handle_input_x(self):
        gate_at_current_node = self.get_gate_at_current_node()
        if gate_at_current_node == GATES['EMPTY']:
            qc_grid_node = QuantumCircuitGridNode(GATES['X'])
            self.qc_grid_model.set_node(self.current_wire, self.current_column, qc_grid_node)
        self.update()
    
    def handle_input_y(self):
        gate_at_current_node = self.get_gate_at_current_node()
        if gate_at_current_node == GATES['EMPTY']:
            qc_grid_node = QuantumCircuitGridNode(GATES['Y'])
            self.qc_grid_model.set_node(self.current_wire, self.current_column, qc_grid_node)
        self.update()
    
    def handle_input_z(self):
        gate_at_current_node = self.get_gate_at_current_node()
        if gate_at_current_node == GATES['EMPTY']:
            qc_grid_node = QuantumCircuitGridNode(GATES['Z'])
            self.qc_grid_model.set_node(self.current_wire, self.current_column, qc_grid_node)
        self.update()
    
    def handle_input_h(self):
        gate_at_current_node = self.get_gate_at_current_node()
        if gate_at_current_node == GATES['EMPTY']:
            qc_grid_node = QuantumCircuitGridNode(GATES['H'])
            self.qc_grid_model.set_node(self.current_wire, self.current_column, qc_grid_node)
        self.update()

    def handle_input_s(self):
        gate_at_current_node = self.get_gate_at_current_node()
        if gate_at_current_node == GATES['EMPTY']:
            qc_grid_node = QuantumCircuitGridNode(GATES['S'])
            self.qc_grid_model.set_node(self.current_wire, self.current_column, qc_grid_node)
        self.update()

    def handle_input_t(self):
        gate_at_current_node = self.get_gate_at_current_node()
        if gate_at_current_node == GATES['EMPTY']:
            qc_grid_node = QuantumCircuitGridNode(GATES['T'])
            self.qc_grid_model.set_node(self.current_wire, self.current_column, qc_grid_node)
        self.update()

    def handle_input_delete(self, wire, column):
        gate_at_current_node = self.qc_grid_model.get_gate_at_node(wire, column)
        if(
            gate_at_current_node == GATES['X']
            or gate_at_current_node == GATES['Y']
            or gate_at_current_node == GATES['Z']
            or gate_at_current_node == GATES['H']
        ):
            self.delete_controls_for_gate(wire, column)

        if gate_at_current_node == GATES['CTRL']:
            gate_wire = self.qc_grid_model.get_wire_for_control_node_at(wire, column)
            if gate_wire >= 0:
                self.delete_controls_for_gate(gate_wire, column)
        elif (
            gate_at_current_node != GATES['CTRL']
            and gate_at_current_node != GATES['SWAP']
            and gate_at_current_node != GATES['CTRL_LINE']
        ):
            qc_grid_node = QuantumCircuitGridNode(GATES['EMPTY'])
            self.qc_grid_model.set_node(wire, column, qc_grid_node)
        
        self.update()

    def handle_input_clear_all(self):
        for wire in range(self.qc_grid_model.num_qubits):
            for column in range(self.qc_grid_model.num_columns):
                self.handle_input_delete(wire, column)

    def handle_input_ctrl(self):
        gate_at_current_node = self.get_gate_at_current_node()
        # Only an actual X/Y/Z/H gate can be given a control. Bail out otherwise -
        # in particular on an empty cell, where get_node() returns 0 and trying to
        # place a control would crash in set_node ('int' has no attribute gate_type).
        if gate_at_current_node not in (GATES['X'], GATES['Y'], GATES['Z'], GATES['H']):
            return

        qc_grid_node = self.qc_grid_model.get_node(self.current_wire, self.current_column)
        if qc_grid_node.first_ctrl >= 0:
            # Gate already has a control qubit, so remove it
            orignal_first_ctrl = qc_grid_node.first_ctrl
            qc_grid_node.first_ctrl = -1
            self.qc_grid_model.set_node(self.current_wire, self.current_column, qc_grid_node)

            # Remove Control Line Nodes
            for wire in range(
                min(self.current_wire, orignal_first_ctrl) + 1,
                max(self.current_column, orignal_first_ctrl)
            ):
                if(self.qc_grid_model.get_gate_at_node(wire, self.current_column) == GATES['CTRL_LINE']):
                    self.qc_grid_model.set_node(wire, self.current_column, QuantumCircuitGridNode(GATES['EMPTY']))
            self.update()
        else:
            # No control yet: place one, trying the wire above first, then below.
            # If neither neighbour is free there is simply nowhere to put the control,
            # so do nothing (the player can move the gate or clear a wire and retry).
            if (self.place_ctrl_qubit(self.current_wire, self.current_wire - 1) == -1):
                self.place_ctrl_qubit(self.current_wire, self.current_wire + 1)

    def handle_input_move_ctrl(self, direction):
        gate_at_current_node = self.get_gate_at_current_node()
        if(
            gate_at_current_node == GATES['X']
            or gate_at_current_node == GATES['Y']
            or gate_at_current_node == GATES['Z']
            or gate_at_current_node == GATES['H']
        ):
            qc_grid_node = self.qc_grid_model.get_node(self.current_wire, self.current_column)
            if 0 <= qc_grid_node.first_ctrl < self.qc_grid_model.num_qubits:
                # Gate already has a control qubit so try to move it
                if direction == QUANTUM_CIRCUIT_MARKER_MOVE_UP:
                    candidate_ctrl_wire = qc_grid_node.first_ctrl - 1
                    if candidate_ctrl_wire == self.current_wire:
                        candidate_ctrl_wire -= 1 # move up to previous wire above
                else:
                    candidate_ctrl_wire = qc_grid_node.first_ctrl + 1
                    if candidate_ctrl_wire == self.current_wire:
                        candidate_ctrl_wire += 1 # Move down to next wire below
            
                if 0 <= candidate_ctrl_wire < self.qc_grid_model.num_qubits:
                    if (self.place_ctrl_qubit(self.current_wire, candidate_ctrl_wire) == candidate_ctrl_wire):
                        if (direction == QUANTUM_CIRCUIT_MARKER_MOVE_UP and candidate_ctrl_wire < self.current_wire):
                            if (self.qc_grid_model.get_gate_at_node(candidate_ctrl_wire + 1, self.current_column) == GATES['EMPTY']):
                                self.qc_grid_model.set_node(candidate_ctrl_wire + 1, self.current_column, QuantumCircuitGridNode(GATES['CTRL_LINE']))
                        elif(direction == QUANTUM_CIRCUIT_MARKER_MOVE_DOWN and candidate_ctrl_wire > self.current_wire):
                            if (self.qc_grid_model.get_gate_at_node(candidate_ctrl_wire - 1, self.current_column) == GATES['EMPTY']):
                                self.qc_grid_model.set_node(candidate_ctrl_wire - 1, self.current_column, QuantumCircuitGridNode(GATES['CTRL_LINE']))
                        
                        self.update()
                    
                    else:
                        pass  # control qubit could not be placed on the candidate wire

    def handle_input_rotate(self, rotation_angle):
        gate_at_current_node = self.get_gate_at_current_node()
        if(
            gate_at_current_node == GATES['X']
            or gate_at_current_node == GATES['Y']
            or gate_at_current_node == GATES['Z']
        ):
            qc_grid_node = self.qc_grid_model.get_node(self.current_wire, self.current_column)
            qc_grid_node.rotation_angle = (qc_grid_node.rotation_angle + rotation_angle) % 2 * math.pi
            self.qc_grid_model.set_node(self.current_wire, self.current_column, qc_grid_node)
        self.update()

    def place_ctrl_qubit(self, gate_wire, candidate_ctrl_wire):
        # Attempt to attach a control on candidate_ctrl_wire for the gate on
        # gate_wire (same column). Returns the control wire on success, else -1.
        if (candidate_ctrl_wire < 0 or candidate_ctrl_wire >= self.qc_grid_model.num_qubits):
            return -1

        candidate_ctrl_wire_gate = self.qc_grid_model.get_gate_at_node(candidate_ctrl_wire, self.current_column)

        if (candidate_ctrl_wire_gate == GATES['EMPTY'] or candidate_ctrl_wire_gate == GATES['CTRL_LINE']):
            # Recording the control on the gate node is what actually makes it a
            # controlled gate (CX/CY/...); get_gate_at_node then reports the control
            # wire as a CTRL, and to_ir() emits the control. (Previously this was
            # never set, so the control - and its connecting line - never appeared.)
            qc_grid_node = self.qc_grid_model.get_node(gate_wire, self.current_column)
            qc_grid_node.first_ctrl = candidate_ctrl_wire
            self.qc_grid_model.set_node(gate_wire, self.current_column, qc_grid_node)

            # Draw the vertical connector on any wires strictly between the gate and
            # its control.
            low, high = sorted((gate_wire, candidate_ctrl_wire))
            for wire in range(low + 1, high):
                if self.qc_grid_model.get_gate_at_node(wire, self.current_column) == GATES['EMPTY']:
                    self.qc_grid_model.set_node(wire, self.current_column, QuantumCircuitGridNode(GATES['CTRL_LINE']))

            self.update()
            return candidate_ctrl_wire

        return -1

    def delete_controls_for_gate(self, gate_wire, column):
        first_control_wire = self.qc_grid_model.get_node(gate_wire, column).first_ctrl
        second_control_wire = self.qc_grid_model.get_node(gate_wire, column).second_ctrl

        # Choose the control wire (if any exist) furthest away from the gate wire
        first_control_wire_distance = 0
        second_control_wire_distance = 0

        if first_control_wire >= 0:
            first_control_wire_distance = abs(first_control_wire - gate_wire)

        if second_control_wire >= 0:
            second_control_wire_distance = abs(second_control_wire - gate_wire)

        ctrl_wire = -1
        if first_control_wire_distance > second_control_wire_distance:
            ctrl_wire = first_control_wire
        elif first_control_wire_distance < second_control_wire_distance:
            ctrl_wire = second_control_wire
        
        if ctrl_wire >= 0:
            for wire in range(
                min(gate_wire, ctrl_wire),
                max(gate_wire, ctrl_wire) + 1
            ):
                qc_grid_node = QuantumCircuitGridNode(GATES['EMPTY'])
                self.qc_grid_model.set_node(wire, column, qc_grid_node)

    def _build_move_keys(self, mode):
        """Map cursor-movement keys according to ``mode`` ("wasd"/"arrows"/"both")."""
        wasd = {
            pygame.K_a: QUANTUM_CIRCUIT_MARKER_MOVE_LEFT,
            pygame.K_d: QUANTUM_CIRCUIT_MARKER_MOVE_RIGHT,
            pygame.K_w: QUANTUM_CIRCUIT_MARKER_MOVE_UP,
            pygame.K_s: QUANTUM_CIRCUIT_MARKER_MOVE_DOWN,
        }
        arrows = {
            pygame.K_LEFT: QUANTUM_CIRCUIT_MARKER_MOVE_LEFT,
            pygame.K_RIGHT: QUANTUM_CIRCUIT_MARKER_MOVE_RIGHT,
            pygame.K_UP: QUANTUM_CIRCUIT_MARKER_MOVE_UP,
            pygame.K_DOWN: QUANTUM_CIRCUIT_MARKER_MOVE_DOWN,
        }
        mode = (mode or "both").lower()
        if mode == "wasd":
            return wasd
        if mode in ("arrows", "arrow"):
            return arrows
        if mode == "both":
            return {**wasd, **arrows}
        raise ValueError(f"movement_keys must be 'wasd', 'arrows' or 'both', got {mode!r}")

    def _build_allowed_gates(self, allowed):
        """Normalise the allowed-gate set; None means every gate is allowed."""
        if allowed is None:
            return None
        normalized = {str(g).upper() for g in allowed}
        unknown = normalized - SUPPORTED_INPUT_GATES
        if unknown:
            raise ValueError(f"Unknown gate token(s) {sorted(unknown)}; choose from {sorted(SUPPORTED_INPUT_GATES)}")
        return normalized

    def set_allowed_gates(self, allowed):
        """Restrict (or with None, re-allow) the gates the player may place at runtime.

        Lets a game change the gate palette per level, e.g. ``set_allowed_gates(["H"])``.
        """
        self._allowed_gates = self._build_allowed_gates(allowed)

    def is_gate_allowed(self, token):
        return self._allowed_gates is None or token.upper() in self._allowed_gates

    def handle_input(self, key):
        # cursor movement first; with movement_keys="arrows" the letter keys
        # (notably S) stay free for gate placement
        if key in self._move_keys:
            self.move_to_adjacent_node(self._move_keys[key])
            return

        match (key):
            case pygame.K_x:
                if self.is_gate_allowed("X"): self.handle_input_x()
            case pygame.K_y:
                if self.is_gate_allowed("Y"): self.handle_input_y()
            case pygame.K_z:
                if self.is_gate_allowed("Z"): self.handle_input_z()
            case pygame.K_h:
                if self.is_gate_allowed("H"): self.handle_input_h()
            case pygame.K_s:
                if self.is_gate_allowed("S"): self.handle_input_s()
            case pygame.K_t:
                if self.is_gate_allowed("T"): self.handle_input_t()
            case pygame.K_BACKSPACE:
                self.handle_input_delete(self.current_wire, self.current_column)
            case pygame.K_DELETE:
                self.handle_input_clear_all()
            case pygame.K_c:
                if self.is_gate_allowed("CTRL"): self.handle_input_ctrl()
            case pygame.K_r:
                self.handle_input_move_ctrl(QUANTUM_CIRCUIT_MARKER_MOVE_UP)
            case pygame.K_f:
                self.handle_input_move_ctrl(QUANTUM_CIRCUIT_MARKER_MOVE_DOWN)
            case pygame.K_q:
                if self.is_gate_allowed("ROTATE"): self.handle_input_rotate(-math.pi / 8)
            case pygame.K_e:
                if self.is_gate_allowed("ROTATE"): self.handle_input_rotate(math.pi / 8)

    ## BUILD, DRAW AND UPDATE EVERYTHING
    def build_tiles(self):
        """Create a gate-tile sprite for every grid cell and register the render group."""
        ## Create QuantumCircuitGridGate Object for each gate in the qc_circuit_grid
        for wire in range(self.qc_grid_model.num_qubits):
            for column in range(self.qc_grid_model.num_columns):
                self.gate_tiles[wire][column] = QuantumCircuitGridGate(self.qc_grid_model, wire, column, gate_dimensions=self.gate_dimensions, gate_phase_angle_color=self.gate_phase_angle_color)
                self.gate_tiles[wire][column].run()
        
        ## Drawing
        pygame.sprite.RenderPlain.__init__(self, self.qc_grid_background, self.gate_tiles, self.qc_grid_marker)
        
        ## Update
        self.update()
