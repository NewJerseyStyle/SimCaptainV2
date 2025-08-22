# Real-Time Tactical Ship Simulation Game

## About the Project
The project is a "Real-Time Tactical Ship Simulation Game" that integrates Large Language Models (LLMs) to enable natural language interaction with ship's crew agents. Players act as commanders, issuing orders to officer agents (Weapons, Helm, Engineering) who then translate these commands into game actions. The simulation features ship management, movement, combat (guns, torpedoes), and dynamic crew interactions, including casualty handling and role reassignment. Enemy ships are controlled by an AI Commander.

## Getting Started

To get started with the Real-Time Tactical Ship Simulation Game, follow these steps:

### Prerequisites
*   Python 3.8+
*   pip (Python package installer)

### Installation
1.  Clone the repository:
    ```bash
    git clone https://github.com/your-repo/stanford-town-sim-complex.git
    cd stanford-town-sim-complex
    ```
    (Note: Replace `https://github.com/your-repo/stanford-town-sim-complex.git` with the actual repository URL if available.)

2.  Create a virtual environment (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
    (Note: A `requirements.txt` file is assumed. If one does not exist, it will need to be created with project dependencies.)

### Configuration
1.  Copy the example environment file:
    ```bash
    cp example.env .env
    ```
2.  Open the newly created `.env` file and fill in any necessary API keys or configuration details for the LLM integration.

### Running the Game
To start the simulation, run the main Python script:
```bash
python main.py
```