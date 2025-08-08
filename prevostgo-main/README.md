# PrevostGO - Luxury Coach Digital Showroom

A modern B2B/B2C digital showroom and lead management platform for Prevost luxury coaches, built with FastAPI and React.

## 🚀 Features

- **Advanced Inventory Search**: Filter by price, year, model, converter, slides, and more
- **Smart Lead Management**: Automated lead scoring and dealer assignment
- **Real-time Scraping**: Automated inventory updates from prevost-stuff.com
- **Virtual Tours**: Integration with Matterport 3D tours
- **Mobile Responsive**: Optimized for all devices
- **Agent Architecture Ready**: Designed for MCP agent integration

## 📋 Prerequisites

- Python 3.9+
- Node.js 16+
- Git

## 🛠️ Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd prevostgo/backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Run database migrations:
```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd prevostgo/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create placeholder image:
```bash
# Add a placeholder-coach.jpg to public/ directory
```

## 🚀 Running the Application

### Development Mode

1. Start the backend server:
```bash
cd backend
python main.py
```
The API will be available at http://localhost:8000

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```
The app will be available at http://localhost:3000

### Running Initial Scrape

To populate the database with initial inventory:

1. Set environment variable:
```bash
export RUN_INITIAL_SCRAPE=true
```

2. Restart the backend server

Or run the scraper manually:
```python
from app.services.scraper import PrevostInventoryScraper
import asyncio

async def scrape():
    scraper = PrevostInventoryScraper()
    await scraper.run_initial_scrape()

asyncio.run(scrape())
```

## 📁 Project Structure

```
prevostgo/
├── backend/
│   ├── app/
│   │   ├── models/         # Database models and schemas
│   │   ├── routers/        # API endpoints
│   │   └── services/       # Business logic and scraper
│   ├── main.py            # FastAPI application
│   └── requirements.txt    # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── components/     # Reusable React components
    │   ├── pages/         # Page components
    │   ├── services/      # API client
    │   └── hooks/         # Custom React hooks
    ├── package.json       # Node dependencies
    └── vite.config.js     # Vite configuration
```

## 🔧 Configuration

### Backend Configuration (.env)

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./prevostgo.db

# API Settings
API_V1_STR=/api
PROJECT_NAME=PrevostGO

# Scraping
RUN_INITIAL_SCRAPE=false
SCRAPE_INTERVAL_HOURS=6

# Email (for production)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
DEFAULT_DEALER_EMAIL=sales@prevostgo.com
```

### Frontend Configuration

Update `src/services/api.js` for production API URL:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://api.prevostgo.com';
```

## 📊 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

- `GET /api/inventory/` - List coaches with filters
- `GET /api/inventory/{id}` - Get coach details
- `POST /api/leads/inquiry` - Submit inquiry
- `POST /api/search/coaches` - Advanced search
- `GET /api/search/facets` - Get filter options

## 🚀 Production Deployment

### Backend Deployment (Using Docker)

1. Create Dockerfile:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. Build and run:
```bash
docker build -t prevostgo-backend .
docker run -p 8000:8000 prevostgo-backend
```

### Frontend Deployment

1. Build for production:
```bash
npm run build
```

2. Deploy to static hosting (Vercel, Netlify, etc.):
```bash
# Example with Vercel
npm i -g vercel
vercel --prod
```

### Database Migration to PostgreSQL

For production, switch to PostgreSQL:

1. Update DATABASE_URL:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/prevostgo
```

2. Install PostgreSQL driver:
```bash
pip install asyncpg
```

## 🔒 Security Considerations

1. **Add Authentication**: Implement JWT authentication for admin routes
2. **Rate Limiting**: Add rate limiting to prevent abuse
3. **CORS**: Configure allowed origins for production
4. **Environment Variables**: Never commit `.env` files
5. **SQL Injection**: SQLAlchemy ORM prevents SQL injection
6. **XSS Protection**: React escapes content by default

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📈 Monitoring

1. **Application Monitoring**: Use Sentry for error tracking
2. **Performance**: Monitor with New Relic or DataDog
3. **Logs**: Centralize logs with ELK stack or CloudWatch
4. **Uptime**: Use Pingdom or UptimeRobot

## 🤝 Agent Integration

The platform is designed for MCP agent integration:

1. **memory_agent**: Reads inventory_summary.json
2. **creative_agent**: Generates listing descriptions
3. **critic_agent**: Reviews content before publishing
4. **lead_agent**: Scores and routes leads
5. **orchestrator**: Coordinates all agents

## 📝 License

Copyright 2025 PrevostGO. All rights reserved.

## 🆘 Support

For issues or questions:
- Create an issue in the repository
- Contact: support@prevostgo.com
- Documentation: https://docs.prevostgo.com

## 🛣️ Roadmap

- [ ] User authentication system
- [ ] Advanced analytics dashboard
- [ ] Mobile app (React Native)
- [ ] AR/VR coach tours
- [ ] Financing calculator
- [ ] Service scheduling integration
- [ ] Expansion to yachts and jets

---

Built with ❤️ for the luxury coach community
