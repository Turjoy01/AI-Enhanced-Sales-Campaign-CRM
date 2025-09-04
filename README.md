# AI Sales Campaign CRM By Md Mahedi Hasan Turjoy

A FastAPI-based CRM dashboard for managing leads and sending real email campaigns with SMTP integration.

## Features

- Upload CSV files with lead data
- Real SMTP email sending using Gmail
- Personalized email generation for each lead
- Track email delivery status (Sent/Failed) in real-time
- View campaign statistics and lead information
- Simple, clean web interface

## Email Credentials for Testing(It just given for 7 days after that i will delete the App Password)
Email = '2021-2-60-072@std.ewubd.edu'
App_password = 'tnxw uvnk uwrg axvv'

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- Gmail account with App Password enabled

### Running the Application

1. Clone or extract this project
2. Run with Docker Compose:
   \`\`\`bash
   docker-compose up --build
   \`\`\`
3. Open your browser and go to `http://localhost:8000`

### Gmail App Password Setup

1. Enable 2-Factor Authentication on your Gmail account
2. Go to Google Account Settings > Security > App Passwords
3. Generate a new app password for "Mail"
4. Use this app password (not your regular password) in the CRM

### Using the CRM

1. **Upload Lead Data**: Upload a CSV file with columns like:
   - Name, Email, Company, Interest Category
   - Phone, Lead Score, Buyer Persona (optional)

2. **Configure Email**: Enter your Gmail address and app password

3. **Send Emails**: Click "Send Emails to All Leads" to start real email campaign

4. **Monitor Results**: View real-time delivery status and campaign statistics

## CSV Format Example

\`\`\`csv
Name,Email,Company,Interest Category,Phone,Lead Score,Buyer Persona
John Doe,john@example.com,Tech Corp,Technology,123-456-7890,8,Enterprise
Jane Smith,jane@company.com,Business Inc,Marketing,987-654-3210,7,SMB
\`\`\`

## Technical Details

- Built with FastAPI and Python
- Real SMTP email sending via Gmail
- Personalized email content generation
- 2-second delay between emails to avoid rate limiting
- Docker containerized for easy deployment
- Real-time email status tracking with error handling

## Email Features

- Personalized greetings using lead names
- Company-specific messaging
- Interest-based content customization
- Professional email templates
- Automatic retry logic for failed sends
- Detailed error reporting

## Troubleshooting

- **SMTP Authentication Error**: Ensure you're using Gmail App Password, not regular password
- **CSV upload issues**: Check that your CSV has Name and Email columns
- **Port conflicts**: Change port 8000 in docker-compose.yml if needed
- **Email delivery issues**: Check Gmail sending limits (500 emails/day for free accounts)

## Production Recommendations

- Use environment variables for email credentials
- Implement email queue system for large campaigns
- Add bounce and unsubscribe handling
- Consider using professional email services (SendGrid, Mailgun)
- Add database persistence for campaign history
- Implement user authentication and multi-tenancy

## Project Demo
https://jumpshare.com/s/rOkmWDEECx4S6MdEbrFu

