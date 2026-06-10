![Quantum Circuit Game Engine](https://github.com/devilkiller-ag/Quantum-Circuit-Game-Engine/assets/43639341/dd998bca-c47b-44fd-8ed2-19724cbc57a2)

<h1>Quantum Circuit Game Engine for Pygame-based Quantum Games</h1>

This is a Quantum Circuit Game Engine for integrating Quantum Circuits into your Pygame-based quantum game. You can use it simply by creating an object of the `QuantumCircuitGrid` class stored in the `quantum_circuit.py` file.

This Quantum Circuit was originaly created for the **QPong Game** developed by <a href='https://huangjunye.github.io/' target='_blank'>Junye Huang</a> in the <a href="https://www.youtube.com/playlist?list=PLOFEBzvs-VvodTkP_rfrs3RWdeWE9aNRD" target='_blank'>12 Days of Qiskit Program</a>. I created this engine by re-writing its code located <a href='https://github.com/QPong/qpong-livestream' target='_blank'>here</a> to make it modular and abstract for easy use with any quantum game. 

The features I have included are:
- Modular and Abstract Code.
- **Pluggable execution backends (new in v2):** run circuits with real **Qiskit** on the desktop, or a **pure-Python statevector simulator** (zero third-party dependencies) that also runs in the browser (pygbag/WebAssembly), where Qiskit cannot. A numpy simulator is also available for desktop use. The engine auto-selects the best backend.
- **Browser-safe by design.** The pure-Python backend imports nothing beyond the standard library. This matters: importing **numpy** inside a pygbag/WebAssembly build breaks the SDL display (grey screen / *"video driver did not add any displays"*), so the browser path must stay numpy-free. `import qcge` is numpy-free (the numpy/qiskit backends are lazy), and `backend="auto"` resolves to the pure-Python simulator in the browser automatically.
- **Qiskit is optional.** `pip install qcge` ships the simulators; `pip install qcge[qiskit]` adds the real Qiskit backend (Qiskit **2.x**; 1.x is end-of-life).
- All configurations in one place in the `config.py` file.
- Developers can create a Quantum Circuit for any number of qubit/wires and circuit width (max. number of gates which can be applied in a wire) of their choice. 
- Easy to change UI by replacing color configs and graphics for gates with those of your choice. 
- Easy to change the size of Quantum Circuit by adjusting `QUANTUM_CIRCUIT_TILE_SIZE`, `GATE_TILE_WIDTH`, and `GATE_TILE_HIEGHT` in the `config.py` file.
- Easily change controls by changing keys in the `handle_input()` method of the `QuantumCircuitGrid` class.


**If this project is helpful for you or you liked my work, consider supporting me through <a href="https://ko-fi.com/ashmitjsg" target="_blank">Ko.fi🍵</a>. Also, kindly consider giving a star to this repository.😁**

<!-- ------------------------------------------------------------------------- -->
<h2>Roadmap</h2>

The v2 backend system (a backend-agnostic circuit IR + a pluggable `QuantumBackend`
strategy) is designed so new execution targets slot in without touching any game or
UI code. Planned next:

- **Real quantum hardware backend.** An `IBMBackend` (`backend="ibm"`, optional
  extra `qcge[ibm]`) built on `qiskit-ibm-runtime`'s `SamplerV2`, where the player
  supplies their own IBM Quantum API token/credits and runs the circuit they built
  on a real QPU. Because hardware jobs are queued and take seconds-to-minutes, this
  is intended as an explicit *"run on real hardware"* action (async, result shown
  when ready) rather than the real-time game loop. Hardware returns measurement
  counts (no statevector), which the uniform `SimulationResult` already accommodates.
  Desktop-only, since a browser/WebAssembly build cannot securely hold credentials.
- More simulator backends (e.g. `qiskit-aer` for noisy/shot-based simulation).
- Additional gates and an explicit measurement node in the grid UI.

<!-- ------------------------------------------------------------------------- -->
<h2>About me</h2>

I am Ashmit JaiSarita Gupta, an Engineering Physics Undergraduate passionate about Quantum Computing, Machine Learning, UI/UX, and Web Development. I have worked on many projects in these fields, participated in hackathons, and am a part of great organizations in these fields. You can explore more about me, my work, and my experience at various organizations through my portfolio website: <a href='https://ashmitjsg.vercel.app/' target="_blank">https://ashmitjsg.vercel.app/</a> ☄️

<!-- ------------------------------------------------------------------------- -->
<h2>Installation</h2>

```bash
# core engine + dependency-free simulator (works everywhere, incl. browser builds)
pip install qcge

# add the real Qiskit backend for desktop/notebook use
pip install qcge[qiskit]
```

> Requires Python ≥ 3.9. The `qiskit` extra pulls Qiskit ≥ 2.0.
<!-- ------------------------------------------------------------------------- -->
<h2>Usage</h2>

You can use it simply by creating an object of the `QuantumCircuitGrid` class stored in the `quantum_circuit.py` file. The constructor of `QuantumCircuitGrid` takes these values as argument:

- `position`: Position of the Quantum Circuit in the game window.
- `num_qubits`: Number of Qubits in the Quantum Circuit.
- `num_columns`: Circuit width (max. number of gates which can be applied in a wire) of their choice.
- `tile_size` (Optional, Default Value = 36): Size of single tile unit of the Quantum Circuit. It is the square area containing single gate in the quantum circuit.
- `gate_dimensions` (Optional Default Value = [24, 24]): [Width, Height] of quantum gates.
- `background_color` (Optional Default Value = '#444654'): Background Color of the Quantum Circuit.
- `wire_color` (Optional Default Value = '#ffffff'): Color of Quantum Wire in the Quantum Circuit.
- `gate_phase_angle_color` (Optional Default Value = '#97ad40'): Color to represent phase angle of Rotation Gates.
- `backend` (Optional, Default `"auto"`): execution backend — `"auto"`, `"qiskit"`, `"python"`/`"sim"`, or `"numpy"` (see below).
- `assets_path` (Optional): folder to load gate images from, if you want to ship your own gate art instead of the bundled graphics.
- `movement_keys` (Optional, Default `"both"`): which keys move the circuit cursor — `"wasd"`, `"arrows"`, or `"both"`. Use `"arrows"` to free the **S** key for the S gate.
- `allowed_gates` (Optional, Default `None` = all): a list/tuple restricting the gate palette the player may place, e.g. `("H", "X", "CTRL")`. Useful for tutorial levels. Tokens come from `SUPPORTED_INPUT_GATES`.

### Running (simulating) the circuit

The grid simulates itself through the selected backend - no Qiskit boilerplate, no
removed `BasicAer`/`execute`:

```python
from qcge import QuantumCircuitGrid

# backend="auto" (default) -> Qiskit if installed, else the pure-Python simulator
grid = QuantumCircuitGrid(position=(0, 0), num_qubits=2, num_columns=8)

# ...player builds a circuit on the grid...

statevector = grid.get_statevector()      # complex amplitudes (little-endian, Qiskit order)
counts      = grid.get_counts(shots=1024) # {"00": 512, "11": 512, ...}
result      = grid.run()                   # full SimulationResult (probabilities/sampling/most_likely)
measured    = int(result.most_likely(), 2)
```

Choose or switch the backend explicitly:

```python
QuantumCircuitGrid(..., backend="qiskit")  # real Qiskit (needs qcge[qiskit])
QuantumCircuitGrid(..., backend="python")  # pure-Python simulator (browser-safe, zero deps)
QuantumCircuitGrid(..., backend="sim")     # alias for the pure-Python simulator
grid.set_backend("numpy")                  # numpy simulator (desktop convenience)

from qcge import available_backends, get_backend
available_backends()                        # e.g. ["qiskit", "python", "numpy"]
# "auto" prefers Qiskit on desktop and the pure-Python simulator otherwise; it
# never auto-selects numpy, so the browser path stays numpy-free.
```

You can still get a raw `qiskit.QuantumCircuit` when needed (requires the qiskit extra):

```python
qc = grid.create_quantum_circuit()  # or grid.to_ir() for the backend-agnostic IR
```

<!-- ------------------------------------------------------------------------- -->
<h2>Configurations</h2>

All the configurations for Quantum Circuit can be done in the `config.py` file. The controls of the quantum circuit in the game can be changed from the defaults mentioned below by changing keys in the `handle_input()` method of the `QuantumCircuitGrid` class.

- You can change the size of Quantum Circuit by passing optional parameters `tile_size`, and `gate_dimensions` (= [GATE_TILE_WIDTH, GATE_TILE_HIEGHT]) to the `qcge.QuantumCircuitGrid` class as parameters.
- You can change UI colors by passing optional parameters `background_color`, `wire_color`, and `gate_phase_angle_color` to the `qcge.QuantumCircuitGrid` class as parameters.

Default values of these optional parameter are:
```python
tile_size = 36
gate_dimensions = [24, 24]
background_color = '#444654'
wire_color = '#ffffff'
gate_phase_angle_color = '#97ad40'
```

<!-- ------------------------------------------------------------------------- -->
<h2>Game Controls for Building Quantum Circuit</h2>

- **W, A, S, D Keys** (or the **Arrow keys**, configurable via `movement_keys`)**:** Move the "Circuit Cursor" in the Quantum Circuit to the place where you want to add a gate in the circuit.
- **Backspace Key:** Remove the gate present at the Circuit Cursor.
- **Delete Key:** Clear the Quantum Circuit, i.e., remove all gates from the Quantum Circuit.
- **X Key:** Add X Gate to the quantum circuit.
- **Y Key:** Add Y Gate to the quantum circuit.
- **Z Key:** Add Z Gate to the quantum circuit.
- **H Key:** Add H Gate to the quantum circuit.
- **C, R, E Keys:** Press **C Key** to convert the X, Y, Z, or H gates into CX, CY, CZ, and CH gates respectively, and then press **R Key** and **F Key** to the control to qubit above or below respectively.
- **Q and E Keys:** To convert X, Y, and Z into RX, RY, and RZ gates respectively. **Q Key** decreases the rotation angle by π/8 and **E Key** increases the rotation angle by π/8.

<!-- ------------------------------------------------------------------------- -->
