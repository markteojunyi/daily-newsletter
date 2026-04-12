import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date
from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL


def build_html(newsletter_text: str, topic: str) -> str:
    """Convert plain newsletter text into a mobile-friendly HTML email."""

    today = date.today().strftime("%B %d, %Y")

    # Convert each line of the newsletter into HTML paragraphs
    paragraphs = ""
    for line in newsletter_text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        # Lines that start with ** are treated as section headings
        if line.startswith("**") and line.endswith("**"):
            heading = line.replace("**", "")
            paragraphs += f'<h2 style="font-size:18px;font-weight:600;color:#1a1a1a;margin:28px 0 8px;">{heading}</h2>\n'
        else:
            paragraphs += f'<p style="margin:0 0 16px;color:#333333;">{line}</p>\n'

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{topic} Newsletter</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f4f4;font-family:Georgia,serif;">

  <!-- Outer wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f4;padding:32px 16px;">
    <tr>
      <td align="center">

        <!-- Card -->
        <table width="100%" cellpadding="0" cellspacing="0"
               style="max-width:600px;background-color:#ffffff;border-radius:12px;overflow:hidden;">

          <!-- Header -->
          <tr>
            <td style="background-color:#1a1a1a;padding:32px 32px 24px;">
              <p style="margin:0 0 4px;font-size:12px;color:#aaaaaa;letter-spacing:2px;text-transform:uppercase;font-family:Arial,sans-serif;">Your Daily Briefing</p>
              <h1 style="margin:0 0 8px;font-size:26px;font-weight:700;color:#ffffff;line-height:1.3;">{topic}</h1>
              <p style="margin:0;font-size:13px;color:#888888;font-family:Arial,sans-serif;">{today}</p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:32px;font-size:16px;line-height:1.8;color:#333333;">
              {paragraphs}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color:#f9f9f9;padding:20px 32px;border-top:1px solid #eeeeee;">
              <p style="margin:0;font-size:12px;color:#aaaaaa;text-align:center;font-family:Arial,sans-serif;">
                Delivered by your personal Newsletter Agent &nbsp;·&nbsp; {today}
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>
"""
    return html


def send_newsletter(newsletter_text: str, topic: str) -> None:
    """Send the newsletter as an HTML email via Gmail SMTP."""

    print("Sending newsletter via Gmail...")

    subject = f"Your Daily Briefing: {topic} — {date.today().strftime('%B %d, %Y')}"
    html_content = build_html(newsletter_text, topic)

    # Build the email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL
    msg.attach(MIMEText(html_content, "html"))

    # Connect to Gmail and send
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())

    print(f"Newsletter sent to {RECIPIENT_EMAIL}")