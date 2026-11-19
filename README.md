# GTA 6 — "What If You Were Born as Lucia?"

Born in Lore formatında, tamamen kodla çizilen ve kurgulanan animasyon video. Seslendirme İngilizce; Türkçe ve Almanca ses kanalları YouTube'a ayrıca yükleniyor.

## 1. Kanal analizi: @borninlore

Analiz tarihi: 19 Kasım 2026. Kanalda 15,1 bin abone ve 7 video vardı; hepsi son 3 haftada yüklenmişti.

| Video | Süre | İzlenme |
|---|---|---|
| What If You Were Born as Kratos? \| God of War | 8:06 | 962K |
| What If You Were Born as CJ? \| GTA San Andreas | 11:14 | 832K |
| What If You Were Born as Master Chief? \| Halo | 12:55 | 409K |
| What If You Were Born as Ghost? \| Call of Duty | 13:18 | 323K |
| What If You Were Born as Arthur Morgan? \| RDR2 | 9:18 | 281K |
| What If You Were Born as Ezio Auditore? \| Assassin's Creed | 11:50 | 204K |
| What If You Were Born as Geralt of Rivia? \| The Witcher | 6:52 | 18K |

En iyi iki video Kratos ve CJ. CJ'nin GTA videosu olması, GTA kitlesinin bu formatı tuttuğunu gösteriyor.

### Formül
Her video aynı döngüyü izliyor. Bizim videomuz da bu döngüye göre kuruldu.

1. **Hook (~10 sn):** "If you were born as X, you'd [şok edici olay]. Then [olay]. And [twist]."
2. **Doğum:** "But right now? You're a baby in [yer]. No X. No Y. Not even Z."
3. **Yaş ilerlemesi:** Sahneler AGE 0 → 2 → 7 → 12 → 16 diye ilerliyor. "Years pass, and the cute kid? Gone."
4. **Callback'ler:** "Remember that." diye bir detay kuruluyor, sonradan karşılığı veriliyor. Bizde bu anlar sarı **REMEMBER THIS** etiketi ve "ding" sesiyle işaretleniyor.
5. **Bölümler:** Prologue + I–IX arası Roma rakamlı bölümler. Açıklamaya zaman damgaları ekleniyor.
6. **Videonun ortasında CTA:** "Quick pause… Who's next? Drop a name. The most liked one gets born next."
7. **Kapanış:** "Not bad for a kid who…", ardından hayatın kısa özeti ve "So, tell me. Would you…?"
8. **Anlatım dili:** 2. tekil şahıs, şimdiki zaman, çok kısa cümleler, kuru mizah.
9. **Thumbnail:** Çapraz bölünmüş iki panel. Solda "AGE 0" yazısı ve kızgın, damarlı chibi bebek; sağda karakterin dramatik yetişkin hali ve 2 kelimelik etiket ("BETRAYED", "GOD KILLER"…).

`docs/reference_thumbnails.jpg` dosyasında kanalın 7 thumbnail'i yan yana duruyor.

## 2. Bizim video

- **Konu:** Lucia Caminos (GTA 6). Oyun 19 Kasım 2026'da çıktı ve Metacritic'te 99 aldı. Arama hacmi şu an zirvede.
- **Kaynak:** Rockstar'ın resmi karakter biyografileri ile Trailer 1 ve 2'deki diyaloglar (altyazılardan alındı). Rockstar'ın açıklamadığı kısımlarda olay uydurulmadı; anlatıcı bunu açıkça söylüyor ("Rockstar never tells us exactly what happened").
- **Yapı:** 9 bölüm ve 38 sahne. Senaryo `project/script_data.py` içinde; EN, TR ve DE metinleri aynı dosyada.

## 3. Üretim hattı (tamamen kod)

| Dosya | Görev |
|---|---|
| `project/characters.py` | Tek chibi karakter rigi. Lucia'nın 7 yaş hâli, Jason (3 hâl), anne, baba ve yan karakterler. IK kollar, göz kırpma, nefes, konuşma ağzı, ifadeler |
| `project/scenes_bg.py`, `scenes.py` | Arka planlar, objeler ve 38 sahnenin animasyonu. Olaylar anlatıcının kelime zaman damgasına bağlı |
| `project/timeline.py` | Ortak zaman çizelgesi. Sahne süresi en uzun dile göre ayarlanıyor; TR/DE gerekirse en fazla %12 hızlandırılıyor, böylece 3 dil de aynı videoya oturuyor |
| `project/render.py` | 1080p30 render, 4 paralel parça |
| `project/audio.py` | Prosedürel synthwave müzik, SFX (pop/whoosh/impact/ding), konuşmada otomatik müzik kısma (ducking), SRT altyazı |
| `project/tts.py` | ElevenLabs seslendirmesi (zaman damgalı) |
| `project/thumbnail.py` | EN/TR/DE thumbnail |
| `project/finalize.py`, `build_meta.py` | Yüklemeye hazır dosyalar; başlık, açıklama (bölümlü) ve etiketler |

Tek komut: `./make_video.sh` (pilot için: `UNTIL=c1a ./make_video.sh en`)

## 4. Durum

- ✅ Kanal analizi, senaryo (EN/TR/DE), karakterler, 38 sahnenin hepsi, müzik/SFX, altyazı ve thumbnail hazır.
- ✅ `output/GTA6_Lucia_PILOT_EN.mp4`: Prolog'un tamamı (~1 dk). Gerçek seslendirme, müzik ve efektlerle bitmiş kalite.
- ⏳ **Kalan:** ElevenLabs kotası doldu. Bu hesaptaki ücretsiz planın 10.000 kredisi bitti; tam video için ~11.600 kredi daha gerekiyor. Kredi açılınca `./make_video.sh` kalan sesleri üretir, tüm videoyu render eder ve `output/` klasörüne yazar. Bu iş yaklaşık 10 dakika sürer.
- Not: ElevenLabs'ın ücretsiz planı ticari kullanıma izin vermiyor. Para kazanılan bir kanal için en az Starter planı gerekir.

## 5. YouTube'a yükleme

1. `GTA6_Lucia_EN.mp4` dosyasını yükle (ana dil: English). Başlık, açıklama ve etiketler `youtube_en.txt` dosyasında.
2. Studio → **Languages** → Turkish / German → **Add audio track**: `audio_TR.m4a`, `audio_DE.m4a`
3. Aynı ekranda başlık ve açıklama çevirileri: `youtube_tr.txt`, `youtube_de.txt`
4. Altyazılar: `subtitles_en.srt`, `subtitles_tr.srt`, `subtitles_de.srt`
5. Thumbnail: `thumbnail_en.jpg`
