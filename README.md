🐋 Black Whale - Security Platform
FastAPI-based all-in-one security platform: Crypto live prices, SMS bomber, web scraper, location tracking, membership system, admin panel. Dark theme, glassmorphism, responsive.
fastapi, python, cryptocurrency, sms-bomber, web-scraper, location-tracking, admin-panel, membership-system, tailwindcss, sqlalchemy, jwt-authentication
Features
Feature	Description
💰 Crypto Prices	Real-time from Tabdeal API
💣 SMS Bomber	85+ Iranian APIs
🕷️ Web Scraper	Sheypoor & Divar
📍 Location Tracker	Browser geolocation
👑 Membership	Bronze/Silver/Gold
🔐 Admin Panel	Full control
🚀 Installation & Setup
Prerequisites
Python 3.10 or higher

pip package manager

Gmail account (for email verification)

MySQL (optional, SQLite works out of the box)

Step 1: Clone the repository
bash
git clone https://github.com/yourusername/blackwhale.git
cd blackwhale
Step 2: Install dependencies
bash
pip install -r requirements.txt
Step 3: Configure environment variables
Create .env file:

env
DATABASE_URL=sqlite:///./blackwhale.db
SECRET_KEY=your-super-secret-key-here
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
Step 4: Initialize database
bash
python -c "from database import init_db; init_db()"
Step 5: Run the application
bash
python main.py
Step 6: Access the application
Open browser and navigate to: http://localhost:8000

Default admin credentials:

Email: admin@blackwhale.com

Password: admin123

📱 API Endpoints
Public Endpoints
Method	Endpoint	Description
__________________________________
GET	/	Home page
GET	/crypto	Crypto prices page
GET	/login	Login page
GET	/register	Registration page
POST	/api/register	Register new user
POST	/api/verify	Verify email OTP
POST	/api/login	User login
GET	/api/logout	User logout
Protected Endpoints
Method	Endpoint	Description
GET	/dashboard	User dashboard
GET	/bomber	SMS bomber page
GET	/scraper	Web scraper page
GET	/search	Intruder search page
GET	/location	Location tracking page
GET	/admin	Admin panel
POST	/api/bomber/start	Start SMS bombing
POST	/api/locations/save	Save user location
GET	/api/locations/history	Get location history
GET	/api/user/limits	Get user daily limits
Crypto API Endpoints
Method	Endpoint	Description
GET	/crypto/api/prices	Get all cryptocurrency prices
GET	/crypto/api/history/{symbol}	Get 24h price history
GET	/crypto/api/test	Test API response
Admin Endpoints
Method	Endpoint	Description
POST	/api/admin/user/upgrade	Upgrade user membership
POST	/api/admin/service/status	Toggle service status
__________________________________
🔧 Configuration
Email Setup (Gmail)
Enable 2-Factor Authentication on your Google account

Generate an App Password (Google Account → Security → App Passwords)

Use the generated 16-digit password in .env file

Database Configuration
SQLite (default, no setup needed): sqlite:///./blackwhale.db

MySQL: mysql+pymysql://username:password@localhost/dbname

Membership Limits
Modify database.py to change daily limits:
__________________________________
python
plans = [
    {"name": "bronze", "daily_bomber_limit": 50, "daily_search_limit": 20},
    {"name": "silver", "daily_bomber_limit": 200, "daily_search_limit": 50},
    {"name": "gold", "daily_bomber_limit": 1000, "daily_search_limit": 200},
]
__________________________________
🎨 Screenshots
Page	Description
Home	Landing page with feature overview
Crypto	Live cryptocurrency prices with search
Dashboard	User statistics and daily usage
Bomber	SMS bomber interface with real-time stats
Scraper	Sheypoor & Divar scraping tools
Location	Map-based location tracking
Admin	User and service management
__________________________________
⚠️ Disclaimer
Educational Purpose Only - This project is created for educational and research purposes. The SMS bomber functionality is for testing your own phone numbers only. Users are responsible for complying with all applicable laws and regulations. The developers assume no liability for misuse of this tool.
__________________________________

🤝 Contributing
Fork the repository

Create your feature branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some AmazingFeature')

Push to the branch (git push origin feature/AmazingFeature)

Open a Pull Request
__________________________________
📧 Contact
Developer: [blackshot134]

Email: blackshot@gmail.com

GitHub:(https://github.com/blackshot134)

⭐ Show Your Support
If you found this project helpful, please give it a ⭐ on GitHub!
__________________________________
📄 LICENSE
MIT License

Copyright (c) 2025 Black Whale

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions...
