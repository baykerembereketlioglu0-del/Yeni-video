# -*- coding: utf-8 -*-
"""YouTube title / description (with chapter timestamps from the real timeline) / tags, per language."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from timeline import build, ROOT
from script_data import TITLE

CH_NAMES = {
    "en": ["Prologue: Born Swinging", "I · The Good Life", "II · Fighting for Family", "III · Bad Luck",
           "IV · Sheer Luck", "V · The Guy at the Gate", "VI · Trust", "VII · Vice City", "VIII · Day One"],
    "tr": ["Prolog: Doğuştan Dövüşçü", "I · Güzel Hayat", "II · Aile İçin Kavga", "III · Şanssızlık",
           "IV · Saf Şans", "V · Kapıdaki Adam", "VI · Güven", "VII · Vice City", "VIII · İlk Gün"],
    "de": ["Prolog: Kämpferin von Geburt", "I · Das gute Leben", "II · Kampf für die Familie", "III · Pech",
           "IV · Pures Glück", "V · Der Typ am Tor", "VI · Vertrauen", "VII · Vice City", "VIII · Tag eins"],
}

DESC = {
    "en": """You're a baby in Liberty City. Years later, you're locked up in the Leonida Penitentiary for fighting for your family. Then pure luck gets you out, and a guy named Jason is waiting at the gate. This is the whole life of Lucia Caminos, from a kid who was born swinging to day one of GTA 6, told as if it were yours.

Liberty City, the gloves, Vice City, the penitentiary, "bad luck, I guess", Jason, Brian, a cheap motel, and one word: trust.

Would you trust Jason? And which GTA 6 character should be born next? Tell me in the comments.

{chapters}

Based on what Rockstar revealed before launch: the official character bios and Trailers 1 & 2. Rockstar hasn't told us everything yet, so the gaps are filled with animation, not invented facts.
Fan-made animation. Not affiliated with or endorsed by Rockstar Games or Take-Two Interactive.""",
    "tr": """Liberty City'de bir bebeksin. Yıllar sonra, ailen için kavga ettiğin için Leonida Cezaevi'ndesin. Sonra saf bir şans seni dışarı çıkarıyor ve kapıda Jason adında bir adam bekliyor. Bu, doğuştan dövüşçü bir çocuktan GTA 6'nın ilk gününe kadar Lucia Caminos'un tüm hayatı; sanki senin hayatınmış gibi.

Liberty City, boks eldivenleri, Vice City, cezaevi, "şanssızlık herhalde", Jason, Brian, ucuz bir motel ve tek bir kelime: güven.

Jason'a güvenir miydin? Sırada hangi GTA 6 karakteri doğsun? Yorumlarda yaz.

{chapters}

Rockstar'ın çıkıştan önce paylaştıklarına dayanır: resmi karakter biyografileri ve 1. ve 2. fragman. Rockstar her şeyi anlatmadı; boşluklar uydurma bilgilerle değil, animasyonla dolduruldu.
Hayran yapımı animasyondur. Rockstar Games veya Take-Two Interactive ile bağlantılı değildir.""",
    "de": """Du bist ein Baby in Liberty City. Jahre später sitzt du im Leonida-Gefängnis, weil du für deine Familie gekämpft hast. Dann holt dich pures Glück raus, und am Tor wartet ein Typ namens Jason. Das ist das ganze Leben von Lucia Caminos, vom Kind, das schon kämpfend auf die Welt kam, bis zum ersten Tag von GTA 6, erzählt, als wäre es deins.

Liberty City, die Boxhandschuhe, Vice City, das Gefängnis, „Pech, schätze ich", Jason, Brian, ein billiges Motel und ein Wort: Vertrauen.

Würdest du Jason vertrauen? Und welcher GTA-6-Charakter soll als Nächstes geboren werden? Schreib es in die Kommentare.

{chapters}

Basiert auf dem, was Rockstar vor dem Release gezeigt hat: die offiziellen Charakter-Bios und Trailer 1 & 2. Rockstar hat noch nicht alles verraten, die Lücken füllt die Animation, nicht erfundene Fakten.
Fan-Animation. Nicht mit Rockstar Games oder Take-Two Interactive verbunden.""",
}

TAGS = {
    "en": "GTA 6, GTA VI, Lucia, Lucia Caminos, Jason Duval, GTA 6 Lucia, GTA 6 story, GTA 6 lore, Vice City, Leonida, "
          "what if you were born, what if you were born as, GTA 6 animation, GTA 6 characters, Grand Theft Auto 6",
    "tr": "GTA 6, GTA 6 Lucia, Lucia Caminos, Jason Duval, GTA 6 hikaye, GTA 6 türkçe, Vice City, Leonida, "
          "doğsaydın ne olurdu, GTA 6 animasyon, GTA 6 karakterleri",
    "de": "GTA 6, GTA VI, Lucia, Lucia Caminos, Jason Duval, GTA 6 Story, GTA 6 deutsch, Vice City, Leonida, "
          "was wäre wenn du geboren wärst, GTA 6 Animation, GTA 6 Charaktere",
}

def ts(t):
    t = int(t); return f"{t // 60}:{t % 60:02d}"

def chapters(shots, lang):
    out = []
    for sh in shots:
        ch = sh.s.get("chapter")
        if ch is not None:
            out.append(f"{ts(0 if ch == 0 else sh.start)} {CH_NAMES[lang][ch]}")
    return "\n".join(out)

if __name__ == "__main__":
    shots, total = build()
    os.makedirs(os.path.join(ROOT, "output"), exist_ok=True)
    for lang in ("en", "tr", "de"):
        txt = (f"TITLE:\n{TITLE[lang]}\n\nDESCRIPTION:\n" + DESC[lang].format(chapters=chapters(shots, lang)) +
               f"\n\nTAGS:\n{TAGS[lang]}\n")
        p = os.path.join(ROOT, "output", f"youtube_{lang}.txt")
        open(p, "w", encoding="utf-8").write(txt)
        print(p)
