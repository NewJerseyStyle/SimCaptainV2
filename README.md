# SimCaptain V2 - Naval Tactical Ship Simulation Game

## About the Project
SimCaptain V2 is a real-time tactical naval simulation game that combines traditional ship combat mechanics with AI-powered natural language command processing. Players command the Japanese destroyer "Fubuki" against AI-controlled enemy vessels, issuing natural language orders to specialized officer agents who interpret and execute tactical decisions.

### Key Features
- **Natural Language Command Interface**: Issue orders in plain English to your ship's officers
- **AI Officer Agents**: WeaponsOfficer, HelmOfficer, and EngineeringOfficer agents powered by LLMs
- **Realistic Naval Combat**: Historically-inspired Japanese destroyer with Type 3 127mm guns and 610mm torpedo launchers
- **Physics-Based Ship Movement**: Speed and resistance calculations based on ship displacement and engine power
- **Real-Time Simulation**: Continuous world updates with module states, crew management, and damage systems

## Getting Started

To get started with the Real-Time Tactical Ship Simulation Game, follow these steps:

### Prerequisites
*   Python 3.8+
*   pip (Python package installer)
*   POE API key (for LLM integration)

### Installation
1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd SimCaptainV2
    ```

2.  Create a virtual environment (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
    
    Dependencies include:
    - `geopy`: Geographic calculations and ship positioning
    - `python-dotenv`: Environment variable management
    - `fastapi-poe`: LLM integration via Poe API
    - `json-repair`: JSON parsing and repair for LLM responses

### Configuration
1.  Copy the example environment file:
    ```bash
    cp example.env .env
    ```
2.  Open the newly created `.env` file and add your POE API key:
    ```
    POE_API_KEY=your_poe_api_key_here
    ```
    This is required for the AI officer agents to function.

### Running the Game
To start the simulation, run the main Python script:
```bash
python main.py
```

## Game Structure

### Ship Systems
Your destroyer "Fubuki" features:
- **Engine Room**: Manages propulsion, speed (0-38 knots), and direction
- **Main Guns**: Three Type 3 127mm guns with 5-minute reload cycles
- **Torpedo Launchers**: Three 610mm torpedo tube systems with rotation capability
- **Physics Model**: Realistic speed/resistance calculations based on ship specifications

### Command Interface
Issue commands using natural language in the format:
```
[officer], [command]
```

**Examples:**
- `helm, turn to starboard`
- `helm, set course to 180 degrees`
- `engineering, increase speed to 20 knots`
- `weapons, fire guns at enemy destroyer`
- `weapons, launch torpedoes at target`

### AI Officers
- **Weapons Officer**: Manages gun and torpedo systems, targeting, and status reporting
- **Helm Officer**: Controls ship movement, navigation, and course changes
- **Engineering Officer**: Operates engine room, manages power and speed settings
- **AI Commander** (Enemy): Strategic AI that commands opposing vessels

### Game Flow
1. **Situation Assessment**: Monitor enemy positions and ship status
2. **Command Issuance**: Give natural language orders to officers
3. **AI Processing**: Officers interpret commands using LLMs
4. **Action Execution**: Commands translated to ship system operations
5. **World Update**: Physics, movement, combat, and damage resolution
6. **Status Reporting**: Officers provide feedback and status updates

## Technical Architecture

### Core Components
- **World**: Central game state manager handling ships, projectiles, and physics
- **Ship**: Container for all ship systems including engines, weapons, and crew
- **Modules**: 
  - `EngineRoom`: Propulsion and power management
  - `Gun`: Weapon systems with reload states and ammunition
  - `TorpedoLauncher`: Multi-tube torpedo systems
  - `ShipSpeedResist`: Physics calculations for movement
- **Agents**: LLM-powered officers for natural language command processing
- **Communication**: Channel system for crew coordination

### File Structure
```
SimCaptainV2/
├── main.py              # Main game loop and entry point
├── world.py             # World state management
├── ship.py              # Ship class with integrated systems
├── agents.py            # LLM agent implementations
├── SimCapt.py           # Alternative ship implementation
├── module/              # Ship system modules
│   ├── Engine.py        # Engine room operations
│   ├── Gun.py           # Gun system states and firing
│   ├── TorpedoLauncher.py # Torpedo launching systems
│   └── ShipSpeedResist.py # Ship physics calculations
├── prompts/             # LLM prompts for each officer type
├── requirements.txt     # Python dependencies
├── example.env          # Environment configuration template
└── README.md           # This file
```

## Troubleshooting

### Common Issues
1. **"POE_API_KEY not set" error**: Ensure your `.env` file contains a valid POE API key
2. **LLM response errors**: Check your POE API key validity and network connection
3. **Module import errors**: Ensure all dependencies from `requirements.txt` are installed
4. **Game crashes during combat**: Monitor the console for specific error messages related to ship states

### Debug Mode
The game uses Python's logging system. Check console output for detailed information about:
- Ship movements and speed changes
- Weapon firing and reload states
- Officer command processing
- Damage and casualty events