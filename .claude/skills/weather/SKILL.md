---
name: weather
description: Get current weather and 3-day forecast for any city. No API key required (uses Open-Meteo).
user-invocable: true
---

# Weather Skill

Fetches real-time weather using Open-Meteo (free, no API key required).

## Usage

```python
from skills.weather import get_weather
result = get_weather("Tokyo")
```

## Arguments

`$ARGUMENTS` — city or location name

## Example invocation

`/weather London`

## Script

```bash
python -c "from skills.weather import get_weather; import json; print(json.dumps(get_weather('$ARGUMENTS'), indent=2))"
```
