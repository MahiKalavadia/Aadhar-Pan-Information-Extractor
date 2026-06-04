import re

def valid_pan(pan: str):
        regex = r"[A-Z]{5}[0-9]{4}[A-Z]{1}"
        pattern = re.compile(regex)
        if (re.match(pattern, pan)) and len(pan) == 10:
            return True
        else:
            return False
        
def valid_aadhar(aadhar:int):
        aadhar = aadhar.replace(" ", "")
        regex = r"[0-9]{12}"
        pattern = re.compile(regex)
        if (re.match(pattern, aadhar)) and len(aadhar) == 12:
            return True
        else:
            return False