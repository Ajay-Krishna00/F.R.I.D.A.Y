import logging
from livekit.agents import function_tool, RunContext
import requests
from langchain_community.tools import DuckDuckGoSearchRun
import os
import smtplib
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText
from typing import Optional

@function_tool()
async def get_weather(
        context: RunContext,
        city: str) -> str:
    """Fetches the current weather for a given city."""
    try:
        response = requests.get(
            f"https://wttr.in/{city}?format=3")
        if(response.status_code==200):
            logging.info(f"Weather fetched {city}: {response.text.strip()}")
            return response.text.strip()
        else:
            logging.error(f"Failed to fetch weather for {city}: {response.status_code}")
            return f"Could not fetch weather for {city}."
    except Exception as e:
        logging.error(f"Error fetching weather for {city}: {e}")
        return f"An error occurred while fetching weather for {city}."
    
@function_tool()
async def search_web(query: str) -> str:
    """Searches the web using DuckDuckGo."""
    try:
        results = DuckDuckGoSearchRun().run(tool_input=query)
        logging.info(f"Search results for '{query}': {results}")
        return results
    except Exception as e:
        logging.error(f"Error searching web for '{query}': {e}")
        return f"An error occurred while searching the web for '{query}'."

@function_tool()
async def send_email(
    context: RunContext,
    to: str,
    subject: str,
    body: str
) -> str:
    """Sends an email through gmail SMTP.
    
    Args:
        to (str): Recipient email address.
        subject (str): Subject of the email.
        body (str): Body of the email.
    Returns:
        str: Confirmation message or error message.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = os.getenv("EMAIL_SENDER")
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(os.getenv("SMTP_SERVER"), os.getenv("SMTP_PORT")) as server:
            server.starttls()
            server.login(os.getenv("EMAIL_SENDER"), os.getenv("EMAIL_PASSWORD"))
            server.send_message(msg)

        logging.info(f"Email sent to {to} with subject: {subject}")
        return f"Email sent to {to}."
    except smtplib.SMTPAuthenticationError:
        logging.error("Gmail authentication failed")
        return "Email sending failed: Authentication error. Please check your Gmail credentials."
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        return f"Email sending failed: SMTP error - {str(e)}"
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return f"An error occurred while sending email: {str(e)}"