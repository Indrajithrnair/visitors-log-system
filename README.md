# Visitor Log & Access Control System

A comprehensive visitor management system built with Django that helps manage and track visitors in residential complexes, offices, or any controlled access environment.

## Features

### Security Personnel
- Visitor registration and verification
- Check-in/check-out management
- Visit request processing
- Security monitoring and reporting
- Blacklist management

### Hosts/Residents
- Visit request management
- Visitor tracking
- Real-time notifications
- Issue reporting

### Administrators
- User management
- System configuration
- Analytics and reporting
- Blacklist management
- Security protocol management

## Technical Stack

- **Backend**: Django 4.2
- **Database**: SQLite (default), PostgreSQL (recommended for production)
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Django's built-in authentication system
- **Permissions**: Role-based access control (Admin, Security, Resident)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd visitor-log
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply database migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
visitor_log/
├── visitor_log/          # Main project directory
│   ├── settings.py      # Project settings
│   ├── urls.py         # Main URL configuration
│   └── wsgi.py         # WSGI configuration
├── visits/             # Visit management app
├── reports/            # Reporting and analytics app
├── templates/          # HTML templates
├── static/            # Static files (CSS, JS, images)
└── manage.py          # Django management script
```

## Database Schema

### User Model
- Custom user model with role-based access
- Supports multiple user types (Admin, Security, Resident)

### Visit Model
- Tracks visitor information
- Manages visit status and scheduling
- Links to hosts and security personnel

### Report Model
- Handles security reports and analytics
- Supports different report types
- Includes severity levels and review status

### Blacklist Model
- Manages restricted visitors
- Includes expiration dates and reason tracking
- Links to security reports

## Usage

1. **Security Personnel**
   - Log in to the system
   - Process visitor registrations
   - Manage check-ins and check-outs
   - Monitor security reports

2. **Hosts/Residents**
   - Access visit management dashboard
   - Approve/reject visit requests
   - Track current visitors
   - Report issues

3. **Administrators**
   - Manage user accounts
   - Configure system settings
   - Generate reports
   - Manage blacklist

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please contact the system administrator or create an issue in the repository. 