import { MarketReport } from "@/types/report";

export const MOCK_REPORTS: Record<string, MarketReport> = {
  "my-pham-thuan-chay": {
    id: "rep-001",
    topic: "Thị trường mỹ phẩm thuần chay Việt Nam",
    createdAt: "16/08/2026 08:30",
    market_size_est: "~2,400 Tỷ VNĐ (2025-2026)",
    growth_rate: "18.5% CAGR",
    executive_summary:
      "Thị trường mỹ phẩm thuần chay (Vegan & Cruelty-free Cosmetics) tại Việt Nam đang bước vào giai đoạn tăng trưởng thần tốc nhờ sự chuyển dịch nhận thức của thế hệ Gen Z và Millennials. Người tiêu dùng ngày càng ưu tiên các sản phẩm lành tính từ thực vật nhiệt đới bản địa (tràm trà, bí đao, cà phê Đắk Lắk, bơ Đắk Nông) có chứng nhận quốc tế (Leaping Bunny, The Vegan Society). Rào cản lớn nhất nằm ở việc xây dựng niềm tin về hiệu quả thực sự so với các hoạt chất hóa học tổng hợp và sự cạnh tranh gay gắt từ các thương hiệu nhập khẩu Hàn Quốc, Nhật Bản.",
    target_audience: [
      {
        title: "Gen Z Ý Thức Sinh Thái (18 - 25 tuổi)",
        desc: "Học sinh, sinh viên và người mới đi làm quan tâm đến lối sống xanh, bao bì tái chế và bảo vệ động vật.",
        pain_points: [
          "Ngân sách có hạn (150k - 300k/sản phẩm)",
          "Dễ bị mụn/kích ứng do môi trường đô thị",
          "Thất vọng vì nhiều nhãn hàng greenwashing (quảng cáo xanh giả tạo)",
        ],
      },
      {
        title: "Nữ Nhân Viên Văn Phòng (26 - 35 tuổi)",
        desc: "Thu nhập ổn định (12M - 30M), tìm kiếm giải pháp phục hồi da nhẹ dịu, chống lão hóa tự nhiên.",
        pain_points: [
          "Da stress, khô ráp do ngồi máy lạnh lâu",
          "Cần sản phẩm thẩm thấu nhanh, không bết dính dưới lớp makeup",
          "Yêu cầu minh bạch 100% bảng thành phần",
        ],
      },
      {
        title: "Mẹ Bầu & Phụ Nữ Cho Con Bú",
        desc: "Nhóm khách hàng cực kỳ khắt khe, chỉ sử dụng sản phẩm cam kết 0% hương liệu, paraben, cồn khô.",
        pain_points: [
          "Khó tìm sản phẩm trị nám/rạn da an toàn tuyệt đối cho thai nhi",
          "Giá các hãng hữu cơ châu Âu quá đắt đỏ",
        ],
      },
    ],
    market_gaps: [
      {
        title: "Dòng chống nắng thuần chay nâng tone kiềm dầu",
        opportunity:
          "Các loại kem chống nắng thuần chay hiện nay thường bị bóng nhờn hoặc vón cục ở khí hậu nhiệt đới ẩm Việt Nam.",
        priority: "Cao",
      },
      {
        title: "Mỹ phẩm cho nam giới (Vegan Men Skincare)",
        opportunity:
          "Nam giới trẻ có nhu cầu dưỡng da sạch mụn cực cao nhưng thị trường chỉ tập trung vào nữ giới.",
        priority: "Cao",
      },
      {
        title: "Mỹ phẩm Refill & Giảm rác thải nhựa",
        opportunity:
          "Mô hình mua chai nhôm tái sử dụng và mua túi nạp (refill pouch) giúp giảm 40% giá thành và 80% rác thải.",
        priority: "Trung bình",
      },
    ],
    swot: {
      strengths: [
        "Nguồn nguyên liệu nông sản Việt dồi dào, độc đáo và giàu dược tính",
        "Chi phí sản xuất nội địa tối ưu hơn hàng ngoại nhập",
        "Sự ủng hộ mạnh mẽ với phong trào 'Người Việt dùng hàng Việt chất lượng cao'",
      ],
      weaknesses: [
        "Hạn sử dụng ngắn hơn do hạn chế chất bảo quản hóa học",
        "Chi phí kiểm nghiệm và xin chứng chỉ thuần chay quốc tế đắt đỏ",
        "Công nghệ chiết xuất sâu còn phụ thuộc vào dây chuyền nhập khẩu",
      ],
      opportunities: [
        "Xu hướng E-commerce & Live Commerce trên TikTok Shop / Shopee Mall bùng nổ",
        "Thị trường xuất khẩu sang các nước Đông Nam Á (Thái Lan, Philippines, Indonesia)",
        "Nhu cầu quà tặng doanh nghiệp theo phong cách eco-friendly",
      ],
      threats: [
        "Mỹ phẩm giả, kem trộn đội lốt 'thảo mộc thiên nhiên' làm xói mòn lòng tin",
        "Các tập đoàn đa quốc gia (L'Oréal, Unilever) mua lại hoặc tung ra các dòng Vegan giá rẻ",
        "Biến động giá nguyên liệu nông sản theo mùa vụ",
      ],
    },
    competitors: [
      {
        name: "Cocoon Vietnam",
        type: "Trực tiếp",
        positioning: "Thương hiệu mỹ phẩm thuần chay 100% dẫn đầu thị trường Việt Nam",
        strengths: ["Nhận diện thương hiệu số 1", "Chứng nhận Leaping Bunny & Vegan Society", "Kênh phân phối phủ khắp Hasaki, Guardian, Watsons"],
        weaknesses: ["Một số sản phẩm dung tích lớn khó mang theo", "Chưa mạnh về dòng đặc trị chuyên sâu (Active Retinol, BHA mạnh)"],
        price_range: "120.000đ - 380.000đ",
        market_share_est: "38%",
        website: "https://cocoonvietnam.com",
      },
      {
        name: "Cỏ Mềm Homelab",
        type: "Trực tiếp",
        positioning: "Mỹ phẩm Lành & Thật cho cả gia đình và mẹ bầu",
        strengths: ["Chuỗi cửa hàng bán lẻ riêng rộng khắp", "Tệp khách hàng trung thành cao", "Sản phẩm đa dạng từ chăm sóc cá nhân đến makeup"],
        weaknesses: ["Bao bì thiết kế còn truyền thống, chưa thu hút mạnh Gen Z sành điệu"],
        price_range: "90.000đ - 450.000đ",
        market_share_est: "25%",
        website: "https://comem.vn",
      },
      {
        name: "Klairs / Skin1004 (Hàn Quốc)",
        type: "Gián tiếp",
        positioning: "Dược mỹ phẩm thuần chay / rau má dịu nhẹ từ K-Beauty",
        strengths: ["Công thức tối ưu cho da nhạy cảm", "Marketing quốc tế mạnh", "Review rầm rộ trên YouTube/TikTok"],
        weaknesses: ["Giá thành cao hơn 30-50% so với thương hiệu nội địa", "Nhiều hàng xách tay trôi nổi khó kiểm soát"],
        price_range: "280.000đ - 650.000đ",
        market_share_est: "22%",
      },
      {
        name: "Sukano / The Body Shop",
        type: "Gián tiếp",
        positioning: "Thương hiệu chăm sóc cơ thể & da hữu cơ toàn cầu",
        strengths: ["Di sản thương hiệu lâu đời", "Tiêu chuẩn kiểm định châu Âu"],
        weaknesses: ["Mức giá cao, khó tiếp cận học sinh sinh viên", "Khó khăn trong tái cấu trúc chuỗi cửa hàng vật lý"],
        price_range: "350.000đ - 1.200.000đ",
        market_share_est: "15%",
      },
    ],
    pricing: {
      min_market_price: 120000,
      median_market_price: 260000,
      recommended_price: 245000,
      premium_market_price: 580000,
      unit: "VNĐ / sản phẩm",
      margin_est: "62% - 70% Gross Margin",
      pricing_logic:
        "Mức giá khuyến nghị 245.000 VNĐ nằm ở 'sweet-spot' của phân khúc Mass-Premium: Đủ cao để khẳng định chất lượng nguyên liệu đạt chuẩn chứng nhận, nhưng đủ thấp để khách hàng Gen Z và dân văn phòng ra quyết định mua ngay lập tức mà không cần đắn đo quá lâu.",
      tiers: [
        {
          tier: "Starter / Trial Size",
          price: 145000,
          description: "Dung tích 50ml hoặc Minikit 3 món trải nghiệm",
          features: ["Giảm rào cản thử nghiệm lần đầu", "Tối ưu làm mồi phễu trên TikTok Live", "Kèm sample miễn phí dòng khác"],
        },
        {
          tier: "Core Standard (Khuyên dùng)",
          price: 245000,
          description: "Dung tích chuẩn 150ml - 200ml dùng trong 2-3 tháng",
          features: ["Bao bì vòi pump tiện lợi", "Chứng nhận thuần chay in nổi", "Tặng túi vải canvas khi mua combo"],
        },
        {
          tier: "Eco Refill Duo / Family Size",
          price: 420000,
          description: "Combo 2 chai hoặc Túi Refill tiết kiệm 500ml",
          features: ["Tiết kiệm 25% cho khách hàng trung thành", "Giảm 70% nhựa nguyên sinh", "Tích điểm thành viên VIP"],
        },
      ],
    },
    risks: [
      {
        category: "Pháp lý",
        risk_title: "Gian lận chứng chỉ thuần chay & greenwashing",
        risk_level: "Cao",
        impact: "Mất uy tín nghiêm trọng nếu bị cơ quan chức năng hoặc cộng đồng mạng bóc phốt thành phần không thuần chay.",
        mitigation: "Chủ động gửi mẫu kiểm nghiệm tại các viện độc lập (Quatest 3) và minh bạch hóa toàn bộ giấy tờ COA nguyên liệu lên website.",
      },
      {
        category: "Vận hành",
        risk_title: "Oxy hóa và biến đổi chất lượng do khí hậu nhiệt đới",
        risk_level: "Trung bình",
        impact: "Sản phẩm đổi màu/mùi khi lưu kho nhiệt độ cao.",
        mitigation: "Sử dụng chai thủy tinh tối màu hoặc chai hút chân không (airless pump), bổ sung hệ chất chống oxy hóa tự nhiên (Vitamin E, chiết xuất hương thảo).",
      },
      {
        category: "Đối thủ",
        risk_title: "Cuộc chiến phá giá trên sàn thương mại điện tử",
        risk_level: "Cao",
        impact: "Xói mòn biên lợi nhuận và hình ảnh thương hiệu.",
        mitigation: "Không giảm giá trực tiếp mà tập trung tặng quà giá trị cao (GWP - Gift with Purchase), xây dựng chương trình hội viên độc quyền.",
      },
    ],
    seo_strategy: [
      {
        keyword: "mỹ phẩm thuần chay việt nam",
        intent: "Mua hàng (Commercial)",
        search_volume_est: "Cao",
        competition: "Cao",
        content_angle: "Top 7 thương hiệu mỹ phẩm thuần chay Việt Nam tốt nhất 2026",
      },
      {
        keyword: "kem chống nắng thuần chay cho da dầu mụn",
        intent: "Mua hàng (Commercial)",
        search_volume_est: "Rất cao",
        competition: "Trung bình",
        content_angle: "Review so sánh chi tiết kem chống nắng thuần chay không vón cục",
      },
      {
        keyword: "mỹ phẩm cho mẹ bầu an toàn",
        intent: "Tìm hiểu (Informational)",
        search_volume_est: "Cao",
        competition: "Trung bình",
        content_angle: "Cẩm nang chọn mỹ phẩm 0% hóa chất độc hại cho phụ nữ mang thai",
      },
      {
        keyword: "phân biệt mỹ phẩm thuần chay và hữu cơ",
        intent: "Tìm hiểu (Informational)",
        search_volume_est: "Trung bình",
        competition: "Thấp",
        content_angle: "Sự thật về Cruelty-free vs Vegan vs Organic mà bạn chưa biết",
      },
    ],
    gtm_roadmap: [
      {
        phase: "Giai đoạn 1: Thử nghiệm & Xây dựng uy tín (Tháng 1 - 2)",
        timeline: "Tuần 1 - Tuần 8",
        key_actions: [
          "Gửi 200 bộ kit Seeding cho Micro-KOLs da liễu & Beauty Bloggers chân thật",
          "Mở bán giới hạn (Pre-order) 1,000 suất đầu tiên kèm quà tặng độc quyền",
          "Thu thập 100+ review video thực tế về khả năng lành tính trên da nhạy cảm",
        ],
      },
      {
        phase: "Giai đoạn 2: Bùng nổ chuyển đổi E-commerce (Tháng 3 - 4)",
        timeline: "Tuần 9 - Tuần 16",
        key_actions: [
          "Chạy chiến dịch Mega Live trên TikTok Shop kết hợp Top Creator",
          "Mở gian hàng Shopee Mall và LazMall với cam kết giao hàng 2h",
          "Triển khai Performance Ads nhắm vào tệp tìm kiếm từ khóa giải quyết vấn đề da",
        ],
      },
      {
        phase: "Giai đoạn 3: Mở rộng kênh Offline & B2B (Tháng 5 - 6)",
        timeline: "Tuần 17 - Tuần 24",
        key_actions: [
          "Đưa sản phẩm lên kệ chuỗi bán lẻ Hasaki, BeautyBox, Cocolux",
          "Hợp tác với các spa / trung tâm yoga & chăm sóc sức khỏe theo gói quà tặng xanh",
          "Ra mắt dòng sản phẩm Refill tiết kiệm",
        ],
      },
    ],
    graph_data: {
      nodes: [
        { id: "market", name: "Mỹ Phẩm Thuần Chay VN", category: "product", size: 24 },
        { id: "cocoon", name: "Cocoon Vietnam", category: "competitor", size: 18 },
        { id: "comem", name: "Cỏ Mềm", category: "competitor", size: 16 },
        { id: "kbeauty", name: "Klairs/Skin1004", category: "competitor", size: 14 },
        { id: "genz", name: "Gen Z Eco-conscious", category: "segment", size: 16 },
        { id: "office", name: "Nữ Văn Phòng", category: "segment", size: 15 },
        { id: "mom", name: "Mẹ Bầu & Sau Sinh", category: "segment", size: 13 },
        { id: "price_sweet", name: "Khoảng giá 245K", category: "price", size: 14 },
        { id: "risk_gw", name: "Greenwashing Risk", category: "risk", size: 12 },
        { id: "sunscreen", name: "Kem Chống Nắng Kiềm Dầu", category: "keyword", size: 14 },
      ],
      links: [
        { source: "market", target: "cocoon", relationship: "DOMINATED_BY" },
        { source: "market", target: "comem", relationship: "COMPETES_WITH" },
        { source: "market", target: "kbeauty", relationship: "IMPORTS_COMPETITION" },
        { source: "cocoon", target: "genz", relationship: "STRONGLY_TARGETS" },
        { source: "comem", target: "mom", relationship: "STRONGLY_TARGETS" },
        { source: "market", target: "price_sweet", relationship: "OPTIMAL_PRICED_AT" },
        { source: "market", target: "risk_gw", relationship: "VULNERABLE_TO" },
        { source: "market", target: "sunscreen", relationship: "BIGGEST_GAP" },
        { source: "office", target: "sunscreen", relationship: "HIGH_DEMAND_FOR" },
      ],
    },
  },
  "nuoc-ep-van-phong": {
    id: "rep-002",
    topic: "Nước ép trái cây tươi đóng chai ngách văn phòng",
    createdAt: "16/08/2026 08:45",
    market_size_est: "~850 Tỷ VNĐ / năm (Hà Nội & TP.HCM)",
    growth_rate: "22% CAGR",
    executive_summary:
      "Thị trường F&B đồ uống healthy giao tận nơi cho nhân viên văn phòng tại các tòa nhà trung tâm đang bùng nổ mạnh mẽ. Nhu cầu 'detox', bổ sung vitamin, thay thế trà sữa nhiều đường bằng nước ép nguyên chất không đường (Cold-pressed Juice) ngày càng trở thành thói quen hàng ngày. Điểm mấu chốt để thành công trong ngách này là: Mô hình đăng ký gói tuần/tháng (Subscription Model), công nghệ ép lạnh giữ nguyên enzyme 72h và cam kết giao đúng giờ trước 8h30 sáng.",
    target_audience: [
      {
        title: "Dân Công Sở & Lãnh Đạo Trẻ (24 - 40 tuổi)",
        desc: "Làm việc tại các tòa nhà văn phòng hạng A/B, thu nhập 15M - 45M/tháng.",
        pain_points: [
          "Ít thời gian ăn rau củ quả tươi",
          "Ngồi nhiều dẫn đến tích mỡ bụng, mệt mỏi vào buổi chiều",
          "Ngại đi mua ngoài trời nắng nóng",
        ],
      },
      {
        title: "Nhóm Đồng Nghiệp Mua Chung (Group Buy)",
        desc: "Văn phòng 5 - 15 người thường rủ nhau order đồ uống xế chiều 14h - 15h.",
        pain_points: [
          "Phí ship đắt nếu đặt lẻ từng chai",
          "Mỗi người thích một khẩu vị khác nhau (ngọt dịu, chua thanh, detox)",
        ],
      },
    ],
    market_gaps: [
      {
        title: "Gói Subscription giao định kỳ theo tuần (5 ngày làm việc)",
        opportunity: "Đa số các quán chỉ bán theo đơn lẻ qua ShopeeFood/GrabFood, chưa có giải pháp giao đúng giờ mỗi sáng với giá ưu đãi cố định.",
        priority: "Cao",
      },
      {
        title: "Nước ép cá nhân hóa theo mục tiêu sức khỏe",
        opportunity: "Bộ liệu trình: Sáng bừng da, Trưa nhẹ bụng, Chiều tỉnh táo không cần cà phê.",
        priority: "Cao",
      },
    ],
    swot: {
      strengths: ["Thói quen chi tiêu cao và ổn định của dân văn phòng", "Biên lợi nhuận gộp ngành F&B cao (60-70%)"],
      weaknesses: ["Hạn sử dụng cực ngắn (2-3 ngày) nếu không dùng chất bảo quản", "Phụ thuộc vào năng lực vận hành giao hàng giờ cao điểm"],
      opportunities: ["Hợp tác bán B2B cho các pantry doanh nghiệp công nghệ, ngân hàng"],
      threats: ["Cạnh tranh từ các chuỗi cà phê lớn (Phúc Long, Highlands) thêm menu nước ép"],
    },
    competitors: [
      {
        name: "Lumi Juice / Juicentin",
        type: "Trực tiếp",
        positioning: "Thương hiệu nước ép lạnh cao cấp nguyên chất 100%",
        strengths: ["Máy ép lạnh công nghiệp xịn", "Menu detox đa dạng"],
        weaknesses: ["Giá thành khá cao (>65k/chai)", "Phí ship chưa tối ưu"],
        price_range: "55.000đ - 85.000đ",
        market_share_est: "30%",
      },
      {
        name: "Các xe nước ép / Quán vỉa hè chân toà nhà",
        type: "Gián tiếp",
        positioning: "Giá rẻ, mua nhanh trực tiếp",
        strengths: ["Giá rẻ (25k - 35k)", "Tiện lợi ngay cửa thang máy"],
        weaknesses: ["Không rõ nguồn gốc hoa quả, dễ pha đường hoá học và đá bẩn", "Không có thương hiệu"],
        price_range: "25.000đ - 35.000đ",
        market_share_est: "45%",
      },
    ],
    pricing: {
      min_market_price: 30000,
      median_market_price: 48000,
      recommended_price: 45000,
      premium_market_price: 85000,
      unit: "VNĐ / chai 330ml",
      margin_est: "58% Gross Margin",
      pricing_logic: "Mức giá 45.000đ cho chai ép lạnh 330ml tương đương 1 ly trà sữa hay cà phê hạt, rất dễ thuyết phục khách hàng chuyển đổi sang thói quen sống lành mạnh hơn.",
      tiers: [
        {
          tier: "Chai Đơn Lẻ",
          price: 49000,
          description: "Chai 330ml ép tươi trong ngày",
          features: ["Không đường, không nước lọc", "Giao nhanh dưới 30 phút"],
        },
        {
          tier: "Gói Tuần Healthy Office (Khuyên dùng)",
          price: 199000,
          description: "5 chai cho 5 ngày làm việc (Chỉ 39.8k/chai)",
          features: ["Miễn phí giao tận bàn làm việc trước 9h", "Đổi vị mỗi ngày", "Tặng túi giữ nhiệt"],
        },
        {
          tier: "Gói Team 10 Người",
          price: 380000,
          description: "Set 10 chai mix đủ vị cho giờ giải lao",
          features: ["Tiết kiệm 22%", "Kèm ống hút cỏ & khay giấy bảo vệ môi trường"],
        },
      ],
    },
    risks: [
      {
        category: "Vận hành",
        risk_title: "Hỏng hóc và chua nước ép do thời tiết nắng nóng",
        risk_level: "Cao",
        impact: "Khách hàng khiếu nại, mất uy tín ngay lập tức.",
        mitigation: "Bắt buộc dùng túi đá gel giữ nhiệt trong suốt quá trình shipper di chuyển.",
      },
      {
        category: "Tài chính",
        risk_title: "Biến động giá trái cây đầu vào theo mùa",
        risk_level: "Trung bình",
        impact: "Giảm biên lợi nhuận.",
        mitigation: "Ký hợp đồng bao tiêu dài hạn với các nhà vườn VietGAP tại Tiền Giang, Đà Lạt.",
      },
    ],
    seo_strategy: [
      {
        keyword: "giao nước ép tận nơi văn phòng",
        intent: "Mua hàng (Commercial)",
        search_volume_est: "Cao",
        competition: "Thấp",
        content_angle: "Dịch vụ giao nước ép lạnh tận bàn làm việc mỗi sáng tiết kiệm 30%",
      },
      {
        keyword: "gói nước ép detox giảm cân 7 ngày",
        intent: "Mua hàng (Commercial)",
        search_volume_est: "Rất cao",
        competition: "Cao",
        content_angle: "Thực đơn nước ép detox 7 ngày nhẹ bụng cho người ngồi nhiều",
      },
    ],
    gtm_roadmap: [
      {
        phase: "Phủ sóng 5 tòa nhà văn phòng thí điểm (Tháng 1)",
        timeline: "Tuần 1 - Tuần 4",
        key_actions: [
          "Tổ chức bàn Sampling dùng thử miễn phí tại sảnh các tòa nhà Landmark 81, Keangnam, Bitexco",
          "Tặng voucher giảm 50% cho đơn đặt gói tuần đầu tiên",
        ],
      },
      {
        phase: "Tự động hóa App / Web đặt hàng (Tháng 2 - 3)",
        timeline: "Tuần 5 - Tuần 12",
        key_actions: [
          "Tích hợp Zalo Mini App để nhân viên văn phòng order 1 chạm chỉ trong 5 giây",
          "Chương trình giới thiệu đồng nghiệp: Mời 1 bạn cùng đặt, cả 2 nhận 1 chai miễn phí",
        ],
      },
    ],
    graph_data: {
      nodes: [
        { id: "market", name: "Nước Ép Văn Phòng", category: "product", size: 24 },
        { id: "lumi", name: "Lumi Juice", category: "competitor", size: 16 },
        { id: "street", name: "Xe Ép Vỉa Hè", category: "competitor", size: 14 },
        { id: "office_worker", name: "Dân Công Sở", category: "segment", size: 18 },
        { id: "team_lead", name: "Admin / HR Cty", category: "segment", size: 14 },
        { id: "sub_pack", name: "Gói Tuần 199k", category: "price", size: 16 },
        { id: "temp_risk", name: "Rủi ro bảo quản lạnh", category: "risk", size: 13 },
      ],
      links: [
        { source: "market", target: "lumi", relationship: "COMPETES_WITH" },
        { source: "market", target: "street", relationship: "REPLACES" },
        { source: "market", target: "office_worker", relationship: "SERVES" },
        { source: "office_worker", target: "sub_pack", relationship: "HIGH_CONVERSION_ON" },
        { source: "market", target: "temp_risk", relationship: "MUST_SOLVE" },
      ],
    },
  },
};

export function generateDynamicMockReport(topic: string): MarketReport {
  const normalized = topic.toLowerCase();
  if (normalized.includes("mỹ phẩm") || normalized.includes("vegan") || normalized.includes("thuần chay")) {
    return { ...MOCK_REPORTS["my-pham-thuan-chay"], topic };
  }
  if (normalized.includes("nước ép") || normalized.includes("juice") || normalized.includes("đồ uống")) {
    return { ...MOCK_REPORTS["nuoc-ep-van-phong"], topic };
  }

  // Generic fallback report template
  return {
    id: "rep-" + Math.random().toString(36).substring(2, 7),
    topic: topic,
    createdAt: new Date().toLocaleString("vi-VN"),
    market_size_est: "Đang tăng trưởng mạnh (~1,200 - 3,500 Tỷ VNĐ)",
    growth_rate: "15% - 25% CAGR",
    executive_summary: `Thị trường '${topic}' tại Việt Nam và khu vực đang thể hiện tiềm năng tăng trưởng rõ rệt nhờ sự ứng dụng công nghệ và hành vi tiêu dùng chuyển dịch số. Để chiếm lĩnh thị phần, các doanh nghiệp mới gia nhập cần tập trung vào việc khác biệt hóa giải pháp, tối ưu hóa chi phí vận hành thông qua AI/Tự động hóa và xây dựng chiến lược Go-To-Market đa kênh.`,
    target_audience: [
      {
        title: "Khách Hàng Cá Nhân Tiên Phong (Early Adopters)",
        desc: "Nhóm khách hàng trẻ từ 20 - 35 tuổi, thích ứng nhanh với các giải pháp mới và sẵn sàng trả tiền cho sự tiện lợi.",
        pain_points: [
          "Quy trình truyền thống tốn quá nhiều thời gian",
          "Chất lượng dịch vụ/sản phẩm hiện tại không đồng đều",
        ],
      },
      {
        title: "Doanh Nghiệp & Đội Nhóm Vừa & Nhỏ (SMEs)",
        desc: "Cần giải pháp nhanh gọn, chi phí hợp lý để tăng năng suất cạnh tranh.",
        pain_points: [
          "Ngân sách đầu tư ban đầu hạn chế",
          "Thiếu nhân sự chuyên môn vận hành phức tạp",
        ],
      },
    ],
    market_gaps: [
      {
        title: "Giải pháp trọn gói tự động hóa & cá nhân hóa",
        opportunity: "Thị trường hiện tại còn nhiều giải pháp rời rạc, chưa có sản phẩm All-in-One trải nghiệm mượt mà.",
        priority: "Cao",
      },
      {
        title: "Mô hình định giá linh hoạt theo mức độ sử dụng",
        opportunity: "Khách hàng muốn dùng bao nhiêu trả bấy nhiêu (Pay-as-you-go) thay vì trả gói cước đắt đỏ.",
        priority: "Cao",
      },
    ],
    swot: {
      strengths: ["Mô hình tinh gọn, chi phí cố định thấp", "Khả năng ứng dụng công nghệ AI tạo đột phá"],
      weaknesses: ["Thương hiệu mới chưa có uy tín lâu năm", "Cần thời gian giáo dục thị trường"],
      opportunities: ["Xu hướng số hóa toàn diện", "Khoảng trống từ các đối thủ lớn phản ứng chậm"],
      threats: ["Đối thủ lớn sao chép tính năng", "Biến động kinh tế vĩ mô"],
    },
    competitors: [
      {
        name: "Top Player A (Thương hiệu truyền thống)",
        type: "Trực tiếp",
        positioning: "Thị phần lớn, uy tín lâu năm",
        strengths: ["Quy mô lớn", "Vốn mạnh", "Nhiều khách hàng trung thành"],
        weaknesses: ["Chậm đổi mới", "Giá cao", "Dịch vụ khách hàng cứng nhắc"],
        price_range: "Cao (Phân khúc Premium)",
        market_share_est: "40%",
      },
      {
        name: "Startup B (Thương hiệu công nghệ mới)",
        type: "Trực tiếp",
        positioning: "Giải pháp nhanh, giao diện hiện đại",
        strengths: ["UX thân thiện", "Marketing viral"],
        weaknesses: ["Hệ sinh thái chưa hoàn thiện", "Dễ gặp lỗi vận hành khi tăng trưởng nóng"],
        price_range: "Trung bình",
        market_share_est: "20%",
      },
    ],
    pricing: {
      min_market_price: 99000,
      median_market_price: 299000,
      recommended_price: 249000,
      premium_market_price: 799000,
      unit: "VNĐ / tháng hoặc gói",
      margin_est: "65% Gross Margin",
      pricing_logic: "Áp dụng chiến lược Penetration Pricing: Giá khởi điểm hấp dẫn để mở rộng tệp người dùng nhanh nhất, sau đó Upsell các tính năng nâng cao.",
      tiers: [
        {
          tier: "Cơ Bản (Starter)",
          price: 99000,
          description: "Dành cho người mới bắt đầu trải nghiệm",
          features: ["Tính năng cốt lõi", "Hỗ trợ qua email", "Giới hạn dung lượng cơ bản"],
        },
        {
          tier: "Chuyên Nghiệp (Pro - Khuyên dùng)",
          price: 249000,
          description: "Dành cho cá nhân & doanh nghiệp muốn tối ưu hiệu quả",
          features: ["Mở khóa toàn bộ tính năng cao cấp", "Hỗ trợ 24/7 ưu tiên", "Báo cáo phân tích chuyên sâu"],
        },
        {
          tier: "Doanh Nghiệp (Enterprise)",
          price: 799000,
          description: "Tùy biến theo quy mô lớn",
          features: ["API tích hợp riêng", "Quản lý đa tài khoản", "Cam kết SLA 99.9%"],
        },
      ],
    },
    risks: [
      {
        category: "Đối thủ",
        risk_title: "Cạnh tranh về giá từ các đối thủ lớn",
        risk_level: "Cao",
        impact: "Giảm tốc độ thu hút khách hàng mới nếu không có USP rõ rệt.",
        mitigation: "Tập trung nâng cao trải nghiệm khách hàng xuất sắc và xây dựng tính năng độc quyền không thể sao chép dễ dàng.",
      },
      {
        category: "Vận hành",
        risk_title: "Rủi ro mở rộng quy mô (Scalability)",
        risk_level: "Trung bình",
        impact: "Quá tải hệ thống khi lượng người dùng tăng đột biến.",
        mitigation: "Sử dụng hạ tầng Cloud Serverless tự động co giãn và bộ đệm Redis tối ưu.",
      },
    ],
    seo_strategy: [
      {
        keyword: `giải pháp ${topic} hiệu quả`,
        intent: "Tìm hiểu (Informational)",
        search_volume_est: "Cao",
        competition: "Trung bình",
        content_angle: `Hướng dẫn A-Z cách chọn và áp dụng ${topic} tối ưu chi phí`,
      },
      {
        keyword: `bảng giá ${topic} tốt nhất 2026`,
        intent: "Mua hàng (Commercial)",
        search_volume_est: "Cao",
        competition: "Thấp",
        content_angle: `So sánh chi tiết giá và chất lượng các bên cung cấp ${topic}`,
      },
    ],
    gtm_roadmap: [
      {
        phase: "Giai đoạn 1: Ra mắt phiên bản MVP & Thu thập Feedback (Tháng 1)",
        timeline: "Tháng 1",
        key_actions: ["Triển khai với 50 khách hàng đầu tiên", "Đo lường chỉ số NPS & tỷ lệ giữ chân"],
      },
      {
        phase: "Giai đoạn 2: Tăng tốc Marketing & Bán hàng (Tháng 2 - 3)",
        timeline: "Tháng 2 - 3",
        key_actions: ["Chạy Performance Ads & SEO Content", "Hợp tác đối tác phân phối liên kết"],
      },
    ],
    graph_data: {
      nodes: [
        { id: "market", name: topic, category: "product", size: 24 },
        { id: "comp1", name: "Đối Thủ A", category: "competitor", size: 16 },
        { id: "comp2", name: "Đối Thủ B", category: "competitor", size: 15 },
        { id: "user_seg", name: "Khách Hàng Mục Tiêu", category: "segment", size: 18 },
        { id: "price_rec", name: "Giá Đề Xuất", category: "price", size: 15 },
        { id: "gap_main", name: "Khoảng Trống Thị Trường", category: "keyword", size: 15 },
      ],
      links: [
        { source: "market", target: "comp1", relationship: "COMPETES_WITH" },
        { source: "market", target: "comp2", relationship: "COMPETES_WITH" },
        { source: "market", target: "user_seg", relationship: "TARGETS" },
        { source: "market", target: "price_rec", relationship: "PRICED_AT" },
        { source: "market", target: "gap_main", relationship: "EXPLOITS" },
      ],
    },
  };
}
