# 🏀 NBA Maç Tahmin Uygulaması

Bu uygulama, NBA takımlarının maç sonuçlarını tahmin etmek için ağırlıklı ortalama hesaplaması yapan bir web uygulamasıdır.

## 🌟 Özellikler

- İki takım arasındaki maç için tahmin yapma
- Ev sahibi ve deplasman takımları için ayrı hesaplamalar
- Görsel grafikler ile sonuçları gösterme
- Detaylı istatistikler ve metrikler

## 📋 Gereksinimler

Uygulamayı çalıştırmak için aşağıdaki gereksinimlere ihtiyacınız vardır:

- Python 3.8 veya üzeri
- Streamlit
- Pandas
- Plotly

## 🚀 Kurulum

1. Projeyi klonlayın:
```bash
git clone [repo-url]
cd [proje-dizini]
```

2. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

3. Uygulamayı çalıştırın:
```bash
streamlit run app.py
```

## 💻 Kullanım

1. Uygulamayı başlattıktan sonra web tarayıcınızda otomatik olarak açılacaktır
2. Ev sahibi takımın kısaltmasını girin (örn: LAL)
3. Deplasman takımının kısaltmasını girin (örn: BOS)
4. "Tahmin Et" butonuna tıklayın
5. Sonuçları görsel grafikler ve metrikler ile inceleyin

## 📊 Veri Formatı

Uygulama, her takım için aşağıdaki formatta CSV dosyaları bekler:
- Dosya adı: `[TAKIM_KISALTMASI]_2024_games.csv`
- Gerekli sütunlar: Tm (Takım sayısı), Opp (Rakip sayısı), homeaway (Ev/Deplasman durumu)

## 🤝 Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik: Açıklama'`)
4. Branch'inizi push edin (`git push origin feature/yeniOzellik`)
5. Pull Request oluşturun

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın. 