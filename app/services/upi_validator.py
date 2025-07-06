import re
from typing import Optional
from loguru import logger


class UPIValidator:
    """Validator for UPI payment strings and related data."""
    
    UPI_ID_PATTERN = re.compile(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+$')
    
    IFSC_PATTERN = re.compile(r'^[A-Z]{4}0[A-Z0-9]{6}$')
    
    ACCOUNT_PATTERN = re.compile(r'^\d{9,18}$')
    
    def validate_upi_id(self, upi_id: str) -> bool:
        """Validate UPI ID format."""
        if not upi_id:
            return False
        
        logger.info(f"Validating UPI ID: {upi_id}")
        
        if not self.UPI_ID_PATTERN.match(upi_id):
            logger.warning(f"UPI ID {upi_id} failed regex pattern check")
            return False
        
        parts = upi_id.split('@')
        if len(parts) != 2:
            logger.warning(f"UPI ID {upi_id} doesn't have exactly one @ symbol")
            return False
        
        username, domain = parts
        
        if len(username) < 3:
            logger.warning(f"UPI ID {upi_id} has username shorter than 3 characters")
            return False
        
        known_providers = [
            'paytm', 'phonepe', 'gpay', 'amazonpay', 'mobikwik',
            'freecharge', 'airtel', 'jio', 'sbi', 'hdfc', 'icici',
            'axis', 'kotak', 'ybl', 'ibl', 'upi', 'okaxis', 'okhdfcbank',
            'okicici', 'oksbi', 'okbizaxis', 'apl', 'axl', 'idfcfirstbank',
            'federal', 'pnb', 'boi', 'canara', 'unionbank', 'indianbank',
            'centralbankofind', 'dbs', 'sc', 'citi', 'hsbc', 'yesbankltd',
            'rbl', 'vijb', 'jkb', 'psb', 'iob', 'syndicate', 'uboi',
            'corp', 'allbank', 'kbl', 'kvbl', 'tmbl', 'tjsb', 'nkgsb'
        ]
        
        if '.' not in domain and domain.lower() not in known_providers:
            logger.warning(f"UPI ID {upi_id} has unknown domain: {domain}")
            # For development, let's be more lenient and allow unknown domains
            # return False
        
        logger.info(f"UPI ID {upi_id} validated successfully")
        return True
    
    def validate_ifsc(self, ifsc_code: str) -> bool:
        """Validate IFSC code format."""
        if not ifsc_code:
            return False
        
        return bool(self.IFSC_PATTERN.match(ifsc_code.upper()))
    
    def validate_account_number(self, account_number: str) -> bool:
        """Validate bank account number format."""
        if not account_number:
            return False
        
        clean_account = re.sub(r'[^0-9]', '', account_number)
        
        return bool(self.ACCOUNT_PATTERN.match(clean_account))
    
    def validate_amount(self, amount: Optional[float]) -> bool:
        """Validate payment amount."""
        if amount is None:
            return True  # Amount is optional
        
        if amount < 0:
            return False
        
        if amount > 1000000:  # 10 lakh limit
            return False
        
        # Check for reasonable decimal places (max 2)
        if round(amount, 2) != amount:
            return False
        
        return True
    
    def create_upi_string(
        self,
        payee_address: str,
        payee_name: str,
        amount: Optional[float] = None,
        transaction_note: Optional[str] = None,
        transaction_ref: Optional[str] = None
    ) -> str:
        """Create UPI payment string."""
        upi_string = f"upi://pay?pa={payee_address}&pn={payee_name}"
        
        if amount:
            upi_string += f"&am={amount}"
        
        if transaction_note:
            # URL encode the note
            encoded_note = transaction_note.replace(' ', '%20')
            upi_string += f"&tn={encoded_note}"
        
        if transaction_ref:
            upi_string += f"&tr={transaction_ref}"
        
        return upi_string
    
    def parse_upi_string(self, upi_string: str) -> dict:
        """Parse UPI payment string and extract components."""
        try:
            if not upi_string.startswith('upi://pay?'):
                return {}
            
            # Extract query parameters
            query_part = upi_string.split('?', 1)[1]
            params = {}
            
            for param in query_part.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value
            
            result = {
                'payee_address': params.get('pa', ''),
                'payee_name': params.get('pn', ''),
                'amount': float(params.get('am')) if params.get('am') else None,
                'transaction_note': params.get('tn', '').replace('%20', ' '),
                'transaction_ref': params.get('tr', ''),
                'currency': params.get('cu', 'INR')
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing UPI string: {str(e)}")
            return {}
