import streamlit as st
from google import genai
from google.genai import types

# 1. Alapbeállítások és stílus (Mobilra optimalizálva)
st.set_page_config(page_title="Sopron Pickleball Asszisztens", page_icon="🏓", layout="centered")

st.title("🏓 Sopron Pickleball & Fesztivál Asszisztens")
st.write("Írd be a neved vagy a kérdésed! Kikeresem a menetrended, segítek a szabályokban, vagy adok élő tippeket **Sopron városával** és a **Sopron Festtel** kapcsolatban!")

# 2. A Gemini API kulcs biztonságos kezelése a felhőben
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Hiba: A GEMINI_API_KEY nem található a Streamlit Secrets beállításokban!")
    st.stop()

# 3. A VERSENY FIX ADATBÁZISA (Szombati élő meccseredményekkel kiegészítve)
VERSENY_KONTEXTUS = """
=== 1. ÁLTALÁNOS VERSENYINFORMÁCIÓK ÉS SZABÁLYOK ===
- Verseny megnevezése: Magyar Országos Pickleball Bajnokság 2026 - Másodosztály - 3. forduló.
- Időpont: 2026. július 4-05. (Szombat és Vasárnap).
- Helyszín: 9400 Sopron, Lővér krt. 1., SVSE Sporttelep.
- Versenybizottság: Böhm Zoltán (+36 30/458-1231), Miklós László (+36 30/274-9423), Takács Attila (Póttag: Komáromi Róbert).
- Hivatalos Labda: Franklin márkájú kültéri labda. A labda színével megegyező vagy ahhoz nagyon hasonló felszerelés (ruha) viselése TILOS!
- Bemelegítés: Minden mérkőzés előtt pontosan 2 perc áll rendelkezésre. Ha a játékos a bemelegítés végére nem jelenik meg, leléptethető.
- Pontozólapok kezelése: A mérkőzés előtt a menetrendben elöl/bal oldalon szereplő csapat veszi át a zsűriasztalnál. A meccs után a győztes feladata a helyes kitöltés és a leadás a befejezést követő 2 percen belül.
- Mérkőzések menete: 1 nyert játszmáig (szettig) tartanak. A győzelemhez 11 pontot kell elérni, legalább 2 pont különbséggel.
- Térfélcsere: Amikor a mérkőzésen vezető játékos/páros eléri a 6 pontot, térfélcserére kerül sor.
- Időkérés: Meccsenként minden játékosnak/párosnak pontosan 1 db időkérési lehetősége van.
- Mérkőzésvezetés: Külön mérkőzésvezető nincs (kivéve esetleg a rájátszást), a játékosok a fair-play alapján maguknak bíráskodnak.
- Óvás: Csak a verseny ideje alatt, írásban, 10.000 Ft óvási díj megfizetésével nyújtható be a versenyző által. Elfogadás Arrays esetén visszajár.

=== 2. CSOPORTKÖRÖK ÉS LEBONYOLÍTÁSI REND ===
A csoportok rangsorolása: 1. Több győzelem, 2. Egymás elleni eredmény (ha 2 holtverseny van), 3. Pontarány (szerzett/vesztett pontok), 4. Egymás elleni mérkőzés.

=== 3. VASÁRNAPI MENETREND (2026.07.05.) ===
M1 KÖR - NŐI PÁROSOK KEZDETE (08:00):
- Court 1: F. SZELI / A. RUPF vs. J. POLGÁR / A. CSATÁRI (Női páros OB2/A - Group A-R1)
- Court 2: K. MISZLAI-KOMÓCSIN / A. RÉDECSI vs. M. MÁTÉ-SZALAI / A. SIPOS (Női páros OB2/A - Group A-R1)
- Court 3: N. CSIGÓ / E. HORVÁTH vs. R. HORVÁTH / K. LUKÁCS (Női páros OB2/A - Group B-R1)
- Court 4: P. TABORI / F. TAKÁCS vs. E. HRANYCZKA / L. HRANYCZKA (Női páros OB2/A - Group B-R1)
- Court 5: K. JAGICZA / K. MOJZER vs. R. KECSKÉS / K. SZABOLCSINÉ MORVAI (Női páros OB2/B - Group A-R1)
- Court 6: E. FANCSALINÉ KOTÁN / M. CSILLAG vs. R. FEKETE ANDREA / D. FEKETÉNÉ GYULAI (Női páros OB2/B - Group A-R1)
- Court 7: A. KÉTSZERINÉ SZŰCS / B. KOMÓCSIN vs. G. PETRA / E. RUBINT (Női páros OB2/B - Group B-R1)
- Court 8: N. KECSKÉS AMÁTA / L. PETROVICS vs. E. NÉMETH / G. BRINDZA (Női páros OB2/B - Group B-R1)

M2 KÖR (08:20):
- Court 1: A. RUPF / F. SZELI vs. M. MÁTÉ-SZALAI / A. SIPOS (Női páros OB2/A - Group A-R2)
- Court 2: J. POLGÁR / A. CSATÁRI vs. K. MISZLAI-KOMÓCSIN / A. RÉDECSI (Női páros OB2/A - Group A-R2)
- Court 3: P. TABORI / F. TAKÁCS vs. K. LUKÁCS / R. HORVÁTH (Női páros OB2/A - Group B-R2)
- Court 4: E. HRANYCZKA / L. HRANYCZKA vs. N. CSIGÓ / E. HORVÁTH (Női páros OB2/A - Group B-R2)
- Court 5: K. JAGICZA / K. MOJZER vs. D. FEKETÉNÉ GYULAI / R. FEKETE ANDREA (Női páros OB2/B - Group A-R2)
- Court 6: K. SZABOLCSINÉ MORVAI / R. KECSKÉS vs. M. CSILLAG / E. FANCSALINÉ KOTÁN (Női páros OB2/B - Group A-R2)
- Court 7: L. PETROVICS / N. KECSKÉS AMÁTA vs. G. PETRA / E. RUBINT (Női páros OB2/B - Group B-R2)
- Court 8: G. BRINDZA / E. NÉMETH vs. B. KOMÓCSIN / A. KÉTSZERINÉ SZŰCS (Női páros OB2/B - Group B-R2)

M3 KÖR (08:40):
- Court 1: F. SZELI / A. RUPF vs. K. MISZLAI-KOMÓCSIN / A. RÉDECSI (Női páros OB2/A - Group A-R3)
- Court 2: M. MÁTÉ-SZALAI / A. SIPOS vs. A. CSATÁRI / J. POLGÁR (Női páros OB2/A - Group A-R3)
- Court 3: F. TAKÁCS / P. TÁBORI vs. E. HORVÁTH / N. CSIGÓ (Női páros OB2/A - Group B-R3)
- Court 4: K. LUKÁCS / R. HORVÁTH vs. L. HRANYCZKA / E. HRANYCZKA (Női páros OB2/A - Group B-R3)
- Court 5: K. JAGICZA / K. MOJZER vs. E. FANCSALINÉ KOTÁN / M. CSILLAG (Női páros OB2/B - Group A-R3)
- Court 6: D. FEKETÉNÉ GYULAI / R. FEKETE ANDREA vs. R. KECSKÉS / K. SZABOLCSINÉ MORVAI (Női páros OB2/B - Group A-R3)
- Court 7: N. KECSKÉS AMÁTA / L. PETROVICS vs. A. KÉTSZERINÉ SZŰCS / B. KOMÓCSIN (Női páros OB2/B - Group B-R3)
- Court 8: E. RUBINT / G. PETRA vs. E. NÉMETH / G. BRINDZA (Női páros OB2/B - Group B-R3)

09:00-tól: Női páros elődöntők, helyosztók és döntők (OB2/A és OB2/B).

VASÁRNAP DELES ÉS DÉLUTÁNI VEGYES PÁROSOK:
- 09:40-től kezdődnek a Vegyes páros OB2/A és OB2/B csoportmérkőzések (A, B, C, D csoportok) a kiírt pályákon (Court 1-8).
- 13:20-tól: Vegyes páros egyenes kieséses szakasz (Negyeddöntők, Elődöntők, Helyosztók és Döntők).

=== 4. SZOMBATI HIVATALOS MÉRKŐZÉSEREDMÉNYEK ÉS JÁTÉKOS STATISZTIKÁK ===
- NŐI EGYÉNI OB2/A FŐÁG:
  * Elődöntők: Tábori Petra győzött Szabadits Eszter ellen 11:5; Takács Flóra győzött Rupf Anna ellen 11:8.
  * Döntő: Takács Flóra győzött Tábori Petra ellen 11:7 (Takács Flóra az Országos Bajnok!).
  * 3. helyért: Rupf Anna győzött Szabadits Eszter ellen 11:7.
  * Mellékág (5-7. hely): Rédecsi Anna - Horváth Ágnes 11:1; Kecskés Rita - Rédecsi Anna 11:3 (Kecskés Rita lett az 5.).

- NŐI EGYÉNI OB2/B KÖRMÉRKŐZÉSEK:
  * Sipos Anna - Feketéné Gyulai Dóra 11:1; Szabolcsiné Morvai Katalin - Viszokai Viktória 11:7.
  * Sipos Anna - Viszokai Viktória 11:9; Szabolcsiné Morvai Katalin - Feketéné Gyulai Dóra 11:0.
  * Sipos Anna - Szabolcsiné Morvai Katalin 11:2; Viszokai Viktória - Feketéné Gyulai Dóra 11:0.

- FÉRFI EGYÉNI OB2/A FŐÁG:
  * Negyeddöntők: Mayer Iván - Fogaras Pál 11:5; Török Bence - Csende Zsolt 11:9; Tomori Benedek - Fekete Géza 11:3; Alasztics Benjamin - Magyar Csanád 11:1.
  * Elődöntők: Mayer Iván - Török Bence 11:3; Tomori Benedek - Alasztics Benjamin 11:3.
  * Döntő: Mayer Iván - Tomori Benedek 12:10 (Mayer Iván az Országos Bajnok!).
  * 3. helyért: Török Bence - Alasztics Benjamin 11:6.
  * Helyosztók (5-8. hely): Csende Zsolt - Fogaras Pál 11:6; Magyar Csanád - Fekete Géza 11:2; Csende Zsolt - Magyar Csanád 11:8 (Csende 5., Magyar Cs. 6.); Fogaras Pál - Fekete Géza 11:7 (Fogaras 7., Fekete G. 8.).
  * Mellékág (9-12. hely): Szabolcsi Attila - Berky Péter 11:7; Takács Attila - Takács Vince 11:2; Döntő (9. helyért): Szabolcsi Attila - Takács Attila 11:6; 11. helyért: Takács Vince - Berky Péter 11:5.
  * Vigaszág (13-16. hely): Ghalegolab Arman - Magyar Benedek 11:5; Katona Milán - Kínál Zoltán 11:3; Döntő (13. helyért): Katona Milán - Ghalegolab Arman 11:5; 15. helyért: Kínál Zoltán - Magyar Benedek 11:9.

- FÉRFI PÁROS OB2/A FŐÁG:
  * Negyeddöntők: Szabolcsi/Katona - Takács A./Tarr 11:5; Fogaras/Fekete - Takács V./Halápi 11:7; Komáromi/Tomori - Magyar B./Magyar D. 11:1; Dobos/Török - Schmidt/Mayer 11:2.
  * Elődöntők: Szabolcsi/Katona - Fogaras/Fekete 11:8; Dobos/Török - Komáromi/Tomori 11:8.
  * Döntő: Dobos Ákos / Török Bence - Szabolcsi Attila / Katona Milán 11:2 (Dobos/Török a bajnokpár!).
  * 3. helyért: Komáromi Róbert / Tomori Benedek - Fogaras Pál / Fekete Géza 11:3.
  * Helyosztók (5-8. hely): Takács A./Tarr - Takács V./Halápi 11:2; Magyar/Magyar - Schmidt/Mayer 11:0; 5. helyért: Takács A./Tarr - Magyar/Magyar 11:4; 7. helyért: Schmidt/Mayer - Takács V./Halápi 11:1.
  * Mellékág (9-12. hely): Ghalegolab/Csende - Schnell/Schnell 11:3; Endre/Kínál - Szeli L./Kétszeri L. 11:7; 9. helyért: Ghalegolab/Csende - Endre/Kínál 11:4; 11. helyért: Schnell/Schnell - Szeli L./Kétszeri L 11:5.
  * 13. helyért: Magyar Csanád / Berky Péter - Komócsin Balázs / Püspök Patrik 11:7.

- FÉRFI EGYÉNI OB2/B FŐÁG:
  * Negyeddöntők: Szeli Lénárd - Magyar Dániel 11:8; Mészáros Szerhij - Racz Robert 11:7; Dinnyés János - Dávid Ádám 11:9; Tóth András - Pawletko Peter 11:8.
  * Elődöntők: Mészáros Szerhij - Szeli Lénárd 12:10; Dinnyés János - Tóth András 11:8.
  * Döntő: Mészáros Szerhij - Dinnyés János 11:5 (Mészáros Szerhij a bajnok!).
  * 3. helyért: Tóth András - Szeli Lénárd 11:7.
  * Helyosztók (5-8. hely): Racz Robert - Magyar Dániel (W/O); Pawletko Peter - Dávid Ádám 12:10; 5. helyért: Racz Robert - Pawletko Peter 11:9; 7. helyért: Dávid Ádám - Magyar Dániel (W/O).
  * Mellékág (9-12. hely): Nagy Dávid - Péntek Vilmos 11:6; Tomori Tamás - Bruckner Nándor 11:2; 9. helyért: Nagy Dávid - Tomori Tamás 11:5; 11. helyért: Péntek Vilmos - Bruckner Nándor 11:0.
  * 13. helyért: Fekete Barnabás - Tran Van Dat 11:9.

- FÉRFI PÁROS OB2/B FŐÁG:
  * Negyeddöntők: Alasztics/Németh T. - Pawletko/Tóth A. 11:0; Fekete K./Mészáros Sz. - Dinnyés/Nagy D. 11:2; Péntek V./Racz R. - Karda/Gulyás 11:1; Viszokai L./Molnár R. - Fekete B./Dávid Á. 11:3.
  * Elődöntők: Alasztics/Németh T. - Fekete K./Mészáros Sz. 11:4; Péntek V./Racz R. - Viszokai L./Molnár R. 11:3.
  * Döntő: Alasztics Benjamin / Németh Tamás - Péntek Vilmos / Racz Robert 11:6 (Alasztics/Németh a bajnokpár!).
  * 3. helyért: Fekete Kristóf / Mészáros Szerhij - Viszokai László / Molnár Róbert 11:6.
  * Helyosztók (5-8. hely): Dinnyés/Nagy D. - Pawletko/Tóth A. 11:3; Fekete B./Dávid Á. - Karda/Gulyás 11:4; 5. helyért: Dinnyés/Nagy D. - Fekete B./Dávid Á. 11:8; 7. helyért: Pawletko/Tóth A. - Karda/Gulyás 11:3.
  * Mellékág (9-12. hely): Berta/Németh A. - Decsi/Pál B. 11:3; Le/Le - Bruckner/Füzi (W/O); 9. helyért: Berta Szabolcs / Németh Attila - Le Tan Minh / Le Tan Dung 11:9; 11. helyért: Decsi Gábor / Pál Barnabás - Bruckner/Füzi (W/O).
  * 13. helyért: Sándor Soós / Zsolt Simon - Lénárd Szeli / Dániel Kétszeri 11:1.
"""

# 4. Rendszer-utasítások konfigurálása
SYSTEM_INSTRUCTION = f"""
Te egy profi Pickleball Versenybíró és Mentor vagy, aki most Sopronban tartózkodik az Országos Bajnokságon. A küldetésed a játékosok és látogatók maximális kiszolgálása.

A válaszadás során az alábbi prioritási és témakör-rendet kövesd:

1. SOPRONI VERSENYADATOK: Ha a kérdés a konkrét hétvégi soproni menetrendre, szombati meccseredményekre, játékosokra, helyszínre vagy egyedi szabályokra vonatkozik, KIZÁRÓLAG az alábbi adatokból dolgozhatsz:
{VERSENY_KONTEXTUS}
Amennyiben a kérdés egy olyan konkrét soproni tornára vonatkozó adatra irányul, ami nincs benne a szövegben, mondd azt: "Erről nincs pontos információm a kiírásban, kérlek fordulj a versenybíróhoz!"

2. ÁLTALÁNOS PICKLEBALL TUDÁS: Ha a kérdés általános pickleball szabályra, kifejezésre, pontozásra, ütésfajtára vagy taktikára vonatkozik, használd a saját széleskörű pickleball szakértelmedet, és válaszolj rá részletesen és segítőkészen.

3. SOPRON VÁROSA ÉS SOPRON FEST: Ha a kérdés Sopron látnivalóira, éttermeire, helyi közlekedésére, vagy a most hétvégén zajló Sopron Fest zenei/kulturális fesztiválra, annak hangulatára, helyszínére vagy részletes napi programjaira vonatkozik, válaszolj bátran a Google Keresés segítségével! Segíts nekik naprakész fesztivál- és városi tippekkel.

4. SZIGORÚ TÉMAKORLÁT: Ha a kérdés egyáltalán NEM kapcsolódik a pickleballhoz, a soproni bajnoksághoz, Sopron városához vagy a Sopron Festhez, akkor NE válaszolj rá! Udvariasan, pici sportos humorral utasítsd vissza, és emlékeztesd a felhasználót, hogy ez az app kizárólag a Sopron Pickleball & Fesztivál hivatalos asszisztense.

Szabályok:
- Használj listákat és félkövér kiemeléseket a lényeges részeknél (időpontok, pályák, helyszínek) a könnyebb olvashatóságért!
- A stílusod legyen sportszerű, profi, de barátságos és közvetlen.
"""

# 5. Felhasználói felület és keresési logika ÉLŐ GOOGLE GROUNDING-AL
user_query = st.text_input("Mit szeretnél tudni? (pl. 'Mayer Iván meccsei', 'Ki ellen nyert meccset Soós Sándor?', 'Ki lép fel ma este a Sopron Festen?')", "")

if user_query:
    try:
        # Az új, hivatalos Google GenAI kliens inicializálása
        client = genai.Client(api_key=api_key)
        
        with st.spinner("Asszisztens gondolkodik és keres..."):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_query,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    tools=[{"google_search": {}}]
                )
            )
            
        st.chat_message("assistant").write(response.text)
        
    except Exception as e:
        st.error(f"Hiba történt a lekérdezés során: {e}")

st.info("Tipp: Ha a saját menetrendedet keresed, pontosan úgy írd be a neved, ahogy a nevezési listában szerepel (pl. 'SIPOS ANNA').")