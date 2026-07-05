"""
HTML email templates for the flight-tracker email service.

Each function returns a (subject, html_body) tuple ready for sending.
"""

from datetime import datetime


# ─── Shared Styles ───────────────────────────────────────────────────────────

_BASE_STYLE = """
<style>
  body { margin: 0; padding: 0; background-color: #0f172a; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
  .wrapper { max-width: 600px; margin: 0 auto; padding: 24px 16px; }
  .card {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid #334155;
    border-radius: 12px;
    overflow: hidden;
  }
  .header {
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
    padding: 28px 32px;
    text-align: center;
  }
  .header h1 { margin: 0; color: #ffffff; font-size: 22px; font-weight: 700; letter-spacing: 0.5px; }
  .header p { margin: 8px 0 0 0; color: rgba(255,255,255,0.85); font-size: 13px; }
  .body { padding: 28px 32px; color: #e2e8f0; }
  .body p { margin: 0 0 16px 0; font-size: 15px; line-height: 1.6; }
  .detail-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 12px 16px; border-radius: 8px;
    background: rgba(51, 65, 85, 0.5);
    margin-bottom: 8px;
  }
  .detail-label { color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
  .detail-value { color: #f1f5f9; font-size: 15px; font-weight: 600; }
  .change-badge {
    display: inline-block; padding: 4px 12px; border-radius: 20px;
    font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;
  }
  .badge-old { background: rgba(239, 68, 68, 0.15); color: #fca5a5; text-decoration: line-through; }
  .badge-new { background: rgba(34, 197, 94, 0.15); color: #86efac; }
  .footer {
    padding: 20px 32px; text-align: center;
    border-top: 1px solid #334155;
    color: #64748b; font-size: 11px;
  }
  .footer a { color: #60a5fa; text-decoration: none; }
  .divider { height: 1px; background: #334155; margin: 20px 0; }
</style>
"""


def _wrap_html(inner: str) -> str:
    """Wrap inner content in the shared HTML skeleton."""
    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  {_BASE_STYLE}
</head>
<body>
  <div class="wrapper">
    <div class="card">
      {inner}
    </div>
  </div>
</body>
</html>"""


# ─── Flight Change Notification ─────────────────────────────────────────────

def flight_change_email(
    flight_id: str | int,
    parameter: str,
    old_value: str,
    new_value: str,
    modified_at: str | datetime,
) -> tuple[str, str]:
    """
    Build an email for a flight-change event.

    Returns:
        (subject, html_body)
    """
    if isinstance(modified_at, datetime):
        timestamp = modified_at.strftime("%b %d, %Y at %H:%M UTC")
    else:
        timestamp = str(modified_at)

    param_display = parameter.replace("_", " ").title()
    subject = f"✈️ Flight {flight_id} Update — {param_display} Changed"

    inner = f"""\
      <div class="header">
        <h1>✈️ Flight Update</h1>
        <p>Flight {flight_id} • {timestamp}</p>
      </div>
      <div class="body">
        <p>
          A change has been detected for <strong>Flight {flight_id}</strong>.
          Here are the details:
        </p>

        <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse: collapse;">
          <tr>
            <td style="padding: 12px 16px; border-radius: 8px 8px 0 0; background: rgba(51,65,85,0.5);">
              <span class="detail-label">Parameter</span><br>
              <span class="detail-value">{param_display}</span>
            </td>
          </tr>
          <tr>
            <td style="padding: 12px 16px; background: rgba(51,65,85,0.35);">
              <span class="detail-label">Previous Value</span><br>
              <span class="change-badge badge-old">{old_value}</span>
            </td>
          </tr>
          <tr>
            <td style="padding: 12px 16px; border-radius: 0 0 8px 8px; background: rgba(51,65,85,0.5);">
              <span class="detail-label">New Value</span><br>
              <span class="change-badge badge-new">{new_value}</span>
            </td>
          </tr>
        </table>

        <div class="divider"></div>

        <p style="font-size: 13px; color: #94a3b8;">
          You are receiving this email because you subscribed to updates for Flight {flight_id}.
        </p>
      </div>
      <div class="footer">
        Flight Tracker &mdash; Real-time flight notifications<br>
        <a href="#">Unsubscribe</a> &bull; <a href="#">Manage Preferences</a>
      </div>"""

    return subject, _wrap_html(inner)


# ─── Subscription Confirmation ───────────────────────────────────────────────

def subscription_confirmation_email(
    email_id: str,
    flight_id: str,
    date: str,
) -> tuple[str, str]:
    """
    Build a confirmation email when a user subscribes to a flight.

    Returns:
        (subject, html_body)
    """
    subject = f"✅ Subscribed to Flight {flight_id} on {date}"

    inner = f"""\
      <div class="header" style="background: linear-gradient(135deg, #10b981 0%, #3b82f6 100%);">
        <h1>✅ Subscription Confirmed</h1>
        <p>You're all set to receive updates</p>
      </div>
      <div class="body">
        <p>
          Hi there! Your subscription has been confirmed. You will now receive
          email notifications for any changes to the following flight:
        </p>

        <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse: collapse;">
          <tr>
            <td style="padding: 12px 16px; border-radius: 8px 8px 0 0; background: rgba(51,65,85,0.5);">
              <span class="detail-label">Flight</span><br>
              <span class="detail-value">{flight_id}</span>
            </td>
          </tr>
          <tr>
            <td style="padding: 12px 16px; border-radius: 0 0 8px 8px; background: rgba(51,65,85,0.35);">
              <span class="detail-label">Date</span><br>
              <span class="detail-value">{date}</span>
            </td>
          </tr>
        </table>

        <div class="divider"></div>

        <p style="font-size: 13px; color: #94a3b8;">
          We'll notify <strong>{email_id}</strong> whenever gate, terminal,
          departure time, or status changes for this flight.
        </p>
      </div>
      <div class="footer">
        Flight Tracker &mdash; Real-time flight notifications<br>
        <a href="#">Unsubscribe</a> &bull; <a href="#">Manage Preferences</a>
      </div>"""

    return subject, _wrap_html(inner)
