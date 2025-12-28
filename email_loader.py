import imaplib
import email
from email.header import decode_header
import datetime
import db_manager
import parsers
import os
from dotenv import load_dotenv # pip install python-dotenv

load_dotenv()

# CONFIGURATION
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
IMAP_SERVER = "imap.gmail.com"

def run_sync():
    print("--- Starting Smart Incremental Sync ---")
    db_manager.init_db()
    
    # Define targets
    targets = [
        {"sender": "noreply@uber.com", "service_key": "uber"},
        {"sender": "noreply@swiggy.in", "service_key": "swiggy"},
        {"sender": "noreply@zomato.com", "service_key": "zomato"} 
    ]
    
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        for target in targets:
            # 1. Get the last date recorded in the DB for this service
            last_db_date = db_manager.get_latest_transaction_date(target['service_key'])
            
            # 2. Format it for IMAP (e.g., "14-Aug-2025")
            imap_date_str = last_db_date.strftime("%d-%b-%Y")
            
            print(f"\nScanning {target['service_key'].upper()} since {imap_date_str}...")
            
            # 3. Dynamic Search Query
            search_criterion = f'(FROM "{target["sender"]}" SINCE "{imap_date_str}")'
            status, messages = mail.search(None, search_criterion)
            
            email_ids = messages[0].split()
            print(f" > Found {len(email_ids)} emails to process.")

            for e_id in email_ids:
                res, msg_data = mail.fetch(e_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Decode Subject
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                        
                        msg_id = msg.get("Message-ID")

                        # Extract Date from Email Header
                        date_tuple = email.utils.parsedate_tz(msg.get("Date"))
                        if date_tuple:
                            date_obj = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple)).date()
                        else:
                            date_obj = datetime.date(2024, 1, 1)

                        # Extract Body
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/html":
                                    body = part.get_payload(decode=True).decode(errors='ignore')
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode(errors='ignore')

                        # Parse and Save
                        parser = parsers.get_parser(target["service_key"]) 
                        
                        if parser and body:
                            data = parser.parse(body, subject)
                            
                            saved = db_manager.save_expense(
                                data['service'], 
                                subject, 
                                data['amount'], 
                                data['currency'], 
                                date_obj, 
                                msg_id
                            )
                            if saved:
                                print(f"   + New: [{data['service']}] {date_obj} | ₹{data['amount']}")
                            # Else: It was a duplicate (already in DB), silently skipped.

        mail.logout()
        print("\n--- Sync Complete ---")

    except Exception as e:
        print(f"[CRITICAL ERROR] Sync failed: {e}")

if __name__ == "__main__":
    run_sync()