import re

def clean_junk_text(text: str) -> str:
    if not text:
        return text
        
    # 1. Xóa các Markdown in đậm/in nghiêng (**, *, __, _)
    # Lấy nội dung bên trong markdown
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    
    # 2. Xóa Headers markdown (#, ##, ###)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    
    # 3. Xóa Emojis
    # Emoji nằm trong các dải Unicode cụ thể
    emoji_pattern = re.compile(
        u"(\ud83d[\ude00-\ude4f])|"  # emoticons
        u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
        u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
        u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
        u"(\ud83c[\udde0-\uddff])|"  # flags (iOS)
        u"([\u2600-\u26FF])|"        # miscellaneous symbols
        u"([\u2700-\u27BF])"         # dingbats
        "+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)
    
    # Một cách khác mạnh mẽ hơn để xóa tất cả ký tự không mong muốn (chỉ giữ lại chữ, số, dấu câu cơ bản)
    # Tuy nhiên vì có tiếng Việt nên không thể dùng [a-zA-Z0-9] được.
    # Nên dùng thư viện emoji, nhưng để tránh cài thêm thư viện, ta dùng regex dải unicode cao.
    # Xóa các ký tự unicode cao (thường là emoji và symbol rác) không thuộc bảng chữ cái tiếng Việt/Latin
    # Bảng chữ cái Latin và tiếng Việt nằm trong khoảng \u0000-\u024F và \u1E00-\u1EFF
    # Dấu câu nằm rải rác, nhưng ta chỉ xóa những dải chuyên chứa symbol.
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    
    # 4. Xóa các ký tự gạch đầu dòng Markdown đặc biệt như - , * đầu dòng và các đường kẻ ---
    text = re.sub(r'^\s*[-*]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^-{3,}$', '', text, flags=re.MULTILINE)
    
    # 5. Xóa các khoảng trắng thừa
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()
