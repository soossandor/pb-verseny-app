import streamlit as st
from google import genai
from google.genai import types

# 1. Alapbeállítások és stílus (Mobilra optimalizálva)
st.set_page_config(page_title="Sopron Pickleball Asszisztens", page_icon="🏓", layout="centered")

st.title("🏓 Sopron Pickleball & Fesztivál Asszisztens")
st.write("Írd be a neved vagy a kérdésed! Kikeresem a menetrended, segítek a szabályokban, vagy adok élő tippeket **Sopron városával** és a **Sopron Festtel** kapcsolatban!")

# Új tájékoztató sáv a szombati meccseredményekről
st.success("🔥 **ÚJDONSÁG:** Most már a **szombati nap összes eredményéről** is kérdezhetsz! Nemcsak a végső helyezések, hanem az összes lejátszott csoportmeccs és helyosztó pontos pontszáma is elérhető!")

# 2. A Gemini API kulcs biztonságos kezelése a felhőben
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Hiba: A GEMINI_API_KEY nem található a Streamlit Secrets beállításokban!")
    st.stop()

# 3. A VERSENY FIX ADATBÁZISA
VERSENY_KONTEXTUS = """
=== 1. ÁLTALÁNOS VERSENYINFORMÁCIÓK ÉS SZABÁLYOK ===
- Verseny megnevezése: Magyar Országos Pickleball Bajnokság 2026 - Másodosztály - 3. forduló.
- Időpont: 2026. július 4-05. (Szombat és Vasárnap).
- Helyszín: 9400 Sopron, Lővér krt. 1., SVSE Sporttelep.
- Hivatalos Labda: Franklin márkájú kültéri labda. A labda színével megegyező vagy ahhoz nagyon hasonló felszerelés (ruha) viselése TILOS!
- Mérkőzések menete: 1 nyert játszmáig (szettig) tartanak. A győzelemhez 11 pontot kell elérni, legalább 2 pont különbséggel.
- Térfélcsere: Amikor a mérkőzésen vezető játékos/páros eléri a 6 pontot, térfélcserére kerül sor.

=== 2. VASÁRNAPI MENETREND (2026.07.05.) ===
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

VEGYES PÁROSOK (VASÁRNAP):
- 09:40-től kezdődnek a Vegyes páros OB2/A és OB2/B csoportmérkőzések (Court 1-8).
- 13:20-tól: Vegyes páros egyenes kieséses szakasz (Negyeddöntők, Elődöntők, Helyosztók és Döntők).

=== 3. SZOMBATI CSOPORTMÉRKŐZÉSEK PONTOS EREDMÉNYEI ===
- Női egyéni OB2/A csoportmeccsek:
  * A csoport: Rédecsi Anna - Tábori Petra 11:4; Rupf Anna - Tábori Petra 12:10; Rupf Anna - Rédecsi Anna 7:11.
  * B csoport: Szabadits Eszter - Kecskés Rita 11:6; Takács Flóra - Horváth Ágnes 11:1; Szabadits Eszter - Horváth Ágnes 11:4; Takács Flóra - Kecskés Rita 11:1; Takács Flóra - Szabadits Eszter 11:2; Kecskés Rita - Horváth Ágnes 11:2.
- Női egyéni OB2/B körmérkőzések:
  * Sipos Anna - Feketéné Gyulai Dóra 11:1; Szabolcsiné Morvai Katalin - Viszokai Viktória 11:7; Sipos Anna - Viszokai Viktória 11:9; Szabolcsiné Morvai Katalin - Feketéné Gyulai Dóra 11:0; Sipos Anna - Szabolcsiné Morvai Katalin 11:2; Viszokai Viktória - Feketéné Gyulai Dóra 11:0.
- Férfi egyéni OB2/A csoportmeccsek:
  * A csoport: Mayer Iván - Berky Péter 11:5; Fekete Géza - Magyar B. 11:7; Mayer Iván - Fekete Géza 11:7; Berky Péter - Magyar B. 11:3; Mayer Iván - Magyar B. 11:5; Fekete Géza - Berky Péter 13:11.
  * B csoport: Alasztics Benjamin - Katona Milán 11:5; Török Bence - Takács Vince 11:5; Takács Vince - Katona Milán 11:8; Török Bence - Alasztics Benjamin 11:6; Török Bence - Katona Milán 11:1; Alasztics Benjamin - Takács Vince 11:9.
  * C csoport: Fogaras Pál - Ghalegolab Arman 11:0; Tomori Benedek - Szabolcsi Attila 12:10; Szabolcsi Attila - Ghalegolab Arman 11:3; Tomori Benedek - Fogaras Pál 11:4; Tomori Benedek - Ghalegolab Arman 11:4; Fogaras Pál - Szabolcsi Attila 11:5.
  * D csoport: Takács Attila - Kínál Zoltán 11:6; Magyar Csanád - Schmidt Adam 11:3; Csende Zsolt - Schmidt Adam 11:8; Magyar Csanád - Takács Attila 11:6; Takács Attila - Schmidt Adam 11:3; Csende Zsolt - Kínál Zoltán 13:11; Csende Zsolt - Takács Attila 11:4; Kínál Zoltán - Magyar Csanád 11:6; Csende Zsolt - Magyar Csanád 11:8; Kínál Zoltán - Schmidt Adam 11:9.
- Férfi páros OB2/A csoportmeccsek:
  * A csoport: Magyar D./Magyar B. - Csende/Ghalegolab 11:3; Szabolcsi/Katona - Magyar/Magyar 11:7; Szabolcsi/Katona - Csende/Ghalegolab 11:6.
  * B csoport: Takács V./Halápi - Szeli L./Kétszeri L. 11:4; Dobos/Török - Szeli L./Kétszeri L. 11:3; Dobos/Török - Takács V./Halápi 11:3.
  * C csoport: Tarr/Takács A. - Magyar Cs./Berky 11:6; Komáromi/Tomori - Schnell/Schnell 11:6; Tarr/Takács A. - Schnell/Schnell 11:2; Komáromi/Tomori - Magyar Cs./Berky 11:0; Komáromi/Tomori - Takács A./Tarr 11:4; Schnell/Schnell - Magyar Cs./Berky 11:5.
  * D csoport: Fogaras/Fekete G. - Püspök/Komócsin 11:0; Mayer/Schmidt - Kínál/Csernavay 11:5; Fogaras/Fekete G. - Kínál/Csernavay 11:6; Mayer/Schmidt - Komócsin/Püspök 11:2; Fogaras/Fekete G. - Mayer/Schmidt 11:8; Kínál/Csernavay - Püspök/Komócsin 11:9.
- Férfi egyéni OB2/B csoportmeccsek:
  * A csoport: Nagy Dávid - Dávid Ádám 11:8; Magyar Dániel - Dávid Ádám 11:2; Magyar Dániel - Nagy Dávid 11:9.
  * B csoport: Mészáros Szerhij - Bruckner Nándor 11:3; Pawletko Peter - Mészáros Szerhij 11:9; Pawletko Peter - Bruckner Nándor 11:1.
  * C csoport: Dinnyés János - Tran Van Dat 11:3; Szeli Lénárd - Péntek Vilmos 11:9; Dinnyés János - Péntek Vilmos 11:3; Szeli Lénárd - Tran Van Dat 11:7; Dinnyés János - Szeli Lénárd 11:9; Péntek Vilmos - Tran Van Dat 11:2.
  * D csoport: Tóth András - Tomori Tamás 11:5; Racz Robert - Fekete Barnabás 11:0; Racz Robert - Tóth András 11:8; Tomori Tamás - Fekete Barnabás 11:5; Tóth András - Fekete Barnabás 11:2; Racz Robert - Tomori Tamás 11:0.
- Férfi páros OB2/B csoportmeccsek:
  * A csoport: Gulyás/Karda - Bruckner/Füzi 11:2; Alasztics/Németh T. - Karda/Gulyás 11:3; Alasztics/Németh T. - Bruckner/Füzi 11:2.
  * B csoport: Fekete B./Dávid Á. - Decsi/Pál B. 12:10; Fekete B./Dávid Á. - Mészáros/Fekete K. 11:3; Fekete K./Mészáros Sz. - Decsi/Pál B. 11:1.
  * C csoport: Péntek/Racz R. - Kétszeri/Szeli L. 11:6; Pawletko/Tóth A. - Le/Le 11:6; Péntek/Racz R. - Le/Le 13:11; Pawletko/Tóth A. - Kétszeri/Szeli L. 11:1; Péntek/Racz R. - Pawletko/Tóth A. 11:0; Le/Le - Kétszeri/Szeli L. 11:0.
  * D csoport: Nagy D./Dinnyés - Németh A./Berta 11:4; Viszokai L./Molnár R. - Simon Z./Soós S. 11:5; Viszokai L./Molnár R. - Németh A./Berta 11:7; Dinnyés/Nagy D. - Simon Z./Soós S. 11:5; Nagy D./Dinnyés - Viszokai L./Molnár R. 11:4; Németh A./Berta - Simon Z./Soós S. 12:10.

=== 4. SZOMBATI HELYOSZTÓK ÉS EGYENES KIESÉSES MECCSEK EREDMÉNYEI ===
- Női egyéni OB2/A helyosztók:
  * Elődöntők: Tábori Petra - Szabadits Eszter 11:5; Takács Flóra - Rupf Anna 11:8. Döntő: Takács Flóra - Tábori Petra 11:8. 3. helyért: Rupf Anna - Szabadits Eszter 11:7. 5. helyért: Kecskés Rita - Rédecsi Anna 11:3. 
- Férfi egyéni OB2/A helyosztók:
  * Negyeddöntők: Mayer Iván - Fogaras Pál 11:5; Török Bence - Csende Zsolt 11:9; Tomori Benedek - Fekete Géza 11:3; Alasztics Benjamin - Magyar Csanád 11:1.
  * Elődöntők: Mayer Iván - Török Bence 11:3; Tomori Benedek - Alasztics Benjamin 11:3. Döntő: Mayer Iván - Tomori Benedek 12:10. 3. helyért: Török Bence - Alasztics Benjamin 11:6.
  * 5. helyért: Csende Zsolt - Magyar Csanád 11:8. 7. helyért: Fogaras Pál - Fekete Géza 11:7. 9. helyért: Szabolcsi Attila - Takács Attila 11:6. 11. helyért: Takács Vince - Berky Péter 11:5. 13. helyért: Katona Milán - Ghalegolab Arman 11:5. 15. helyért: Kínál Zoltán - Magyar Benedek 11:9.
- Férfi páros OB2/A helyosztók:
  * Elődöntők: Szabolcsi/Katona - Fogaras/Fekete 11:8; Dobos/Török - Komáromi/Tomori 11:8. Döntő: Dobos Ákos / Török Bence - Szabolcsi Attila / Katona Milán 11:3. 3. helyért: Komáromi Róbert / Tomori Benedek - Fogaras Pál / Fekete Géza 11:8.
  * 5. helyért: Takács A./Tarr - Magyar/Magyar 11:4. 7. helyért: Schmidt/Mayer - Takács V./Halápi 11:1. 9. helyért: Ghalegolab/Csende - Endre/Kínál 11:4. 11. helyért: Schnell/Schnell - Szeli L./Kétszeri L. 11:5. 13. helyért: Magyar Csanád / Berky Péter - Komócsin Balázs / Püspök Patrik 11:7.
- Férfi egyéni OB2/B helyosztók:
  * Elődöntők: Mészáros Szerhij - Szeli Lénárd 12:10; Dinnyés János - Tóth András 11:8. Döntő: Mészáros Szerhij - Dinnyés János 11:5. 3. helyért: Tóth András - Szeli Lénárd 11:7.
  * 5. helyért: Racz Robert - Pawletko Peter 11:9. 9. helyért: Nagy Dávid - Tomori Tamás 11:5. 11. helyért: Péntek Vilmos - Bruckner Nándor 11:0. 13. helyért: Fekete Barnabás - Tran Van Dat 11:9.
- Férfi páros OB2/B helyosztók:
  * Elődöntők: Alasztics/Németh T. - Fekete K./Mészáros Sz. 11:4; Péntek V./Racz R. - Viszokai L./Molnár R. 11:3. Döntő: Alasztics Benjamin / Németh Tamás - Péntek Vilmos / Racz Robert 11:4. 3. helyért: Fekete Kristóf / Mészáros Szerhij - Viszokai László / Molnár Róbert 11:6.
  * 5. helyért: Dinnyés/Nagy D. - Fekete B./Dávid Á. 11:8. 7. helyért: Pawletko/Tóth A. - Karda/Gulyás 11:3. 9. helyért: Berta Szabolcs / Németh Attila - Le Tan Minh / Le Tan Dung 11:9. 13. helyért: Sándor Soós / Zsolt Simon - Lénárd Szeli / Dániel Kétszeri 11:1.

=== 5. SZOMBATI KATEGÓRIÁK HIVATALOS VÉGEREDMÉNYEI ===
- Női egyéni OB2/A: 1. Takács Flóra, 2. Tábori Petra, 3. Rupf Anna, 4. Szabadits Eszter.
- Női egyéni OB2/B: 1. Sipos Anna, 2. Viszokai Viktória, 3. Szabolcsiné Morvai Katalin, 4. Feketéné Gyulai Dóra.
- Férfi egyéni OB2/A: 1. Mayer Iván, 2. Tomori Benedek, 3. Török Bence, 4. Alasztics Benjamin, 5. Csende Zsolt, 6. Magyar Csanád, 7. Fogaras Pál, 8. Fekete Géza.
- Férfi páros OB2/A: 1. Dobos Ákos / Török Bence, 2. Szabolcsi Attila / Katona Milán, 3. Komáromi Róbert / Tomori Benedek, 4. Fogaras Pál / Fekete Géza, 5. Takács Attila / Tarr Sándor.
- Férfi egyéni OB2/B: 1. Mészáros Szerhij, 2. Dinnyés János, 3. Tóth András, 4. Szeli Lénárd, 5. Racz Robert, 6. Pawletko Peter, 7. Dávid Ádám.
- Férfi páros OB2/B: 1. Alasztics Benjamin / Németh Tamás, 2. Péntek Vilmos / Racz Robert, 3. Fekete Kristóf / Mészáros Szerhij, 4. Viszokai László / Molnár Róbert ... 13. Soós Sándor / Simon Zsolt, 14. Szeli Lénárd / Kétszeri Dániel.
"""

# 4. Rendszer-utasítások konfigurálása
SYSTEM_INSTRUCTION = f"""
Te egy profi Pickleball Versenybíró és Mentor vagy, aki most Sopronban tartózkodik az Országos Bajnokságon. A küldetésed a játékosok és látogatók maximális kiszolgálása.

A válaszadás során az alábbi prioritási és témakör-rendet kövesd:

1. SOPRONI VERSENYADATOK: Ha a kérdés a konkrét hétvégi soproni menetrendre, szombati csoportmeccsekre vagy rájátszás eredményekre, játékosokra, helyszínre vagy egyedi szabályokra vonatkozik, KIZÁRÓLAG az alábbi adatokból dolgozhatsz:
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