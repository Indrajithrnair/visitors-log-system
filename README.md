# Visitor Log System

A comprehensive visitor management and analytics dashboard with resident rent payment functionality using Razorpay.

## Features

- Visitor management and tracking
- Resident portal with dashboard
- Security guard check-in interface
- Analytics and reporting
- Rent payment processing with Razorpay
- User role management (Admin, Resident, Security)

## Technology Stack

- **Backend**: Django 5.1.6
- **Database**: SQLite (Development), PostgreSQL (Production)
- **Payment Gateway**: Razorpay
- **Deployment**: Render.com

## Local Development Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd Visitors\ log
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```
   cd visitor_log
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

## Deployment to Render.com

This project includes a `render.yaml` file for easy deployment to Render.com using the Blueprint feature.

### Automatic Deployment

1. Push your code to a Git repository (GitHub, GitLab, etc.)
2. Log in to your Render.com account
3. Go to the Dashboard and click "New" > "Blueprint"
4. Connect to your Git repository
5. Render will detect the `render.yaml` file and set up the services
6. Review the settings and click "Apply"
7. Once deployed, set the required environment variables:
   - Razorpay credentials
   - Email server settings

### Manual Deployment

1. Push your code to a Git repository
2. Create a new Web Service on Render
3. Connect to your Git repository
4. Use the following settings:
   - **Environment**: Python
   - **Build Command**: `./build.sh`
   - **Start Command**: `cd visitor_log && gunicorn visitor_log.wsgi:application --bind 0.0.0.0:$PORT`
5. Add the required environment variables in the Environment tab:
   - `DEBUG`: False
   - `SECRET_KEY`: (generate a secure key)
   - `ALLOWED_HOSTS`: yourapp.onrender.com,localhost,127.0.0.1
   - `DATABASE_URL`: (from your PostgreSQL database)
   - `RAZORPAY_KEY_ID`: (your Razorpay key)
   - `RAZORPAY_KEY_SECRET`: (your Razorpay secret)
   - Email settings if needed

## Payment Integration

To use the payment feature:

1. Set up a Razorpay account and get your API keys
2. Add your Razorpay credentials to the environment variables:
   - `RAZORPAY_KEY_ID`
   - `RAZORPAY_KEY_SECRET`
3. For webhook integration, set the webhook URL in your Razorpay dashboard to:
   `https://yourdomain.com/payments/callback/`

## Project Structure

```
visitor_log/
├── manage.py
├── visitor_log/          # Project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── users/                # User management app
├── visits/               # Visit tracking app
├── reports/              # Reporting and analytics app
├── notifications/        # Notification system app
└── payments/             # Payment processing app
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Include your license information here] 