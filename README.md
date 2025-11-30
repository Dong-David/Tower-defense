# QUÁ TRÌNH HÌNH THÀNH VÀ PHÁT TRIỂN GAME “TOWER AI DEFENSE”

## 1. Ý TƯỞNG BAN ĐẦU
Mục tiêu: Xây dựng một game mô phỏng dạng **Tower Defense** có khả năng **AI điều khiển**, nơi người chơi hoặc hệ thống có thể bố trí, tấn công và phòng thủ theo chiến thuật.  

Lý do: Thử nghiệm khả năng quản lý tác nhân thông minh (AI Manager), xử lý va chạm không gian (Spatial System), và hiển thị đa đối tượng (Renderer) bằng Python + Pygame.  

Nền tảng chọn: `Pygame` để xử lý khung hình, âm thanh và sự kiện; sử dụng OOP nhằm tách biệt logic của từng thành phần (Enemy, Tower, Soldier, AI).

---

## 2. PHÁC THẢO CẤU TRÚC
Chương trình chia thành **nhiều module nhỏ**, mỗi file đại diện cho một vai trò riêng:

- `AIManager.py`: điều phối chiến thuật của quân đội và tháp.  
- `Soldier.py`: định nghĩa hành vi lính (di chuyển, tấn công, chết...).  
- `Enemy.py`: quản lý kẻ địch (HP, sát thương, hướng đi...).  
- `Tower.py`: đại diện các tháp phòng thủ (bắn đạn, tầm nhìn, mục tiêu).  
- `Spatial.py`: hệ thống không gian (chia ô, tối ưu tìm kiếm đối tượng gần).  
- `Renderer.py`: hiển thị toàn cảnh, sprite, animation.  
- `Audio.py`: xử lý hiệu ứng âm thanh, load và phát tiếng.  
- `config.py`: chứa hằng số cấu hình (FPS, màu sắc, tốc độ...).  
- `main.py`: vòng lặp chính — nơi tất cả các module kết hợp.

**Luồng vận hành cơ bản:**
1. Khởi tạo toàn bộ hệ thống (AI, Renderer, Audio...).
2. Sinh bản đồ và các thực thể (Tower, Enemy, Soldier).
3. Vòng lặp game cập nhật vị trí, xử lý va chạm, kiểm tra tấn công.
4. Renderer vẽ toàn bộ khung hình.
5. Kết thúc khi toàn bộ quân hoặc tháp bị tiêu diệt.

---

## 3. QUẢN LÝ TÁC NHÂN (AI MANAGER)
**Vai trò:** Trung tâm điều phối chiến thuật – xác định khi nào tấn công, khi nào rút lui, spawn thêm lính, hoặc chọn mục tiêu.

**Các chức năng chính:**
- `update()`: cập nhật chiến lược mỗi khung hình.  
- `assign_targets()`: phân phối kẻ địch cho từng Soldier hoặc Tower.  
- `spawn_units()`: tạo thêm lính hoặc địch mới khi cần.  

**Tư duy thiết kế:** Hệ AI này không cần thông minh phức tạp, mà mang tính mô phỏng “hành vi chiến thuật” – giúp game có tính sống động và phản ứng.

---

## 4. HỆ THỐNG NHÂN VẬT (SOLDIER & ENEMY)
### Soldier.py
Mỗi Soldier có thuộc tính:
- Vị trí, tốc độ, hướng, HP.  
- Trạng thái: “di chuyển”, “tấn công”, “chết”.  
- Có hàm `update()` và `draw()` riêng.  
- Khi gặp Enemy → gọi `attack()` hoặc `take_damage()`.  

### Enemy.py
- Tương tự Soldier nhưng di chuyển theo hướng ngược lại (hướng tới khu phòng thủ).  
- Có hệ thống máu, tốc độ sinh ra và phạm vi di chuyển ngẫu nhiên để tạo cảm giác “sóng tấn công”.  
- Khi chết có thể kích hoạt hiệu ứng nổ hoặc âm thanh qua `Audio`.

---

## 5. TOWER – HỆ PHÒNG THỦ
**Class `Tower` chịu trách nhiệm:**
- Xác định phạm vi tấn công.  
- Tìm kẻ địch gần nhất (`get_nearest_enemy()`).  
- Gọi `shoot()` → bắn đạn hoặc hiệu ứng tấn công.  

Mỗi Tower có thể nâng cấp hoặc thay đổi sát thương.  
**Tư duy thiết kế:** Đơn giản nhưng có thể mở rộng, dễ gắn thêm loại Tower khác (ví dụ: “Sniper”, “AOE”, “Slow”).

---

## 6. SPATIAL SYSTEM – QUẢN LÝ KHÔNG GIAN
File `Spatial.py` cài đặt **phân vùng không gian (spatial hashing)**:
- Chia map thành các ô (grid) để giảm chi phí kiểm tra va chạm.  
- Các thực thể (Soldier, Enemy, Tower) được thêm vào lưới.  
- Khi cần tìm mục tiêu gần → chỉ duyệt trong ô lân cận thay vì toàn bộ map.  
- Kết hợp với AI để chọn mục tiêu tối ưu.

---

## 7. RENDERER – HIỂN THỊ
`Renderer.py` phụ trách:
- Vẽ background, sprite nhân vật, tháp, hiệu ứng đạn, HP bar.  
- Quản lý thứ tự vẽ theo lớp (layering).  
- Có thể zoom hoặc di chuyển camera (nếu cấu hình cho phép).  
- Được gọi mỗi frame từ vòng lặp chính trong `main.py`.

---

## 8. ÂM THANH – AUDIO MANAGER
`Audio.py` load các file âm thanh (`attack.wav`, `explode.wav`, `bgm.mp3`, ...).  
Cung cấp hàm:
- `play_bgm()`: bật nhạc nền.  
- `play_effect(name)`: phát hiệu ứng tương ứng với hành động.  
Sử dụng thư viện `pygame.mixer`.

---

## 9. MAIN LOOP – TRÁI TIM CỦA GAME
`main.py` là **bộ điều phối trung tâm**:
1. Gọi `init()` → khởi tạo cấu hình, tạo các đối tượng.  
2. Bắt đầu vòng lặp chính:
   - Nhận sự kiện từ bàn phím / chuột.  
   - Cập nhật AI, Tower, Enemy, Soldier, Spatial.  
   - Renderer vẽ lại toàn cảnh.  
   - Giữ FPS ổn định bằng `pygame.time.Clock()`.  
3. Khi thắng hoặc thua → in thông báo, chờ người chơi restart.

---

## 10. CẢM NHẬN & HƯỚNG PHÁT TRIỂN
**Điểm mạnh:**
- Kiến trúc module rõ ràng, dễ mở rộng.  
- Spatial system giúp tăng hiệu năng đáng kể.  
- Renderer và Audio tách riêng giúp dễ thêm hiệu ứng.  

**Điểm có thể cải thiện:**
- AI có thể được huấn luyện bằng học tăng cường (Reinforcement Learning).  
- Cần thêm UI hiển thị máu, tiền, số lượt địch.  
- Có thể thêm nhiều loại địch và tháp với kỹ năng riêng.  

**Trải nghiệm:** Game vận hành ổn định, dễ tùy chỉnh chiến thuật, cho cảm giác “sandbox defense” rất tự nhiên.
