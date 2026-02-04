# Fridge Vision - Deployment Guide

This guide covers deployment options for the Fridge Vision backend.

## Local Development

### Prerequisites
- Python 3.9+
- 4GB+ RAM
- Optional: NVIDIA GPU (for faster inference)

### Setup

1. **Clone and Install**
```bash
cd Fridge_Vision
pip install -r requirements.txt
```

2. **Configure (Optional)**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Run Server**
```bash
python run_server.py
```

Server will be available at `http://localhost:8000`

## Docker Deployment

### Build Docker Image

```bash
docker build -t fridge-vision:latest .
```

### Run with Docker

```bash
docker run -d \
  --name fridge-vision \
  -p 8000:8000 \
  -e MODEL_NAME=yolov5s \
  -e CONF_THRESHOLD=0.5 \
  fridge-vision:latest
```

### Docker Compose

```bash
docker-compose up -d
```

Check logs:
```bash
docker-compose logs -f fridge-vision-api
```

Stop service:
```bash
docker-compose down
```

## GPU Support

### With Docker (NVIDIA Container Runtime)

Edit `docker-compose.yml` and uncomment the GPU section:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

Then run:
```bash
docker-compose up -d
```

### Environment Variables for GPU

```bash
export DEVICE=cuda
export OCR_USE_GPU=true
python run_server.py
```

## Cloud Deployment

### AWS (EC2)

1. **Launch Instance**
   - AMI: Ubuntu 22.04
   - Instance: t3.large (minimum)
   - Storage: 20GB EBS

2. **Install Dependencies**
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev
sudo apt-get install -y libopencv-dev python3-opencv
```

3. **Deploy**
```bash
git clone <your-repo>
cd Fridge_Vision
pip install -r requirements.txt
python run_server.py
```

4. **Production Setup (with Gunicorn)**
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app --bind 0.0.0.0:8000
```

### Heroku

1. **Create app**
```bash
heroku create fridge-vision
```

2. **Add Procfile**
```
web: python run_server.py
```

3. **Deploy**
```bash
git push heroku main
```

### Google Cloud Run

1. **Build and push image**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/fridge-vision
```

2. **Deploy**
```bash
gcloud run deploy fridge-vision \
  --image gcr.io/PROJECT_ID/fridge-vision \
  --platform managed \
  --memory 4Gi \
  --timeout 300
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_NAME` | yolov5s | YOLO model size (s/m/l/x) |
| `CONF_THRESHOLD` | 0.5 | Detection confidence threshold |
| `DEVICE` | auto | Compute device (cpu/cuda/auto) |
| `API_HOST` | 0.0.0.0 | API host address |
| `API_PORT` | 8000 | API port |
| `OCR_LANGUAGES` | en | OCR languages (comma-separated) |
| `OCR_USE_GPU` | false | Enable GPU for OCR |
| `DEBUG` | false | Enable debug mode |
| `LOG_LEVEL` | INFO | Logging level |

## Production Checklist

- [ ] Use larger YOLO model (yolov5m or yolov5l) for better accuracy
- [ ] Enable GPU for faster inference
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up monitoring and logging
- [ ] Add rate limiting
- [ ] Implement authentication
- [ ] Use load balancer for multiple instances
- [ ] Set up database for predictions history
- [ ] Configure auto-scaling policies

## Performance Tuning

### Single Model Instance
- **CPU Only**: ~1.5s per request
- **GPU**: ~500ms per request

### Scaling
For high load, use multiple instances behind a load balancer:

```yaml
# docker-compose with multiple replicas
services:
  fridge-vision:
    build: .
    deploy:
      replicas: 4
    ports:
      - "8000-8003:8000"
```

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Metrics
- CPU usage
- Memory usage
- Request latency
- Model inference time
- API response codes

### Recommended Tools
- Prometheus for metrics
- Grafana for visualization
- ELK Stack for logging

## Troubleshooting

### Out of Memory
```bash
# Use smaller model
export MODEL_NAME=yolov5n

# Reduce worker count
gunicorn -w 1 api.main:app
```

### Slow Inference
```bash
# Use GPU
export DEVICE=cuda

# Use faster model
export MODEL_NAME=yolov5s
```

### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Use different port
export API_PORT=8001
```

## Backup & Recovery

### Data Backup
```bash
# Backup recipes database
cp data/recipes.json data/recipes.json.backup

# Backup model weights
cp -r ~/.cache/torch/hub weights_backup/
```

### Recovery
```bash
# Restore recipes
cp data/recipes.json.backup data/recipes.json

# Restart container
docker-compose restart
```

## Security Considerations

1. **API Rate Limiting**
   - Implement per-IP rate limiting
   - Set upload size limits (default: 50MB)

2. **File Validation**
   - Only accept image formats
   - Scan for malicious files

3. **Resource Limits**
   - Set memory limits per container
   - Timeout long-running requests

4. **Authentication**
   - Use API keys for production
   - Implement token-based auth

5. **HTTPS**
   - Use SSL/TLS certificates
   - Redirect HTTP to HTTPS

## Monitoring Dashboard

Access Swagger UI for API documentation:
```
http://<server>/docs
```

Get API info endpoint:
```bash
curl http://localhost:8000/info
```

## Support

For deployment issues:
1. Check logs: `docker-compose logs -f`
2. Verify prerequisites are met
3. Ensure sufficient resources
4. Check firewall rules for port access

---

**Deployment Support**: Contact your DevOps team or refer to framework documentation
