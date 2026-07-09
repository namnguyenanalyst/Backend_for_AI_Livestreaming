from ddgs import DDGS
from core.logger import get_logger

logger = get_logger("SearchClient")

def search_internet(query: str, max_results: int = 10) -> str:
    """
    Thực hiện tìm kiếm trên internet bằng DuckDuckGo và trả về kết quả dưới dạng chuỗi văn bản.
    """
    logger.info(f"Đang tìm kiếm trên mạng với từ khóa: '{query}'")
    try:
        results = DDGS().text(query, max_results=max_results)
        
        if not results:
            return "Không tìm thấy kết quả nào."
            
        formatted_results = []
        for idx, res in enumerate(results):
            title = res.get('title', 'Không có tiêu đề')
            body = res.get('body', 'Không có nội dung')
            link = res.get('href', 'Không có link')
            formatted_results.append(f"Kết quả {idx+1}:\nTiêu đề: {title}\nNội dung: {body}\nLink: {link}\n---")
            
        final_text = "\n".join(formatted_results)
        logger.info(f"Đã tìm thấy {len(results)} kết quả.")
        return final_text
    except Exception as e:
        logger.error(f"Lỗi khi tìm kiếm DuckDuckGo: {e}")
        return f"Lỗi khi tìm kiếm: {str(e)}"
