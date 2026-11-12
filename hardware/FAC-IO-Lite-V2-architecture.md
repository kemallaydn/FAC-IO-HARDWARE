# FAC-IO Lite V2 — sade kart taslağı

Durum: **Yeni tasarım yönü / üretime hazır değil.** V1 dosyaları korunur.

## Amaç

Robotistan’a Gerber + BOM + Pick & Place verip, ESP32 ve Ethernet’i üzerinde bulunan, iki ayrı kuru-kontak bariyer komut rölesiyle birlikte dizilmiş tek kart almak. Kart sadece Hikvision kontrol kartının etiketli OPEN/CLOSE düşük gerilim komut girişlerini kapatır; motor veya şebeke bağlantısı yoktur.

## Seçilen sade mimari

- **U1: WT32-ETH01**; ESP32, Ethernet PHY, magnetics ve RJ45 aynı hazır modülde. Mevcut ESP32-C3 + WIZ850io + iki host soketinin yerine geçer.
- İlk sade güç seçimi **3.3 V doğrudan besleme**; üretici 3.3 V ve 5 V seçeneklerinden yalnız birinin kullanılmasını, en az 500 mA besleme kapasitesini belirtiyor. Bu, 12 V → 3.3 V `AP63203WU-7` buck adayını koruyup ayrı 5 V hattı ve regulator değişikliğini önleyebilir. 3.3 V rail gerçek yükte, 12 V giriş köşelerinde ve termalde yeterli olduğu hesaplanıp ölçülmeden seçilmiş BOM sayılmaz.
- 12 V girişinde sigorta, ters kutup koruması ve TVS; iki 12 V röle bobini korunmalı flyback diyotlarıyla sürülür.
- İki bağımsız NO/COM/NC çıkış için mevcut Omron G6K-2P-Y DC12 sinyal röleleri korunur; her rölenin bir DPDT kutbu kullanılır.
- **Güncel V2 şema durumu:** Tek CD74HC221 iki bağımsız, yeniden tetiklenmeyen darbe üretiyor. Bu parça/RC ağı nominal adaydır; mutlak zaman toleransı üretici veri sayfasında sınırlanmadığı için üretim kapısı fiziksel pulse testi ve bariyerin komut girişine uygunluk ölçümüdür.
- Tetik GPIO adayları WT32 IO32 ve IO33; açılışta rölelerin kapalı kalması için tetik pull-down ve MOSFET gate pull-down. Programlama için EN, IO0, TXD, RXD, 3V3 ve GND erişimli header; USB-UART köprüsü karttan çıkarılır.
- WT32 şema sembolü fiziksel 26-pad aday sırasını kullanır: debug pad 1–3, ana arayüz pad 4–23, debug pad 24–26. OPEN/CLOSE tetikleri aday pad 5/6, programlama sinyalleri pad 24/25/26'dır. Bu pad sırası üreticinin ayrı arayüz tabloları ile topluluk KiCad footprint'inden eşlenmiştir; üretici ölçülü land-pattern vermediği için numune/revizyon ölçümü olmadan PCB Gerberi üretim için onaylanmayacak.
- İki katmanlı taşıyıcı kart. PoE, Wi-Fi işlevi, USB-UART, W5500, ESP32-C3, durum LED'leri ve geniş kullanıcı arayüzü V2'de yok.

## Tedarik ve üretim gerçekleri

- 2026-11-10 canlı tedarik kontrolünde Robotistan WT32-ETH01 ürünü listeliyor ama stok durumu satışa hazır değil; LCSC C477837 kaydı da **0 stok** gösteriyor. Görsü Elektronik ürün sayfası 404,51 TL + KDV ve **stokta var** gösteriyor. Dolayısıyla modül Türkiye'den alınabilir görünüyor ama Robotistan'ın kendi tedarikinden garanti edilemiyor; müşteri tedarikli modülün PCBA'ya kabulü ve bu modülü montajlı geri gönderme yöntemi yazılı olarak netleşmeden bu V2 Robotistan montaj siparişi kabul edilemez. Kaynaklar: [Robotistan WT32-ETH01](https://www.robotistan.com/wt32-eth01-ethernet-modul), [Görsü WT32-ETH01](https://gorsuelektronik.com/wt32-eth01-esp32-tabanli-serial-to-ethernet-modul), [LCSC C477837](https://www.lcsc.com/product-image/C477837.html).
- Robotistan PCBA için mevcut stok yok; numune tedariği için Görsü Elektronik ürünü 404,51 TL + KDV stokta gösteriyor. Bu tekil sayfa stok adedini veya Robotistan'ın müşteri tedarikli THT WT32 modülünü dizme kabulünü ispatlamaz. Her ikisi numune/teklif aşamasında doğrulanmalı.
- Üretici veri sayfası modülün 5 V veya 3.3 V'tan yalnız biriyle beslenmesini, en az 500 mA kaynak kapasitesini, pin işlevlerini ve yarım pad/THT bağlantı seçeneğini doğruluyor. Veri sayfasında üretime esas ölçülü land pattern yok; satıcı/üçüncü taraf 60 × 26 mm gövde ölçüsü, pad delik aralığını doğrulamıyor. Kart footprint'i ve RJ45 kenar açıklığı gerçek modül numunesiyle ölçülmeden Gerber üretim onayı yok. Kaynak: [WT32-ETH01 üretici veri sayfası](https://www.mouser.com/datasheet/2/744/WT32_ETH01_datasheet_V1_1__en-2487862.pdf).
- Ön fiyat karşılaştırmasında WT32-ETH01 Seeed'de 19,90 USD; mevcut iki ağ modülü LCSC'de ESP32-C3-WROOM-02-N4 3,3169 USD + WIZ850io 22,8926 USD. Fiyatlar farklı tedarik/vergileri kapsamaz; yön gösterir. WT32 stok/tedarik ve dizgi kabulü kesinleşmeden maliyet tasarrufu gerçekleşmiş sayılmaz.
- Ek yerel karşılaştırma (2026-11-10): Robotistan'da W5500 USR-ES1 modülü 348,49 TL KDV dahil; ESP32-C3 Mini sayfası 189,01 TL KDV dahil ama stokta yok. Bu iki parçanın görünen ara toplamı 537,50 TL; buna taşıyıcı üzerindeki soket/montaj dahil değil. Görsü'de WT32 404,51 TL + KDV (yaklaşık 485,41 TL KDV dahil) görünüyor. Bu yaklaşık 52,09 TL / %9,7 parça fiyatı avantajı yönünde; farklı satıcı, stok ve dizgi koşulları nedeniyle kesin üretim maliyet farkı değildir. WT32 ayrıca RJ45+magnetics'i ve harici ethernet modül soketlerini tek kartta toplar. Kaynaklar: [Robotistan W5500](https://www.robotistan.com/spidan-ethernettcpip-donusturucu-w5500-usr-es1), [Robotistan ESP32-C3 Mini](https://www.robotistan.com/esp32-c3-mini-wifi-bluetooth-modul), [Görsü WT32](https://gorsuelektronik.com/wt32-eth01-esp32-tabanli-serial-to-ethernet-modul).

## Üretim kapıları

1. WT32 gerçek modül numunesiyle 20-pin ana arayüz + ayrı 6-pin debug arayüzü, pad aralığı / RJ45 mekanik yönü ve yükseklik ölçümü; datasheet fiziksel land-pattern vermiyor.
2. Buck regülatör 12 V giriş köşeleri, 3.3 V rail'in en az 500 mA kaynak kapasitesi, röle eşzamanlı yük ve termal hesabı.
3. CD74HC221 giriş/reset/power-up davranışı, 3.3 V K faktörü ve MLCC bias/tolerans hesabı; OPEN/CLOSE pulse sınırının osiloskopla doğrulanması.
4. Kuru kontak izolasyonu, akım yolu, röle kontağı ve tam montaj mekanik kontrolü.
5. KiCad şematik/PCB: ERC, DRC, schematic parity, netlist, Gerber/CAM; Robotistan BOM/PnP referans ve miktar eşleşmesi; assembler WT32 kabulü ve fiyat yazılı doğrulaması.
6. İlk numune güç, reset, brownout, Ethernet/DHCP, firmware yükleme, iki röle, maksimum pulse ve bariyer giriş testi.

Bu taslak üretim onayı, doğrulanmış BOM veya Gerber değildir.
