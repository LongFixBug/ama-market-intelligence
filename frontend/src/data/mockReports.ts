import { MarketReport } from "@/types/report";

export const MOCK_REPORTS: Record<string, MarketReport> = {
  "kinh-doanh-kindle": {
    id: "rep-kindle-001",
    topic: "kinh doanh kindle",
    createdAt: "16/08/2026 09:50",
    niche_analysis: {
      summary:
        "Thị trường máy đọc sách Kindle tập trung vào đối tượng học sinh, sinh viên, nhân viên văn phòng và những người yêu thích đọc sách điện tử. Điểm độc đáo (USP) của Kindle là màn hình công nghệ E-ink chống mỏi mắt, thời lượng pin siêu dài và hệ sinh thái sách phong phú từ Amazon. Cơ hội cạnh tranh nằm ở việc phân phối các dòng máy chính hãng, bảo hành tốt và cung cấp dịch vụ hỗ trợ tải sách, cài đặt từ điển tiếng Việt.",
      growth_potential: "Cao trong ngách mục tiêu",
    },
    pricing: {
      price_range: "2.500.000 VNĐ - 4.500.000 VNĐ",
      rationale:
        "Mức giá này phù hợp với các dòng máy phổ biến như Kindle Paperwhite (bản mới nhất), cân bằng giữa sức mua của người tiêu dùng Việt Nam và biên độ lợi nhuận cho nhà bán lẻ sau khi cộng chi phí nhập khẩu và vận chuyển.",
      tagline: "Tối ưu điểm hòa vốn & tỷ lệ chuyển đổi ban đầu",
    },
    risks: [
      {
        index: 1,
        title: "Cạnh tranh gay gắt từ các thương hiệu máy đọc sách Android khác như Kobo, Boox.",
      },
      {
        index: 2,
        title: "Rủi ro về nguồn hàng xách tay biến động giá và chính sách bảo hành quốc tế phức tạp.",
      },
      {
        index: 3,
        title: "Tâm lý người dùng e ngại vì màn hình đơn sắc (đối với dòng cơ bản) hoặc giá cao (đối với dòng Oasis/Scribe).",
      },
    ],
    seo_keywords: [
      "máy đọc sách kindle",
      "kindle paperwhite chính hãng",
      "đánh giá máy đọc sách kindle",
      "nên mua kindle loại nào",
      "mua kindle giá rẻ",
    ],
    ai_prompts: [
      {
        prompt:
          "Viết một bài đăng Facebook quảng cáo máy đọc sách Kindle Paperwhite hướng đến đối tượng dân văn phòng thích đọc sách vào ban đêm.",
      },
      {
        prompt:
          "Lập bảng so sánh chi tiết thông số kỹ thuật giữa Kindle Paperwhite và Kobo Clara để tư vấn cho khách hàng phân vân giữa 2 dòng máy này.",
      },
      {
        prompt:
          "Tạo kịch bản video ngắn (TikTok/Reels) 30 giây review 3 lý do tại sao nên đầu tư một chiếc máy đọc sách Kindle.",
      },
    ],
  },
  "my-pham-thuan-chay": {
    id: "rep-vegan-002",
    topic: "Thị trường mỹ phẩm thuần chay Việt Nam",
    createdAt: "16/08/2026 09:52",
    niche_analysis: {
      summary:
        "Thị trường mỹ phẩm thuần chay (Vegan Cosmetics) tại Việt Nam bùng nổ mạnh mẽ nhờ thế hệ Gen Z và phụ nữ văn phòng ưu tiên nguyên liệu nông sản bản địa lành tính (bí đao, tràm trà, cà phê Đắk Lắk). Điểm độc đáo (USP) là cam kết 100% không thử nghiệm trên động vật và chứng nhận quốc tế (Leaping Bunny, The Vegan Society). Cơ hội cạnh tranh lớn nằm ở dòng kem chống nắng kiềm dầu không vón cục và bộ sản phẩm phục hồi da nhạy cảm.",
      growth_potential: "Rất cao (18.5% CAGR)",
    },
    pricing: {
      price_range: "150.000 VNĐ - 380.000 VNĐ",
      rationale:
        "Khoảng giá Mass-Premium giúp sản phẩm tiếp cận ngay tệp khách hàng trẻ từ 18-35 tuổi mà không gặp rào cản tài chính quá lớn, đồng thời đảm bảo biên lợi nhuận gộp 60-68% để đầu tư marketing đa kênh.",
      tagline: "Tối ưu điểm hòa vốn & tỷ lệ chuyển đổi ban đầu",
    },
    risks: [
      {
        index: 1,
        title: "Cạnh tranh trực tiếp từ các thương hiệu đầu ngành như Cocoon, Cỏ Mềm và các hãng dược mỹ phẩm Hàn Quốc (Klairs, Skin1004).",
      },
      {
        index: 2,
        title: "Rủi ro biến tính và oxy hóa sản phẩm nhanh hơn do khí hậu nhiệt đới ẩm và hạn chế chất bảo quản hóa học.",
      },
      {
        index: 3,
        title: "Vấn nạn hàng giả, kem trộn đội lốt 'thiên nhiên thuần chay' gây nhiễu loạn niềm tin người tiêu dùng.",
      },
    ],
    seo_keywords: [
      "mỹ phẩm thuần chay việt nam",
      "kem chống nắng thuần chay cho da dầu mụn",
      "review mỹ phẩm thuần chay tốt nhất",
      "mỹ phẩm cho mẹ bầu an toàn",
      "cocoon mỹ phẩm thuần chay chính hãng",
    ],
    ai_prompts: [
      {
        prompt:
          "Viết bài viết Seeding TikTok/Facebook chia sẻ câu chuyện hành trình nghiên cứu mỹ phẩm thuần chay từ nông sản Việt sạch.",
      },
      {
        prompt:
          "Lập kịch bản Livestream bán hàng Mega Live 2 tiếng trên TikTok Shop cho combo 3 bước dưỡng da thuần chay mờ thâm ngừa mụn.",
      },
      {
        prompt:
          "Viết email marketing gửi khách hàng thân thiết giải thích sự khác biệt giữa mỹ phẩm thuần chay (Vegan) và mỹ phẩm thiên nhiên thông thường.",
      },
    ],
  },
};

export function generateDynamicMockReport(topic: string): MarketReport {
  const normalized = topic.toLowerCase();
  if (normalized.includes("kindle") || normalized.includes("sách")) {
    return { ...MOCK_REPORTS["kinh-doanh-kindle"], topic };
  }
  if (normalized.includes("mỹ phẩm") || normalized.includes("vegan") || normalized.includes("thuần chay")) {
    return { ...MOCK_REPORTS["my-pham-thuan-chay"], topic };
  }

  return {
    id: "rep-" + Math.random().toString(36).substring(2, 8),
    topic: topic,
    createdAt: new Date().toLocaleString("vi-VN"),
    niche_analysis: {
      summary: `Thị trường '${topic}' tại Việt Nam đang có xu hướng dịch chuyển mạnh sang các giải pháp cá nhân hóa, tối ưu chi phí và trải nghiệm số. Điểm độc đáo (USP) nằm ở khả năng giải quyết trực diện điểm đau của người dùng với chi phí hợp lý. Cơ hội cạnh tranh then chốt là tập trung vào dịch vụ khách hàng xuất sắc, xây dựng thương hiệu uy tín và phân phối đa kênh (E-commerce + Social Commerce).`,
      growth_potential: "Cao trong ngách mục tiêu",
    },
    pricing: {
      price_range: "250.000 VNĐ - 1.200.000 VNĐ",
      rationale: `Mức giá này nằm ở khoảng giá ngọt (Sweet Spot) của thị trường '${topic}', cân bằng giữa khả năng chi trả của nhóm khách hàng tiên phong và biên độ lợi nhuận gộp từ 55% - 65% để bù đắp chi phí quảng cáo, vận hành ban đầu.`,
      tagline: "Tối ưu điểm hòa vốn & tỷ lệ chuyển đổi ban đầu",
    },
    risks: [
      {
        index: 1,
        title: "Cạnh tranh về giá và khuyến mãi mạnh mẽ từ các đối thủ lớn đã có mặt lâu năm trong ngành.",
      },
      {
        index: 2,
        title: "Biến động chi phí thu hút khách hàng mới (CAC) trên các nền tảng quảng cáo số (Facebook, TikTok, Google).",
      },
      {
        index: 3,
        title: "Rủi ro duy trì chất lượng dịch vụ và thời gian giao hàng/hỗ trợ khi quy mô khách hàng tăng trưởng nhanh.",
      },
    ],
    seo_keywords: [
      `${topic.toLowerCase()} giá rẻ`,
      `đánh giá ${topic.toLowerCase()} tốt nhất`,
      `hướng dẫn ${topic.toLowerCase()} từ a đến z`,
      `kinh nghiệm chọn mua ${topic.toLowerCase()}`,
      `top thương hiệu ${topic.toLowerCase()} uy tín`,
    ],
    ai_prompts: [
      {
        prompt: `Viết một bài đăng Facebook quảng cáo ${topic} hướng đến khách hàng mục tiêu nhấn mạnh vào ưu đãi độc quyền và cam kết chất lượng.`,
      },
      {
        prompt: `Lập bảng so sánh chi tiết ưu và nhược điểm giữa giải pháp ${topic} của chúng tôi so với các bên truyền thống trên thị trường.`,
      },
      {
        prompt: `Tạo kịch bản video ngắn (TikTok/Reels) 30 giây review 3 lý do tại sao nên chọn giải pháp ${topic} này ngay hôm nay.`,
      },
    ],
  };
}
