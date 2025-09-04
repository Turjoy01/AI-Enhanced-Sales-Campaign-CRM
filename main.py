from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import io
import time
from datetime import datetime
import os
from typing import List, Dict
import json

class EmailConfig(BaseModel):
    sender_email: str
    sender_password: str
    email_subject: str = "Personalized Business Proposal"

class UploadResponse(BaseModel):
    message: str

class EmailResponse(BaseModel):
    message: str
    successful: int
    failed: int

class Stats(BaseModel):
    total_leads: int
    emails_sent: int
    successful: int
    failed: int

app = FastAPI(
    title="AI Sales Campaign CRM By Md Mahedi Hasan Turjoy",
    description="A comprehensive CRM system for managing sales campaigns with automated email functionality",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Global variables to store data
leads_data = []
email_results = []
campaign_stats = {"total_leads": 0, "emails_sent": 0, "successful": 0, "failed": 0}

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Sales Campaign CRM By Md Mahedi Hasan Turjoy</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; color: #2563eb; margin-bottom: 30px; }
            .section { margin: 20px 0; padding: 20px; border: 1px solid #e5e7eb; border-radius: 6px; }
            .stats { display: flex; gap: 20px; margin: 20px 0; }
            .stat-card { flex: 1; padding: 15px; background: #f8fafc; border-radius: 6px; text-align: center; }
            .stat-number { font-size: 24px; font-weight: bold; color: #2563eb; }
            .stat-label { color: #6b7280; font-size: 14px; }
            .form-group { margin: 15px 0; }
            .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
            .form-group input, .form-group select { width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; }
            .btn { background: #2563eb; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
            .btn:hover { background: #1d4ed8; }
            .btn-success { background: #059669; }
            .btn-success:hover { background: #047857; }
            .btn-info { background: #0891b2; }
            .btn-info:hover { background: #0e7490; }
            .table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            .table th, .table td { padding: 8px; text-align: left; border-bottom: 1px solid #e5e7eb; }
            .table th { background: #f9fafb; font-weight: bold; }
            .status-sent { color: #059669; font-weight: bold; }
            .status-failed { color: #dc2626; font-weight: bold; }
            .loading { display: none; color: #2563eb; }
            .api-section { background: #f0f9ff; border: 1px solid #0891b2; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">AI Sales Campaign CRM By Md Mahedi Hasan Turjoy</h1>
            
            <!-- Added API Documentation section -->
            <div class="section api-section">
                <h2>API Documentation</h2>
                <p>Access the interactive API documentation to explore all available endpoints:</p>
                <button class="btn btn-info" onclick="window.open('/api/docs', '_blank')">📚 View Swagger API Documentation</button>
                <button class="btn btn-info" onclick="window.open('/api/redoc', '_blank')">📖 View ReDoc API Documentation</button>
            </div>
            
            <div class="section">
                <h2>Campaign Statistics</h2>
                <div class="stats" id="stats">
                    <div class="stat-card">
                        <div class="stat-number" id="total-leads">0</div>
                        <div class="stat-label">Total Leads</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="emails-sent">0</div>
                        <div class="stat-label">Emails Sent</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="successful">0</div>
                        <div class="stat-label">Successful</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="failed">0</div>
                        <div class="stat-label">Failed</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>Upload CSV File</h2>
                <form id="upload-form" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="file">Select CSV File:</label>
                        <input type="file" id="file" name="file" accept=".csv" required>
                    </div>
                    <button type="submit" class="btn">Upload CSV</button>
                </form>
            </div>

            <div class="section">
                <h2>Email Configuration</h2>
                <form id="email-config-form">
                    <div class="form-group">
                        <label for="sender-email">Your Gmail Address:</label>
                        <input type="email" id="sender-email" name="sender_email" required>
                    </div>
                    <div class="form-group">
                        <label for="sender-password">Gmail App Password:</label>
                        <input type="password" id="sender-password" name="sender_password" required>
                    </div>
                    <div class="form-group">
                        <label for="email-subject">Email Subject:</label>
                        <input type="text" id="email-subject" name="email_subject" value="Personalized Business Proposal" required>
                    </div>
                    <button type="button" class="btn btn-success" onclick="sendEmails()">Send Emails to All Leads</button>
                    <div class="loading" id="loading">Sending emails... Please wait.</div>
                </form>
            </div>

            <div class="section">
                <h2>Leads Data</h2>
                <div id="leads-table"></div>
            </div>

            <div class="section">
                <h2>Email Results</h2>
                <div id="email-results-table"></div>
            </div>
        </div>

        <script>
            async function loadStats() {
                try {
                    const response = await fetch('/api/stats');
                    const stats = await response.json();
                    document.getElementById('total-leads').textContent = stats.total_leads;
                    document.getElementById('emails-sent').textContent = stats.emails_sent;
                    document.getElementById('successful').textContent = stats.successful;
                    document.getElementById('failed').textContent = stats.failed;
                } catch (error) {
                    console.error('Error loading stats:', error);
                }
            }

            async function loadLeads() {
                try {
                    const response = await fetch('/api/leads');
                    const leads = await response.json();
                    const table = document.getElementById('leads-table');
                    
                    if (leads.length === 0) {
                        table.innerHTML = '<p>No leads uploaded yet.</p>';
                        return;
                    }

                    let html = '<table class="table"><thead><tr>';
                    const headers = Object.keys(leads[0]);
                    headers.forEach(header => {
                        html += `<th>${header}</th>`;
                    });
                    html += '</tr></thead><tbody>';
                    
                    leads.forEach(lead => {
                        html += '<tr>';
                        headers.forEach(header => {
                            html += `<td>${lead[header] || ''}</td>`;
                        });
                        html += '</tr>';
                    });
                    html += '</tbody></table>';
                    table.innerHTML = html;
                } catch (error) {
                    console.error('Error loading leads:', error);
                }
            }

            async function loadEmailResults() {
                try {
                    const response = await fetch('/api/email-results');
                    const results = await response.json();
                    const table = document.getElementById('email-results-table');
                    
                    if (results.length === 0) {
                        table.innerHTML = '<p>No emails sent yet.</p>';
                        return;
                    }

                    let html = '<table class="table"><thead><tr><th>Email</th><th>Status</th><th>Timestamp</th><th>Error</th></tr></thead><tbody>';
                    results.forEach(result => {
                        const statusClass = result.status === 'Sent' ? 'status-sent' : 'status-failed';
                        html += `<tr>
                            <td>${result.email}</td>
                            <td class="${statusClass}">${result.status}</td>
                            <td>${result.timestamp}</td>
                            <td>${result.error || ''}</td>
                        </tr>`;
                    });
                    html += '</tbody></table>';
                    table.innerHTML = html;
                } catch (error) {
                    console.error('Error loading email results:', error);
                }
            }

            document.getElementById('upload-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData();
                const fileInput = document.getElementById('file');
                formData.append('file', fileInput.files[0]);

                try {
                    const response = await fetch('/api/upload-csv', {
                        method: 'POST',
                        body: formData
                    });
                    const result = await response.json();
                    alert(result.message);
                    loadStats();
                    loadLeads();
                } catch (error) {
                    alert('Error uploading file: ' + error.message);
                }
            });

            async function sendEmails() {
                const senderEmail = document.getElementById('sender-email').value;
                const senderPassword = document.getElementById('sender-password').value;
                const emailSubject = document.getElementById('email-subject').value;

                if (!senderEmail || !senderPassword) {
                    alert('Please enter your Gmail credentials');
                    return;
                }

                document.getElementById('loading').style.display = 'block';

                try {
                    const response = await fetch('/api/send-emails', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            sender_email: senderEmail,
                            sender_password: senderPassword,
                            email_subject: emailSubject
                        })
                    });
                    const result = await response.json();
                    alert(result.message);
                    loadStats();
                    loadEmailResults();
                } catch (error) {
                    alert('Error sending emails: ' + error.message);
                } finally {
                    document.getElementById('loading').style.display = 'none';
                }
            }

            // Load data on page load
            loadStats();
            loadLeads();
            loadEmailResults();

            // Refresh data every 30 seconds
            setInterval(() => {
                loadStats();
                loadEmailResults();
            }, 30000);
        </script>
    </body>
    </html>
    """

@app.post("/api/upload-csv", response_model=UploadResponse, summary="Upload CSV File", description="Upload a CSV file containing lead data for email campaigns")
async def upload_csv(file: UploadFile = File(..., description="CSV file containing lead information")):
    global leads_data, campaign_stats
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Please upload a CSV file")
    
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        leads_data = df.to_dict('records')
        campaign_stats["total_leads"] = len(leads_data)
        
        return {"message": f"Successfully uploaded {len(leads_data)} leads"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")

@app.post("/api/send-emails", response_model=EmailResponse, summary="Send Emails to All Leads", description="Send personalized emails to all leads using SMTP configuration")
async def send_emails(email_config: EmailConfig):
    global leads_data, email_results, campaign_stats
    
    if not leads_data:
        raise HTTPException(status_code=400, detail="No leads data found. Please upload a CSV first.")
    
    sender_email = email_config.sender_email
    sender_password = email_config.sender_password
    email_subject = email_config.email_subject
    
    if not sender_email or not sender_password:
        raise HTTPException(status_code=400, detail="Email credentials are required")
    
    # Clear previous results
    email_results = []
    successful = 0
    failed = 0
    
    # SMTP Configuration (same as your Jupyter notebook)
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    
    try:
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect to Gmail SMTP server
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(sender_email, sender_password)
            
            for lead in leads_data:
                try:
                    # Get email from lead data
                    recipient_email = lead.get('Email') or lead.get('email') or lead.get('EMAIL')
                    
                    if not recipient_email:
                        email_results.append({
                            "email": "N/A",
                            "status": "Failed",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "error": "No email address found"
                        })
                        failed += 1
                        continue
                    
                    # Create personalized email content
                    name = lead.get('Name') or lead.get('name') or lead.get('NAME') or 'Valued Customer'
                    company = lead.get('Company') or lead.get('company') or lead.get('COMPANY') or 'your company'
                    interest = lead.get('Interest Category') or lead.get('interest') or 'business solutions'
                    
                    email_body = f"""
Dear {name},

I hope this email finds you well. I'm reaching out regarding {interest} solutions that could benefit {company}.

Based on our research, I believe we have services that align perfectly with your business needs. Our team specializes in providing customized solutions that drive growth and efficiency.

I would love to schedule a brief call to discuss how we can help {company} achieve its goals. Are you available for a 15-minute conversation this week?

Looking forward to hearing from you.

Best regards,
{sender_email.split('@')[0].title()}
                    """
                    
                    # Create email message
                    message = MIMEMultipart()
                    message["From"] = sender_email
                    message["To"] = recipient_email
                    message["Subject"] = email_subject
                    message.attach(MIMEText(email_body, "plain"))
                    
                    # Send email
                    server.send_message(message)
                    
                    email_results.append({
                        "email": recipient_email,
                        "status": "Sent",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "error": None
                    })
                    successful += 1
                    
                    # Add delay to avoid rate limiting (same as your notebook)
                    time.sleep(2)
                    
                except Exception as e:
                    email_results.append({
                        "email": recipient_email if 'recipient_email' in locals() else "Unknown",
                        "status": "Failed",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "error": str(e)
                    })
                    failed += 1
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SMTP connection error: {str(e)}")
    
    # Update campaign stats
    campaign_stats["emails_sent"] = successful + failed
    campaign_stats["successful"] = successful
    campaign_stats["failed"] = failed
    
    return {
        "message": f"Email campaign completed! {successful} successful, {failed} failed",
        "successful": successful,
        "failed": failed
    }

@app.get("/api/stats", response_model=Stats, summary="Get Campaign Statistics", description="Retrieve current campaign statistics including total leads and email status")
async def get_stats():
    return campaign_stats

@app.get("/api/leads", summary="Get All Leads", description="Retrieve all uploaded lead data")
async def get_leads():
    return leads_data

@app.get("/api/email-results", summary="Get Email Results", description="Retrieve detailed results of sent emails including status and timestamps")
async def get_email_results():
    return email_results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
