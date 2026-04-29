# EditMind Integration

This document describes the integration of [EditMind](https://github.com/iliashad/edit-mind), an open-source AI-powered local video indexing and semantic search platform, into the Director project.

## Overview

EditMind provides local AI capabilities for:
- Video transcription
- Scene detection and indexing
- Object/face recognition
- Emotion analysis
- Natural language semantic search using vector databases

The integration allows Director to leverage these capabilities locally, maintaining privacy and reducing cloud dependencies while enhancing video analysis features.

## Architecture

### Components

1. **EditMind Services** (Docker containers):
   - `editmind-ml`: Core ML service for transcription and analysis (port 8765)
   - `editmind-background-jobs`: Background processing for indexing (port 4000)
   - `editmind-web`: Web interface (port 3745)
   - `editmind-chroma`: Vector database for semantic search (port 8000)
   - `editmind-redis`: Caching and job queue (port 6379)
   - `editmind-postgres`: Metadata storage (port 5432)

2. **Director Integration**:
   - `EditMindWrapper`: Python wrapper class for API communication
   - `LocalVideoDBTool`: Enhanced with EditMind-powered transcription and scene indexing
   - REST API endpoints for search functionality

### Data Flow

```
Video Upload → EditMind ML Service → Transcription/Scene Analysis → ChromaDB Vector Storage
                                                                 ↓
User Query → Semantic Search → Vector Similarity → Ranked Results
```

## Setup

### Prerequisites

- Docker Desktop installed and running
- Python environment with required packages
- FFmpeg for video processing

### Environment Variables

Create `.env.editmind` file:

```bash
# EditMind System Configuration
POSTGRES_USER=editmind
POSTGRES_PASSWORD=your_password
POSTGRES_DB=editmind
REDIS_URL=redis://redis:6379
CHROMA_HOST=chroma
CHROMA_PORT=8000

# EditMind Application
PORT=3745
BACKGROUND_JOBS_PORT=4000
ML_PORT=8765
HOST_MEDIA_PATH=./backend/director/downloads
```

Create `.env.editmind.system` file:

```bash
POSTGRES_USER=editmind
POSTGRES_PASSWORD=your_password
POSTGRES_DB=editmind
REDIS_URL=redis://redis:6379
CHROMA_HOST=chroma
CHROMA_PORT=8000
```

### Starting Services

```bash
docker-compose up -d
```

This will start all EditMind services alongside the Director backend and frontend.

## API Usage

### EditMindWrapper

```python
from director.tools.ai.editmind_wrapper import EditMindWrapper

wrapper = EditMindWrapper()

# Get transcript
transcript = wrapper.get_transcript("path/to/video.mp4")

# Index scenes
scenes = wrapper.index_scenes("path/to/video.mp4")

# Semantic search
results = wrapper.semantic_search("query", limit=10)
```

### REST API

#### Search Videos

```http
GET /videodb/collection/{collection_id}/search?query=search_term&limit=10
```

Response:
```json
{
  "results": [
    {
      "id": "video_id",
      "name": "video_name.mp4",
      "collection_id": "default",
      "file_path": "/path/to/video.mp4",
      "metadata": {...},
      "transcript_snippet": "matching text...",
      "search_method": "editmind"
    }
  ]
}
```

## Fallback Behavior

If EditMind services are unavailable, the system automatically falls back to:
- OpenAI Whisper for transcription
- Local AI vision models for scene detection
- Basic text search in transcripts

## Monitoring

### Health Checks

All EditMind containers include health checks. Monitor service status:

```bash
docker ps --filter "name=director-editmind"
```

### Logs

View logs for specific services:

```bash
docker logs director-editmind-ml
docker logs director-editmind-background-jobs
```

## Troubleshooting

### Common Issues

1. **Container won't start**: Check Docker resources and port conflicts
2. **Transcription fails**: Verify ML models are downloaded (check container logs)
3. **Search returns no results**: Ensure videos are indexed (check ChromaDB)
4. **Performance issues**: Increase container resource limits in docker-compose.yml

### Resetting Data

To reset EditMind data:

```bash
docker-compose down -v
docker-compose up -d
```

## Development

### Testing EditMind Integration

Run integration tests:

```bash
cd backend
python test_local_videodb.py
```

### Adding New Features

1. Extend `EditMindWrapper` methods
2. Update `LocalVideoDBTool` to use new capabilities
3. Add REST API endpoints in `routes.py`
4. Update tests and documentation

## Performance Considerations

- EditMind containers require significant resources (4GB+ RAM recommended)
- First transcription may take longer due to model loading
- Vector search scales with indexed content size
- Consider GPU acceleration for better performance

## Security

- All processing happens locally within Docker containers
- No video data is sent to external services
- API communication uses local network only
- Environment variables contain sensitive configuration</content>
<parameter name="filePath">C:\Users\ASUS PC\Desktop\Projects\Director\docs\editmind_integration.md