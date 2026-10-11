# ✦ Gemini Usage & Quota Tracker (Windows Top Menu Bar)

Windows için özel olarak tasarlanmış, **Google Gemini'nin 5 saatlik yuvarlanan kullanım kotasını (rolling compute limit)** ve sıfırlanma sayacını ekranın en üstünde modern bir **"Dynamic Island / Top Bar"** şeklinde sürekli ve canlı olarak gösteren masaüstü durum çubuğu uygulaması.

---

## 🌟 Öne Çıkan Özellikler

1. **Sürekli Güncel 5 Saatlik Limit Takibi:**
   - 5 saatlik kalan limit yüzdesi (`%85 Kalan` veya `%15 Kullanıldı`).
   - Canlı saniyelik sıfırlanma sayacı (`⏳ 03:42:15` geri sayım).
   - Tam dolum saati (`Sıfırlanma: 15:30:00`).
   - Haftalık toplam kota takibi.

2. **Dinamik Renk Kodlu İlerleme Çubuğu:**
   - 🟢 **Yeşil (> %50):** Kotanız bol ve rahatça kullanabilirsiniz.
   - 🟡 **Turuncu (%20 - %50):** Orta seviye kota.
   - 🔴 **Kırmızı (< %20):** Kritik düşük limit seviyesi (yoğun işlemlerde kısıtlama gelebilir).

3. **Modern Windows 11 Fluent Tasarım (Dynamic Island):**
   - Yarı saydam koyu cam efekti (Glassmorphism), yuvarlatılmış köşeler ve yumuşak gölgeler.
   - **Her Zaman Üstte (Always on Top):** Kod yazarken, tarayıcıda veya başka bir uygulamadayken tek bakışta görünür.
   - **Sürüklenebilir:** Çubuğu farenizle tutup ekranın istediğiniz yerine taşıyabilirsiniz. Çift tıklama ile ortalayabilir veya detay panelini açabilirsiniz.
   - **Sistem Tepsisi (Tray) Entegrasyonu:** Görev çubuğunun sağ altındaki sistem tepsisinde sürekli çalışır, sağ tıklama menüsüyle kolayca kontrol edilir.

4. **Çift Yönlü Canlı Otomatik Senkronizasyon:**
   - **Yöntem A - Chrome/Edge Eklentisi:** `gemini.google.com` üzerinde sohbet ettiğinizde arka planda limitinizi otomatik okur ve yerel masaüstü çubuğuna saniyesinde aktarır.
   - **Yöntem B - Tampermonkey Userscript:** Eklenti kurmak istemeyenler için tek dosyalık userscript alternatifi.
   - **Yöntem C - Manuel / Akıllı Simülasyon:** Tarayıcı açık olmasa bile 5 saatlik zaman penceresini geri sayarak simüle eder; `+1 Normal Soru`, `+1 Kod/Pro` veya manuel yüzde belirleme butonlarıyla kotanızı ayarlayabilirsiniz.

5. **Düşük Limit & Sıfırlanma Bildirimleri:**
   - Limit %20'nin altına indiğinde Windows Bildirimi ve sesli uyarı.
   - 5 saatlik süre tamamlanıp kotanız %100'e ulaştığında "Kotanız Yenilendi!" bildirimi.

---

## 🚀 Hızlı Başlangıç

### 1. Çalıştırma
Uygulamayı başlatmak için klasördeki:
- `run.bat` dosyasına çift tıklayın (Konsol penceresi olmadan arka planda sessizce başlar).
- veya konsol çıktılarını görmek isterseniz `run_debug.bat` çalıştırabilirsiniz.

### 2. İsteğe Bağlı: Tek Tıkla EXE Oluşturma
PyInstaller ile harici Python kurulumuna ihtiyaç duymayan bağımsız bir `GeminiUsageTracker.exe` oluşturmak isterseniz:
- `compile_exe.bat` dosyasına çift tıklayın.

---

## 🔌 Tarayıcı ile Otomatik Eşitleme (Auto-Sync)

### A. Chrome / Edge Eklentisi ile Kurulum (2 Dakika)
1. Üst menü çubuğundaki `▾` (veya sağ tık > Detaylı Panel) butonuna basarak açılan pencereden **"Otomatik Senkron"** sekmesine gelin.
2. **"📂 Eklenti Klasörünü Aç"** butonuna tıklayın (klasör yolu: `extension/`).
3. Google Chrome veya Microsoft Edge tarayıcınızda adres çubuğuna `chrome://extensions` (veya `edge://extensions`) yazıp Enter'a basın.
4. Sağ üstteki **"Geliştirici Modu" (Developer Mode)** anahtarını açın.
5. Sol üstte beliren **"Paketlenmemiş öge yükle" (Load unpacked)** butonuna tıklayın ve açılan `extension` klasörünü seçin.
6. Artık `gemini.google.com` sitesine her girdiğinizde veya mesaj gönderdiğinizde limitleriniz otomatik olarak masaüstü çubuğunuza yansıyacaktır!

### B. Tampermonkey / Violentmonkey ile Kurulum
Eğer Tampermonkey eklentiniz varsa:
1. `userscript/gemini_usage_sync.user.js` dosyasını Tampermonkey paneline yeni script olarak ekleyin.
2. Sayfayı yenilediğinizde senkronizasyon otomatik olarak devreye girer.

---

## 🎛️ Kullanım Kısayolları ve Kontroller

| Eylem | Nasıl Yapılır? |
| :--- | :--- |
| **Detaylı Paneli Aç / Kapat** | Çubuğun üzerindeki `▾` butonuna basın veya çubuğa **çift tıklayın**. |
| **Çubuğu Taşıma** | Çubuğu sol tıkla basılı tutup ekranın istediğiniz yerine sürükleyin. |
| **Ekranın Üst Ortasına Hizalama** | Çubuğa sağ tıklayıp **"Ekranın Üst Ortasına Hizala"** seçin. |
| **Her Zaman Üstte Tutma** | Çubuktaki `📌` simgesine tıklayın veya sağ tık menüsünden seçin. |
| **Gizle / Sistem Tepsisine Küçült** | Çubuktaki `✕` butonuna tıklayın. Sağ alttaki sistem tepsisindeki Gemini simgesine tıklayarak tekrar açabilirsiniz. |
| **Manuel Kota Ayarı** | Detay panelindeki "Hızlı İstek Simülasyonu" veya "Manuel Ayar" alanını kullanın. |

---

## 🛠️ Teknik Altyapı
- **Arayüz:** Python 3.12 + PyQt6 (High-DPI aware, Windows 11 Acrylic styling, Hardware accelerated drop shadows).
- **Yerel Köprü:** `127.0.0.1:38281` üzerinde çalışan ultra-hafif asenkron HTTP API.
- **Güvenlik & Gizlilik:** Tüm işlemler tamamen bilgisayarınızda yerel olarak çalışır, hiçbir kimlik bilgisi, çerez veya sohbet metni harici sunuculara iletilmez.
