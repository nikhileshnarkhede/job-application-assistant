# Docker Setup - Job Application Assistant

## Quick Start

### 1. Create your `.env` file

```bash
# Copy the template
cp .env.example .env

# Edit with your API keys
nano .env  # or use any text editor
```

Required variables in `.env`:
```env
OPENAI_API_KEY=sk-your-key-here
GITHUB_USERNAME=your-username
GITHUB_TOKEN=ghp_your-token-here
```

### 2. Run with Docker Compose (Recommended)

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### 3. Or run with Docker directly

```bash
# Build image
docker build -t job-application-assistant .

# Run with .env file
docker run -p 8501:8501 --env-file .env job-application-assistant

# Run with volume mounts for persistence
docker run -p 8501:8501 \
  --env-file .env \
  -v $(pwd)/applications:/app/applications \
  -v $(pwd)/data:/app/data \
  job-application-assistant
```

### 4. Access the Application

Open your browser: **http://localhost:8501**

## Environment Variables

The `.env` file is loaded at **runtime**, not baked into the image. This means:

- ✅ Your API keys stay secure (not in the image)
- ✅ You can change keys without rebuilding
- ✅ Same image works for different users

### Required Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `GITHUB_USERNAME` | Your GitHub username |
| `GITHUB_TOKEN` | GitHub personal access token |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `LOG_LEVEL` | `INFO` | Logging level |

## Volume Mounts

Docker Compose automatically mounts these directories for persistence:

| Host Path | Container Path | Purpose |
|-----------|---------------|---------|
| `./applications` | `/app/applications` | Generated resumes/cover letters |
| `./data/checkpoints` | `/app/data/checkpoints` | Pipeline checkpoints |
| `./data/candidate_experience.json` | `/app/data/candidate_experience.json` | Your profile |
| `./data/github_projects.json` | `/app/data/github_projects.json` | Project overrides |

## Commands

### Using Docker Compose

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Rebuild after code changes
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f job-assistant

# Execute command in container
docker-compose exec job-assistant python main.py --config

# Run CLI pipeline
docker-compose exec job-assistant python main.py --test
```

### Using Docker

```bash
# Build
docker build -t job-application-assistant .

# Run Streamlit (default)
docker run -p 8501:8501 --env-file .env job-application-assistant

# Run CLI
docker run --env-file .env job-application-assistant python main.py --test

# Interactive shell
docker run -it --env-file .env job-application-assistant bash
```

## Troubleshooting

### "OPENAI_API_KEY not set"

Make sure your `.env` file exists and contains valid keys:
```bash
cat .env  # Check file exists
docker-compose config  # Verify compose reads env
```

### Container can't write files

Ensure volume directories exist on host:
```bash
mkdir -p applications data/checkpoints
```

### Port already in use

Change the port mapping in `docker-compose.yml`:
```yaml
ports:
  - "8502:8501"  # Use 8502 on host
```

### Rebuild after code changes

```bash
docker-compose up --build
```

## Production Deployment

For production, consider:

1. **Use secrets management** instead of `.env` file
2. **Add reverse proxy** (nginx/traefik) for HTTPS
3. **Set resource limits** in docker-compose.yml
4. **Use Docker Swarm or Kubernetes** for scaling

Example with resource limits:
```yaml
services:
  job-assistant:
    ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```
