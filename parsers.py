import re
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from datetime import datetime

class BaseParser(ABC):
    @abstractmethod
    def parse(self, email_content, subject):
        pass

class UberParser(BaseParser):
    def parse(self, html_content, subject):
        """
        Parses Uber HTML receipts. 
        Note: HTML parsing is brittle. In a production env, 
        we would use specific ID selectors or API data.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        
        # 1. Extract Amount (Regex for currency like ₹120.50 or $15.00)
        # Looking for "Total" followed by numbers
        amount_match = re.search(r'Total\s*[:\-]?.?\s?([₹$€£]?)\s?([\d,]+\.?\d*)', text, re.IGNORECASE)
        
        amount = 0.0
        currency = "INR"
        
        if amount_match:
            currency_symbol = amount_match.group(1)
            amount_str = amount_match.group(2).replace(',', '')
            amount = float(amount_str)
            if '₹' in currency_symbol or 'Rupee' in text: currency = "INR"
        
        # 2. Extract Date (Fallback to today if not found)
        # Uber usually puts date in the subject or top of body
        # Simple extraction for now:
        date_obj = datetime.now().date()
        
        return {
            "service": "Uber",
            "amount": amount,
            "currency": currency,
            "date": date_obj
        }

class SwiggyParser(BaseParser):
    def parse(self, html_content, subject):
        """
        Parses Swiggy HTML/Text receipts.
        Looks for 'Order Total:' or 'Paid Via Bank:'
        """
        # Clean the HTML to get raw text for easier regex matching
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        
        amount = 0.0
        currency = "INR"
        
        # Swiggy specific regex: Finds "Order Total:" followed by currency and digits
        # This handles the "Order Total:₹ 590" or "Paid Via Bank:₹ 590.00"
        amount_match = re.search(r'(?:Order Total|Paid Via Bank)\s*[:\-]?\s*[₹]?\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
        
        if amount_match:
            amount_str = amount_match.group(1).replace(',', '')
            amount = float(amount_str)

        # Date Extraction: Swiggy emails usually have the date in the body
        # e.g., "Order placed at: Sunday, December 14, 2025"
        date_obj = datetime.now().date()
        date_match = re.search(r'Order placed at:\s*\w+,\s*(\w+\s+\d{1,2},\s+\d{4})', text)
        if date_match:
            try:
                date_str = date_match.group(1)
                date_obj = datetime.strptime(date_str, "%B %d, %Y").date()
            except:
                pass # Fallback to email header date handled in email_loader
        
        return {
            "service": "Swiggy",
            "amount": amount,
            "currency": currency,
            "date": date_obj
        }
        
class ZomatoParser(BaseParser):
    def parse(self, html_content, subject):
        """
        Parses Zomato HTML receipts.
        Looks for 'Total paid - ₹' and 'ORDER ID:'
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        
        amount = 0.0
        currency = "INR"
        
        # Zomato specific regex: Finds "Total paid - ₹860.42"
        amount_match = re.search(r'Total paid\s*[-]\s*[₹]?\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
        if amount_match:
            amount_str = amount_match.group(1).replace(',', '')
            amount = float(amount_str)

        return {
            "service": "Zomato",
            "amount": amount,
            "currency": currency
        }

# Update the Factory function to include Zomato
def get_parser(service_key):
    service_key = service_key.lower()
    if "uber" in service_key:
        return UberParser()
    elif "swiggy" in service_key:
        return SwiggyParser()
    elif "zomato" in service_key:
        return ZomatoParser()
    return None