"""Manages, resolves, and describes style rules for the supported video script styles."""

from typing import List, Optional, Dict
from src.script_engine.constants import SUPPORTED_STYLES


# Rich descriptions/guidelines for each style to inject into prompt generator
STYLE_GUIDELINES: Dict[str, str] = {
    "Problem Solution": (
        "Cấu trúc kinh điển: 3 giây đầu nêu bật nỗi đau/vấn đề nhức nhối của khách hàng. "
        "Tiếp theo đưa ra giải pháp là sản phẩm này, chứng minh tính hiệu quả và kêu gọi hành động (CTA) rõ ràng."
    ),
    "Review": (
        "Trải nghiệm khách quan, chi tiết về sản phẩm. Liệt kê các ưu nhược điểm thực tế, "
        "mở hộp, cận cảnh chất liệu/chất lượng sản phẩm. Giọng điệu chân thật, đáng tin cậy."
    ),
    "Native Review": (
        "Cách tiếp cận cực kỳ tự nhiên giống như một người dùng chia sẻ mẹo, không mang tính quảng cáo lộ liễu. "
        "Kể về việc vô tình biết tới và yêu thích sản phẩm."
    ),
    "POV": (
        "Góc nhìn thứ nhất (Point of View). Tạo tình huống nhập vai thực tế (ví dụ: 'POV: Bạn đi làm muộn và...'). "
        "Giúp người xem cảm thấy chính mình đang ở trong câu chuyện."
    ),
    "Luxury": (
        "Phong cách sang trọng, đẳng cấp. Ngôn từ trau chuốt, tinh tế. Nhấn mạnh vào trải nghiệm thượng lưu, "
        "thiết kế tinh xảo, cảm giác độc bản và giá trị thương hiệu vượt trội."
    ),
    "ASMR": (
        "Tập trung cực kỳ cao độ vào âm thanh thực tế: tiếng gõ, tiếng xé bao bì, tiếng rót nước, "
        "tiếng thì thầm. Câu thoại ngắn, ngắt quãng dài để chừa không gian cho hiệu ứng âm thanh."
    ),
    "Comparison": (
        "So sánh trực tiếp sản phẩm với một giải pháp thông thường hoặc sản phẩm đối thủ (không dìm hàng lộ liễu). "
        "Làm rõ sự khác biệt vượt trội về giá cả, hiệu năng hoặc thiết kế để người mua dễ đưa ra quyết định."
    ),
    "Storytelling": (
        "Kể một câu chuyện có bối cảnh, nhân vật, diễn biến và cao trào. Sản phẩm đóng vai trò "
        "là nút thắt giải quyết vấn đề của nhân vật chính ở cuối câu chuyện."
    ),
    "Lifestyle": (
        "Lồng ghép sản phẩm vào hoạt động thường nhật một cách tự nhiên (một ngày làm việc, đi du lịch, tập thể dục). "
        "Tập trung truyền tải năng lượng tích cực, phong cách sống hiện đại và thẩm mỹ cao."
    ),
    "Emotional": (
        "Tập trung khai thác cảm xúc: sự biết ơn, tình yêu gia đình, sự nỗ lực vươn lên. "
        "Lời thoại ấm áp, tốc độ nói chậm rãi, nhấn nhá sâu sắc."
    ),
    "Expert": (
        "Phong cách chuyên gia chuyên sâu. Sử dụng kiến thức khoa học, thuật ngữ chuyên môn hoặc số liệu để "
        "chứng minh công dụng sản phẩm. Giọng điệu tự tin, uy tín, thuyết phục tuyệt đối."
    ),
    "Funny": (
        "Hài hước, hóm hỉnh. Tạo các tình huống dở khóc dở cười, meme thịnh hành hoặc cách nói cường điệu vui nhộn. "
        "Giúp người xem giải trí đồng thời ghi nhớ sâu sắc về sản phẩm."
    ),
    "Premium": (
        "Tinh giản nhưng đẳng cấp. Thích hợp cho sản phẩm trung và cao cấp. Tập trung vào các đường nét thiết kế, "
        "sự tiện ích thông minh và cảm giác thỏa mãn khi sở hữu."
    ),
    "Minimal": (
        "Tối giản tối đa lời thoại, chỉ tập trung vào thông điệp cốt lõi cực kỳ cô đọng. "
        "Sử dụng hình ảnh tĩnh hoặc chuyển động chậm để người xem tự cảm nhận sâu sắc."
    ),
}


class StyleSelector:
    """Orchestrates style-specific guidelines and selects non-duplicate style arrays."""

    @classmethod
    def get_guideline(cls, style_name: str) -> str:
        """Returns prompt-ready copywriting instructions for a specific script style."""
        return STYLE_GUIDELINES.get(style_name, STYLE_GUIDELINES["Problem Solution"])

    @classmethod
    def select_unique_styles(cls, requested_quantity: int, preferred_style: Optional[str] = None) -> List[str]:
        """Returns a list of unique styles of length requested_quantity.

        Assures 'No Duplicate Style' is respected by choosing distinct styles from SUPPORTED_STYLES.
        If preferred_style is specified, it is placed first in the list.
        """
        styles = []
        available = [s for s in SUPPORTED_STYLES]

        # Put preferred style first if valid
        if preferred_style and preferred_style in available:
            styles.append(preferred_style)
            available.remove(preferred_style)

        # Fill up with other unique styles
        while len(styles) < requested_quantity and available:
            styles.append(available.pop(0))

        # If quantity > available styles (e.g. user requested 30 scripts), we must wrap around
        while len(styles) < requested_quantity:
            for s in SUPPORTED_STYLES:
                styles.append(s)
                if len(styles) >= requested_quantity:
                    break

        return styles[:requested_quantity]
