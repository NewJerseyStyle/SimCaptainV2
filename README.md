# SimCaptain V2 - Naval Tactical Ship Simulation Game

## About the Project
SimCaptain V2 is a real-time tactical naval simulation game that combines traditional ship combat mechanics with AI-powered natural language command processing. Players command the Japanese destroyer "Fubuki" against AI-controlled enemy vessels, issuing natural language orders to specialized officer agents who interpret and execute tactical decisions.

### Key Features
- **Flexible LLM Integration**: Support for multiple AI providers including OpenAI, Anthropic, and local models via Ollama
- **Natural Language Command Interface**: Issue orders in plain English to your ship's officers
- **AI Officer Agents**: WeaponsOfficer, HelmOfficer, and EngineeringOfficer agents powered by LLMs
- **Realistic Naval Combat**: Historically-inspired Japanese destroyer with Type 3 127mm guns and 610mm torpedo launchers
- **Physics-Based Ship Movement**: Speed and resistance calculations based on ship displacement and engine power
- **Real-Time Simulation**: Continuous world updates with module states, crew management, and damage systems

## Getting Started

### Prerequisites
*   Python 3.8+
*   pip (Python package installer)
*   API key for your chosen LLM provider (OpenAI, Anthropic, etc.) OR Ollama for local models

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
    - `litellm`: Universal LLM API client supporting 100+ providers
    - `json-repair`: JSON parsing and repair for LLM responses

### Configuration
1.  Copy the example environment file:
    ```bash
    cp example.env .env
    ```
2.  Configure your LLM provider in the `.env` file:

#### OpenAI (GPT models)
```env
LLM_MODEL="gpt-3.5-turbo"
OPENAI_API_KEY="your_openai_api_key_here"
```

#### Anthropic (Claude models)
```env
LLM_MODEL="claude-3-sonnet-20240229"
ANTHROPIC_API_KEY="your_anthropic_api_key_here"
```

#### Local Models (Ollama)
```env
LLM_MODEL="ollama/llama2"
OLLAMA_BASE_URL="http://localhost:11434"
```

**Note**: For local models, first install and run [Ollama](https://ollama.ai/), then pull your desired model:
```bash
ollama pull llama2
# or
ollama pull mistral
```

### Running the Game
To start the simulation, run the main Python script:
```bash
python main.py
```

## Supported LLM Providers

Thanks to LiteLLM integration, SimCaptain V2 supports 100+ LLM providers:

### Cloud Providers
- **OpenAI**: GPT-3.5-turbo, GPT-4, GPT-4-turbo
- **Anthropic**: Claude-3-sonnet, Claude-3-haiku, Claude-3-opus
- **Google**: Gemini Pro, Gemini Ultra
- **Cohere**: Command, Command-light
- **Mistral AI**: Mistral-7B, Mixtral-8x7B
- **Azure OpenAI**: All OpenAI models via Azure
- **AWS Bedrock**: Claude, Llama2, and more

### Local Models
- **Ollama**: Run models locally (Llama2, Mistral, CodeLlama, etc.)
- **Hugging Face**: Any compatible model
- **LocalAI**: Self-hosted OpenAI-compatible API

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
3. **AI Processing**: Officers interpret commands using your chosen LLM
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
- **LiteLLM Integration**: Universal interface supporting 100+ AI providers
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

## Performance Considerations

### LLM Provider Comparison
- **Local models (Ollama)**: No API costs, privacy, but slower inference
- **GPT-3.5-turbo**: Fast, cost-effective, good performance
- **GPT-4**: Best performance, higher cost, slower
- **Claude-3-haiku**: Fast and affordable
- **Claude-3-sonnet**: Balanced performance and cost

### Recommendations
- **Development/Testing**: Use `gpt-3.5-turbo` or local `ollama/llama2`
- **Production/Best Experience**: Use `gpt-4` or `claude-3-sonnet`
- **Privacy/Offline**: Use Ollama with local models

## Troubleshooting

### Common Issues
1. **LLM API Key errors**: Ensure your chosen provider's API key is set correctly in `.env`
2. **Model not found**: Verify the model name matches your provider's available models
3. **Local model connection**: For Ollama, ensure the service is running and the model is pulled
4. **Module import errors**: Ensure all dependencies from `requirements.txt` are installed
5. **Game crashes during combat**: Monitor console for error messages related to ship states

### LLM Provider Switching
You can change LLM providers without code changes by updating the `.env` file:
```bash
# Switch from OpenAI to local Ollama
LLM_MODEL="ollama/mistral"
# Comment out: OPENAI_API_KEY=...
```

### Debug Mode
Enable detailed LLM logging:
```env
LLM_DEBUG="true"
```

The game uses Python's logging system for detailed information about ship operations, officer decisions, and combat events. Check console output for detailed information about:
- Ship movements and speed changes
- Weapon firing and reload states
- Officer command processing
- Damage and casualty events
