import inflect
import re

p = inflect.engine()

def normalize_for_tts(text: str) -> str:
    """
    Chuẩn hóa văn bản chứa số, tiền tệ, phần trăm thành chữ đọc tiếng Anh chuẩn.
    Ví dụ: $65,000 -> sixty-five thousand dollars
    """
    if not text:
        return text

    # Handle $xxx,xxx.xx
    def replace_dollar(match):
        num_str = match.group(1).replace(',', '')
        try:
            words = p.number_to_words(num_str)
            return words + " dollars"
        except:
            return match.group(0)
            
    text = re.sub(r'\$([\d,]+(?:\.\d+)?)', replace_dollar, text)

    # Handle xxx,xxx.xx%
    def replace_percent(match):
        num_str = match.group(1).replace(',', '')
        try:
            words = p.number_to_words(num_str)
            return words + " percent"
        except:
            return match.group(0)
            
    text = re.sub(r'([\d,]+(?:\.\d+)?)\s*%', replace_percent, text)

    # Handle standalone numbers (e.g. 2024, 65000)
    def replace_number(match):
        num_str = match.group(1).replace(',', '')
        try:
            return p.number_to_words(num_str)
        except:
            return match.group(0)
            
    text = re.sub(r'\b([\d,]+(?:\.\d+)?)\b', replace_number, text)

    return text
