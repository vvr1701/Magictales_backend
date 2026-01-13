"""
Email service using Resend for transactional emails.

Resend Free Tier: 3,000 emails/month
Docs: https://resend.com/docs
"""

import httpx
import structlog
from typing import Optional

from app.config import get_settings

logger = structlog.get_logger()


class EmailService:
    """Service for sending transactional emails via Resend."""
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key = getattr(self.settings, 'resend_api_key', None)
        self.from_email = getattr(self.settings, 'from_email', 'MagicTales <noreply@zelavokids.com>')
        self.base_url = "https://api.resend.com"
    
    def _is_configured(self) -> bool:
        """Check if email service is configured."""
        return bool(self.api_key)
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email via Resend API.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text fallback (optional)
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self._is_configured():
            logger.warning("Email service not configured (RESEND_API_KEY missing)")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/emails",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "from": self.from_email,
                        "to": [to_email],
                        "subject": subject,
                        "html": html_content,
                        "text": text_content or subject
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(
                        "Email sent successfully",
                        to=to_email,
                        email_id=data.get("id")
                    )
                    return True
                else:
                    logger.error(
                        "Failed to send email",
                        to=to_email,
                        status=response.status_code,
                        response=response.text
                    )
                    return False
                    
        except Exception as e:
            logger.error("Email sending error", to=to_email, error=str(e))
            return False
    
    async def send_book_ready_email(
        self,
        to_email: str,
        child_name: str,
        story_title: str,
        download_url: str,
        preview_url: str
    ) -> bool:
        """
        Send "Your Book is Ready!" notification email.
        
        Args:
            to_email: Customer email
            child_name: Child's name in the story
            story_title: Title of the storybook
            download_url: Direct PDF download URL
            preview_url: Link to preview page
        """
        subject = f"🎉 {child_name}'s Storybook is Ready!"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f8f4ff;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table role="presentation" style="max-width: 600px; width: 100%; border-collapse: collapse; background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #9333ea 0%, #ec4899 100%); padding: 40px 30px; text-align: center; border-radius: 16px 16px 0 0;">
                            <h1 style="margin: 0; color: white; font-size: 28px; font-weight: 700;">
                                ✨ Your Storybook is Ready! ✨
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <p style="margin: 0 0 20px; color: #374151; font-size: 16px; line-height: 1.6;">
                                Great news! <strong>{child_name}'s</strong> personalized storybook has been created and is ready for download.
                            </p>
                            
                            <div style="background: #f3e8ff; border-radius: 12px; padding: 20px; margin: 20px 0; text-align: center;">
                                <p style="margin: 0 0 8px; color: #7c3aed; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                                    Your Story
                                </p>
                                <p style="margin: 0; color: #1f2937; font-size: 20px; font-weight: 700;">
                                    {story_title}
                                </p>
                            </div>
                            
                            <!-- Download Button -->
                            <table role="presentation" style="width: 100%; margin: 30px 0;">
                                <tr>
                                    <td align="center">
                                        <a href="{download_url}" style="display: inline-block; background: linear-gradient(135deg, #9333ea 0%, #ec4899 100%); color: white; text-decoration: none; padding: 16px 40px; border-radius: 12px; font-size: 18px; font-weight: 700; box-shadow: 0 4px 15px rgba(147, 51, 234, 0.3);">
                                            📥 Download Your PDF
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 20px 0 0; color: #6b7280; font-size: 14px; text-align: center;">
                                Or <a href="{preview_url}" style="color: #9333ea; text-decoration: underline;">view your book online</a>
                            </p>
                            
                            <!-- What's Included -->
                            <div style="border-top: 1px solid #e5e7eb; margin-top: 30px; padding-top: 30px;">
                                <p style="margin: 0 0 15px; color: #1f2937; font-size: 16px; font-weight: 600;">
                                    What's included:
                                </p>
                                <ul style="margin: 0; padding: 0 0 0 20px; color: #4b5563; font-size: 14px; line-height: 1.8;">
                                    <li>📖 10-page personalized storybook</li>
                                    <li>🎨 High-resolution illustrations featuring {child_name}</li>
                                    <li>📄 Print-ready PDF format</li>
                                    <li>♾️ Download unlimited times (30 days)</li>
                                </ul>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background: #f9fafb; padding: 20px 30px; text-align: center; border-radius: 0 0 16px 16px; border-top: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 10px; color: #6b7280; font-size: 12px;">
                                Made with ❤️ by MagicTales
                            </p>
                            <p style="margin: 0; color: #9ca3af; font-size: 11px;">
                                © 2026 Zelavo Kids. All rights reserved.
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
        
        text_content = f"""
Your Storybook is Ready!

Great news! {child_name}'s personalized storybook has been created and is ready for download.

Story: {story_title}

Download your PDF: {download_url}

Or view online: {preview_url}

What's included:
- 10-page personalized storybook
- High-resolution illustrations featuring {child_name}
- Print-ready PDF format
- Unlimited downloads (30 days)

Made with love by MagicTales
© 2026 Zelavo Kids
"""
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )


# Singleton instance
_email_service: Optional[EmailService] = None

def get_email_service() -> EmailService:
    """Get or create email service singleton."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
