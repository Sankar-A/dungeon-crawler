# 🚀 Deployment Guide

## Deploy to Render

### Quick Deploy (Recommended)

1. **Create a GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Dungeon Crawler RPG"
   git branch -M main
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`
   - Click "Create Web Service"
   - Wait for deployment (2-3 minutes)

3. **Access Your Game**
   - Render will provide a URL like: `https://dungeon-crawler-xxxx.onrender.com`
   - Share with friends and start playing!

### Manual Configuration (Alternative)

If you prefer manual setup:

1. **Create Web Service on Render**
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`

2. **Environment Variables**
   - `PYTHON_VERSION`: 3.11.0
   - `PORT`: 5000

## Deploy to Other Platforms

### Heroku

1. Create `Procfile`:
   ```
   web: python app.py
   ```

2. Deploy:
   ```bash
   heroku create your-dungeon-crawler
   heroku git:remote -a your-dungeon-crawler
   git push heroku main
   ```

### Railway

1. Connect your GitHub repo to Railway
2. Railway auto-detects Python and installs dependencies
3. Set start command: `python app.py`

### DigitalOcean App Platform

1. Connect your GitHub repo
2. Select Python as runtime
3. Build command: `pip install -r requirements.txt`
4. Run command: `python app.py`

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python app.py

# Access at http://localhost:5000
```

## Production Considerations

### For High Traffic

1. **Use Gunicorn with Eventlet**
   
   Update `requirements.txt`:
   ```
   gunicorn==21.2.0
   ```
   
   Update start command:
   ```bash
   gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
   ```

2. **Add Database (Optional)**
   - Currently uses in-memory storage
   - For persistence, add PostgreSQL or MongoDB
   - Store player data, dungeons, and sessions

3. **Enable HTTPS**
   - Render provides free SSL certificates
   - Ensure WebSocket connections use WSS protocol

4. **Monitor Performance**
   - Use Render's built-in metrics
   - Monitor memory usage (dungeons are stored in RAM)
   - Consider Redis for session management

## Troubleshooting

### WebSocket Connection Issues
- Ensure CORS is properly configured
- Check that Socket.IO versions match (client & server)
- Verify firewall allows WebSocket connections

### Memory Issues
- Dungeons are stored in memory
- Consider implementing dungeon cleanup for inactive floors
- Monitor RAM usage on Render dashboard

### Port Issues
- Render assigns PORT via environment variable
- Update app.py if needed:
  ```python
  port = int(os.environ.get('PORT', 5000))
  socketio.run(app, host='0.0.0.0', port=port)
  ```

## Scaling

For larger player bases:
1. Implement Redis for shared state
2. Use multiple worker processes
3. Add load balancing
4. Implement room-based sharding

## Support

For issues or questions:
- Check server logs on Render dashboard
- Review browser console for client errors
- Ensure all dependencies are installed correctly
