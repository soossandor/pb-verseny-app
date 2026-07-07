import streamlit as st
from google import genai
from google.genai import types

# 1. Alapbeállítások és stílus (Mobilra optimalizálva)
st.set_page_config(page_title="Sopron Pickleball Asszisztens", page_icon="🏓", layout="centered")

st.title("🏓 Sopron Pickleball & Fesztivál Asszisztens")
st.write("Írd be a neved vagy a kérdésed! Kikeresem a menetrended, segítek a szabályokban, vagy adok élő tippeket **Sopron városával** és a **Sopron Festtel** kapcsolatban!")

# Siker sáv a lezárt, auditált hétvégi eredménytárhoz
st.success("🎉 **MEGLEPETÉS:** A verseny sikeresen lezárult! Az asszisztens a teljes hétvége összes számszerű meccs- és csoportgyőzelmét ismeri, 100%-os bírói pontossággal!")

# LÁTVÁNYOS NYOMÓGOMBOK A HÉTVÉGI FOTÓKHOZ ÉS VIDEÓKHOZ
st.subheader("📸 Hivatalos Fotók és Videók Mappái")
col1, col2 = st.columns(2)
with col1:
    st.link_button("🎬 Vasárnapi Eredményhirdetés (Videó)", "https://drive.google.com/file/d/1ir7T5Gyg1v9Hi74oXCt5hSulGNIC8gIl/view?usp=sharing")
    st.link_button("📷 Szombati Díjátadó (Képek)", "https://drive.google.com/drive/u/0/folders/1btewN9JCocdESGwm0D5gMKiYAoTOBDpb")
    st.link_button("📹 Szombati Vágatlan Meccsek (Videó)", "https://drive.google.com/drive/folders/1Nhd4uteCtM-bnJGwgX7fq_C58v1h7UtA")
with col2:
    st.link_button("📷 Vasárnapi Díjátadó (Képek)", "https://drive.google.com/drive/u/0/folders/1eA8GYR1ZfxWf38Vuf9_leZ7Wdg5nZOwI")
    st.link_button("📹 Vasárnapi Vágatlan Meccsek (Videó)", "https://drive.google.com/drive/folders/1POj4Lqn9U3Hav0LIlCf132JXy-lMu13K?usp=sharing")

# 2. A Gemini API kulcs biztonságos kezelése a felhőben
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Hiba: A GEMINI_API_KEY nem található a Streamlit Secrets beállításokban!")
    st.stop()

# 3. A TELJES HÉTVÉGE HIVATALOS ADATBÁZISA (Javított meccseredményekkel és médiatárral)
VERSENY_KONTEXTUS = """
=== 1. ÁLTALÁNOS VERSENYINFORMÁCIÓK ===
- Verseny megnevezése: Magyar Országos Pickleball Bajnokság 2026 - Másodosztály - 3. forduló.
- Időpont: 2026. július 4-05.
- Helyszín: 9400 Sopron, Lővér krt. 1., SVSE Sporttelep.
- Versenybizottság: Böhm Zoltán, Miklós László, Takács Attila.
- Mérkőzések szabálya: 1 nyert játszmáig (szettig) tartanak, 11 elért pontig, legalább 2 pont különbséggel. 6 pontnál térfélcsere.

=== 2. SZOMBATI CSOPORTMÉRKŐZÉSEK PONTOS SZÁMSZERŰ EREDMÉNYEI ===
- Női egyéni OB2/A csoportmeccsek:
  * A csoport: Rédecsi Anna - Tábori Petra 11:4; Rupf Anna - Tábori Petra 12:10; Rédecsi Anna - Rupf Anna 11:7.
  * B csoport: Szabadits Eszter - Kecskés Rita 11:6; Takács Flóra - Horváth Ágnes 11:1; Szabadits Eszter - Horváth Ágnes 11:4; Takács Flóra - Kecskés Rita 11:1; Takács Flóra - Szabadits Eszter 11:2; Kecskés Rita - Horváth Ágnes 11:2.
- Női egyéni OB2/B körmérkőzések:
  * Sipos Anna - Feketéné Gyulai Dóra 11:1; Szabolcsiné Morvai Katalin - Viszokai Viktória 11:7; Sipos Anna - Viszokai Viktória 11:9; Szabolcsiné Morvai Katalin - Feketéné Gyulai Dóra 11:0; Sipos Anna - Szabolcsiné Morvai Katalin 11:2; Viszokai Viktória - Feketéné Gyulai Dóra 11:0.
- Férfi egyéni OB2/A csoportmeccsek:
  * A csoport: Mayer Iván - Berky Péter 11:5; Fekete Géza - Magyar Benedek 11:7; Mayer Iván - Fekete Géza 11:7; Berky Péter - Magyar Benedek 11:3; Mayer Iván - Magyar Benedek 11:5; Fekete Géza - Berky Péter 13:11.
  * B csoport: Alasztics Benjamin - Katona Milán 11:5; Török Bence - Takács Vince 11:5; Takács Vince - Katona Milán 11:8; Török Bence - Alasztics Benjamin 11:6; Török Bence - Katona Milán 11:1; Alasztics Benjamin - Takács Vince 11:9.
  * C csoport: Fogaras Pál - Ghalegolab Arman 11:0; Tomori Benedek - Szabolcsi Attila 12:10; Szabolcsi Attila - Ghalegolab Arman 11:3; Tomori Benedek - Fogaras Pál 11:4; Tomori Benedek - Ghalegolab Arman 11:4; Fogaras Pál - Szabolcsi Attila 11:5.
  * D csoport: Takács Attila - Kínál Zoltán 11:6; Magyar Csanád - Schmidt Adam Anton 11:3; Csende Zsolt - Schmidt Adam Anton 11:8; Magyar Csanád - Takács Attila 11:6; Takács Attila - Schmidt Adam Anton 11:3; Csende Zsolt - Kínál Zoltán 13:11; Csende Zsolt - Takács Attila 11:4; Kínál Zoltán - Magyar Csanád 11:6; Csende Zsolt - Magyar Csanád 11:8; Kínál Zoltán - Schmidt Adam Anton 11:9.
- Férfi páros OB2/A csoportmeccsek:
  * A csoport: Ghalegolab/Csende - Magyar B./Magyar D. 11:3; Szabolcsi/Katona - Magyar B./Magyar D. 11:7; Szabolcsi/Katona - Ghalegolab/Csende 11:6.
  * B csoport: Takács V./Halápi - Szeli L./Kétszeri L. 11:4; Dobos/Török - Szeli L./Kétszeri L. 11:3; Dobos/Török - Takács V./Halápi 11:3.
  * C csoport: Tarr/Takács A. - Magyar Cs./Berky 11:6; Komáromi/Tomori - Schnell/Schnell 11:6; Tarr/Takács A. - Schnell/Schnell 11:2; Komáromi/Tomori - Magyar Cs./Berky 11:0; Komáromi/Tomori - Takács A./Tarr 11:4; Schnell/Schnell - Magyar Cs./Berky 11:5.
  * D csoport: Fogaras/Fekete G. - Püspök/Komócsin 11:0; Mayer/Schmidt - Kínál/Csernavay 11:5; Fogaras/Fekete G. - Kínál/Csernavay 11:6; Mayer/Schmidt - Komócsin/Püspök 11:2; Fogaras/Fekete G. - Mayer/Schmidt 11:8; Kínál/Csernavay - Püspök/Komócsin 11:9.
- Férfi egyéni OB2/B csoportmeccsek:
  * A csoport: Dávid Ádám - Nagy Dávid 11:8; Magyar Dániel - Dávid Ádám 11:2; Magyar Dániel - Nagy Dávid 11:9.
  * B csoport: Mészáros Szerhij - Bruckner Nándor 11:3; Pawletko Peter - Mészáros Szerhij 11:9; Pawletko Peter - Bruckner Nándor 11:1.
  * C csoport: Dinnyés János - Tran Van Dat 11:3; Szeli Lénárd - Péntek Vilmos 11:9; Dinnyés János - Péntek Vilmos 11:3; Szeli Lénárd - Tran Van Dat 11:7; Dinnyés János - Szeli Lénárd 11:9; Péntek Vilmos - Tran Van Dat 11:2.
  * D csoport: Tóth András - Tomori Tamás 11:5; Racz Robert - Fekete Barnabás 11:0; Racz Robert - Tóth András 11:8; Tomori Tamás - Fekete Barnabás 11:5; Tóth András - Fekete Barnabás 11:2; Racz Robert - Tomori Tamás 11:0.
- Férfi páros OB2/B csoportmeccsek:
  * A csoport: Gulyás/Karda - Bruckner/Füzi 11:2; Alasztics/Németh T. - Karda/Gulyás 11:3; Alasztics/Németh T. - Bruckner/Füzi 11:2.
  * B csoport: Fekete B./Dávid Á. - Decsi/Pál B. 12:10; Fekete B./Dávid Á. - Mészáros/Fekete K. 11:3; Fekete K./Mészáros Sz. - Decsi/Pál B. 11:1.
  * C csoport: Péntek/Racz R. - Kétszeri/Szeli L. 11:6; Pawletko/Tóth A. - Le/Le 11:6; Péntek/Racz R. - Le/Le 13:11; Pawletko/Tóth A. - Kétszeri/Szeli L. 11:1; Péntek/Racz R. - Pawletko/Tóth A. 11:0; Le/Le - Kétszeri/Szeli L. 11:0.
  * D csoport: Nagy D./Dinnyés - Németh A./Berta 11:4; Viszokai L./Molnár R. - Simon Zsolt/Soós Sándor 11:5; Viszokai L./Molnár R. - Németh A./Berta 11:7; Dinnyés/Nagy D. - Simon Zsolt/Soós Sándor 11:5; Nagy D./Dinnyés - Viszokai L./Molnár R 11:4; Németh A./Berta - Simon Zsolt/Soós Sándor 12:10.

=== 3. VASÁRNAPI CSOPORTMÉRKŐZÉSEK PONTOS SZÁMSZERŰ EREDMÉNYEI ===
- Női páros OB2/A csoportmeccsek:
  * A csoport: Szeli F./Rupf - Polgár/Csatári 11:1; Kinga Miszlai-Komócsin / Anna Rédecsi - Máté-Szalai/Sipos 12:10; Szeli F./Rupf - Máté-Szalai/Sipos 11:7; Kinga Miszlai-Komócsin / Anna Rédecsi - Polgár/Csatári 11:4; Szeli F./Rupf - Miszlai-Komócsin/Rédecsi 11:4; Máté-Szalai/Sipos - Csatári/Polgár 12:10.
  * B csoport: Csigó/Horváth E. - Horváth R./Lukács 11:6; Tábori/Takács F. - Hranyczka/Hranyczka L-né 11:1; Tábori/Takács F. - Horváth R./Lukács 11:1; Hranyczka/Hranyczka L-né - Csigó/Horváth E. 11:7; Tábori/Takács F. - Csigó/Horváth E. 11:5; Horváth R./Lukács - Hranyczka/Hranyczka L-né 11:7.
- Női páros OB2/B csoportmeccsek:
  * A csoport: Jagicza/Mojzer - Szabolcsiné/Kecskés 11:6; Csillag/Fancsaliné - Feketéné/Fekete Andrea 11:1; Katalin Szabolcsiné Morvai / Rita Kecskés - Csillag/Fancsaliné 11:9; Jagicza/Mojzer - Feketéné/Fekete Andrea 11:0; Jagicza/Mojzer - Csillag/Fancsaliné 11:0; Kecskés/Szabolcsiné - Feketéné/Fekete Andrea 11:0.
  * B csoport: Komócsin L-né/Kétszeriné - Gyimesi-Varga/Rubint 11:6; Petrovics/Kecskés Amáta - Brindza/Németh E. 11:1; Petrovics/Kecskés Amáta - Rubint/Gyimesi-Varga 12:10; Brindza/Németh E. - Komócsin L-né/Kétszeriné 11:5; Petrovics/Kecskés Amáta - Komócsin L-né/Kétszeriné 11:4; Rubint/Gyimesi-Varga - Brindza/Németh E. 11:8.
- Vegyes páros OB2/A csoportmeccsek:
  * A csoport: Tarr/Tarrné - Torma/Máté-Szalai 11:6; Szabolcsi/Szabolcsiné - Komócsin/Szeli I. 11:7; Szeli F./Fekete G. - Torma/Máté-Szalai 11:3; Tarr/Tarrné - Szabolcsi/Szabolcsiné 11:5; Szeli F./Fekete G. - Komócsin/Szeli I. 11:2; Torma/Máté-Szalai - Szabolcsi/Szabolcsiné 11:4; Szeli F./Fekete G. - Szabolcsi/Szabolcsiné 11:9; Komócsin/Szeli I. - Tarr/Tarrné 11:1; Szeli F./Fekete G. - Tarr/Tarrné 11:2; Komócsin/Szeli I. - Torma/Máté-Szalai 11:7.
  * B csoport: Czirják/Magyar D. - Püspök/Miszlai-Komócsin 11:2; Csende/Szabadits - Csatári/Szeli L. 11:7; Török/Rupf - Csatári/Szeli L. 11:4; Csende/Szabadits - Czirják/Magyar D. 11:4; Csatári/Szeli L. - Czirják/Magyar D. 11:1; Török/Rupf - Püspök/Miszlai-Komócsin 11:3; Török/Rupf - Czirják/Magyar D. 11:4; Csende/Szabadits - Püspök/Miszlai-Komócsin 11:2; Török/Rupf - Csende/Szabadits 11:6; Csatári/Szeli L. - Püspök/Miszlai-Komócsin 11:7.
  * C csoport: Magyar Cs./Horváth R. - Csigó/Sónyák 11:9; Polgár/Takács V. - Kétszeri/Kétszeriné 11:7; Tábori/Katona - Kétszeri/Kétszeriné 11:5; Polgár/Takács V. - Magyar Cs./Horváth R. 11:9; Tábori/Katona - Csigó/Sónyák 11:7; Magyar Cs./Horváth R. - Kétszeri/Kétszeriné 11:4; Tábori/Katona - Magyar Cs./Horváth R. 11:4; Ákos Sónyák / Nóra Csigó - Polgár/Takács V. 11:6; Tábori/Katona - Polgár/Takács V. 11:6; Ákos Sónyák / Nóra Csigó - Kétszeriné/Kétszeri 11:3.
  * D csoport: Hranyczka/Szeli L. - Kínál/Füles 11:2; Fekete K./Rédecsi - Mayer/Komócsin B-né 11:5; Fogaras/Takács F. - Mayer/Komócsin B-né 11:6; Fekete K./Rédecsi - Hranyczka/Szeli L. 11:4; Fogaras/Takács F. - Kínál/Füles 11:1; Mayer/Komócsin B-né - Hranyczka/Szeli L. 11:9; Fogaras/Takács F. - Hranyczka/Szeli L. 11:3; Fekete K./Rédecsi - Kínál/Füles 11:7; Fogaras/Takács F. - Fekete K./Rédecsi 11:6; Mayer/Komócsin B-né - Kínál/Füles 11:6.
- Vegyes páros OB2/B csoportmeccsek:
  * A csoport: Berta/Gyimesi-Varga - Fancsaliné/Torma L. 11:5; Petrovics/Schmidt - Fancsaliné/Torma L. 11:2; Petrovics/Schmidt - Berta/Gyimesi-Varga 12:10.
  * B csoport: Fekete B./Feketéné - Jagicza/Tran Van 11:2; Molnár R./Kecskés Amáta - Jagicza/Tran Van 11:2; Molnár R./Kecskés Amáta - Feketéné/Fekete B. 11:2.
  * C csoport: Máté A./Sipos - Füzi/Fekete Andrea 11:8; Németh E./Decsi - Takács Z./Hranyczka L-né 12:10; Máté A./Sipos - Hranyczka L-né/Takács Z. 11:2; Máté A./Sipos - Németh E./Decsi 11:2.
  * D csoport: Karda/Kecskés R. - Viszokai L./Viszokai V. 11:2; Soós/Brindza - Dávid Á./Steinwengerné 11:2; Karda/Kecskés R. - Dávid Á./Steinwengerné 11:6; Soós/Brindza - Viszokai L./Viszokai V. 16:14.

=== 4. HIVATALOS RÁJÁTSZÁS ÉS HELYOSZTÓ MÉRKŐZÉSEK EREDMÉNYEI ===
- NŐI PÁROS OB2/A:
  * Elődöntők: Szeli F./Rupf - Csigó/Horváth 11:3; Takács F./Tábori - Miszlai-Komócsin/Rédecsi 11:1.
  * Döntő: Fruzsina Szeli / Anna Rupf - Flóra Takács / Petra Tábori 11:5.
  * 3. helyért: Nóra Csigó / Eszter Horváth - Kinga Miszlai-Komócsin / Anna Rédecsi 11:5.
- NŐI PÁROS OB2/B:
  * Elődöntők: Jagicza/Mojzer - Komócsin L-né/Kétszeriné 12:10; Szabolcsiné/Kecskés - Brindza/Németh 12:10.
  * Döntő: Kata Jagicza / Katalin Mojzer - Katalin Szabolcsiné Morvai / Rita Kecskés 11:3.
  * 3. helyért: Gyöngyike Brindza / Eszter Németh - Balázsné Komócsin / Anita Kétszeriné Szűcs 11:0.
- VEGYES PÁROSOK OB2/A:
  * Negyeddöntők: Szeli F./Fekete G. - Csigó/Sónyák 11:3; Fogaras/Takács F. - Szabadits/Csende 11:3; Tábori/Katona - Szabolcsi/Szabolcsiné 11:4; Török/Rupf - Fekete K./Rédecsi 11:8.
  * Elődöntők: Szeli F./Fekete G. - Fogaras/Takács F. 11:7; Török/Rupf - Tábori/Katona 11:7.
  * Döntő: Fruzsina Szeli / Géza Fekete - Bence Török / Anna Rupf 11:3.
  * 3. helyért: Pál Fogaras / Flóra Takács - Petra Tábori / Milán Katona 11:8.
  * 5. helyért: Kristof Fekete / Anna Rédecsi - Eszter Szabadits / Zsolt Csende 11:8.
  * 7. helyért: Nóra Csigó / Ákos Sónyák - Attila Szabolcsi / Katalin Szabolcsiné Morvai 11:8.
- VEGYES PÁROSOK OB2/B:
  * Negyeddöntők: Berta/Gyimesi-Varga - Decsi/Németh E. 11:5; Jagicza/Tran Van - Karda/Kecskés R. 11:7; Schmidt/Petrovics - Máté A./Sipos 11:2; Molnár R./Kecskés Amáta - Soós/Brindza 11:3.
  * Elődöntők: Jagicza/Tran Van - Berta/Gyimesi-Varga 11:7; Molnár R./Kecskés Amáta - Schmidt/Petrovics 13:11.
  * Döntő: Kata Jagicza / Dat Tran Van - Róbert Molnár / Nóra Kecskés Amáta 11:7.
  * 3. helyért: Szabolcs Berta / Petra Gyimesi-Varga - Adam Anton Schmidt / Laura Petrovics 11:8.
- FIXÁLT SZOMBATI HELYOSZTÓ KORREKCIÓK:
  * 5. helyért: Csende Zsolt - Magyar Csanád 11:2 (frissítve a meccsnapló pontos állása szerint).

=== 5. HIVATALOS MÉRKŐZÉSNAP VÉGEREDMÉNYEK (DOBOGÓSOK) ===
1. Női egyéni OB2/A: 1. Takács Flóra, 2. Tábori Petra, 3. Rupf Anna.
2. Női egyéni OB2/B: 1. Sipos Anna, 2. Viszokai Viktória, 3. Szabolcsiné Morvai Katalin.
3. Férfi egyéni OB2/A: 1. Mayer Iván, 2. Tomori Benedek, 3. Török Bence.
4. Férfi páros OB2/A: 1. Dobos Ákos / Török Bence, 2. Szabolcsi Attila / Katona Milán, 3. Komáromi Róbert / Tomori Benedek.
5. Férfi egyéni OB2/B: 1. Mészáros Szerhij, 2. Dinnyés János, 3. Tóth András.
6. Férfi páros OB2/B: 1. Alasztics Benjamin / Németh Tamás, 2. Péntek Vilmos / Racz Robert, 3. Viszokai László / Molnár Róbert.
7. Női páros OB2/A: 1. Fruzsina Szeli / Anna Rupf, 2. Flóra Takács / Petra Tábori, 3. Nóra Csigó / Eszter Horváth.
8. Női páros OB2/B: 1. Kata Jagicza / Katalin Mojzer, 2. Katalin Szabolcsiné Morvai / Rita Kecskés, 3. Gyöngyike Brindza / Eszter Németh.
9. Vegyes páros OB2/A: 1. Fruzsina Szeli / Géza Fekete, 2. Bence Török / Anna Rupf, 3. Pál Fogaras / Flóra Takács.
10. Vegyes páros OB2/B: 1. Kata Jagicza / Dat Tran Van, 2. Róbert Molnár / Nóra Kecskés Amáta, 3. Szabolcs Berta / Petra Gyimesi-Varga.

=== 6. HIVATALOS HÉTVÉGI FOTÓK ÉS VIDEÓK ELÉRÉSI LINKJEI ===
- A vasárnapi eredményhirdetés videója: https://drive.google.com/file/d/1ir7T5Gyg1v9Hi74oXCt5hSulGNIC8gIl/view?usp=sharing
- A szombati eredményhirdetések képei: https://drive.google.com/drive/u/0/folders/1btewN9JCocdESGwm0D5gMKiYAoTOBDpb
- A vasárnapi eredményhirdetések képei: https://drive.google.com/drive/u/0/folders/1eA8GYR1ZfxWf38Vuf9_leZ7Wdg5nZOwI
- A szombati vágatlan meccsvideók: https://drive.google.com/drive/folders/1Nhd4uteCtM-bnJGwgX7fq_C58v1h7UtA
- A vasárnapi vágatlan meccsvideók: https://drive.google.com/drive/folders/1POj4Lqn9U3Hav0LIlCf132JXy-lMu13K?usp=sharing
"""

# 4. Rendszer-utasítások konfigurálása
SYSTEM_INSTRUCTION = f"""
Te egy profi Pickleball Versenybíró és Mentor vagy, aki most Sopronban tartózkodik az Országos Bajnokságon. A küldetésed a játékosok és látogatók maximális kiszolgálása.

A válaszadás során az alábbi prioritási és témakör-rendet kövesd:

1. SOPRONI VERSENYADATOK: Ha a kérdés a konkrét hétvégi soproni csoportmeccsekre vagy rájátszás eredményekre, egyedi pontszámokra, képekre, fotókra vagy videók elérésére vonatkozik, KIZÁRÓLAG az alábbi adatokból dolgozhatsz:
{VERSENY_KONTEXTUS}
Amennyiben a kérdés egy olyan konkrét soproni tornára vagy médiára vonatkozó adatra irányul, ami nincs benne a szövegben, mondd azt: "Erről nincs pontos információm a kiírásban, kérlek fordulj a versenybíróhoz!"

2. ÁLTALÁNOS PICKLEBALL TUDÁS: Ha a kérdés általános pickleball szabályra, kifejezésre, pontozásra, ütésfajtára vagy taktikára vonatkozik, használd a saját széleskörű pickleball szakértelmedet, és válaszolj rá részletesen és segítőkészen.

3. SOPRON VÁROSA ÉS SOPRON FEST: Ha a kérdés Sopron látnivalóira, éttermeire, helyi közlekedésére, vagy a most hétvégén zajló Sopron Fest zenei/kulturális fesztiválra, annak hangulatára, helyszínére vagy részletes napi programjaira vonatkozik, válaszolj bátran a Google Keresés segítségével! Segíts nekik naprakész fesztivál- és városi tippekkel.

4. SZIGORÚ TÉMAKORLÁT: Ha a kérdés egyáltalán NEM kapcsolódik a pickleballhoz, a soproni bajnoksághoz, Sopron városához vagy a Sopron Festhez, akkor NE válaszolj rá! Udvariasan, pici sportos humorral utasítsd vissza, és emlékeztesd a felhasználót, hogy ez az app kizárólag a Sopron Pickleball & Fesztivál hivatalos asszisztense.

Szabályok:
- Használj listákat és félkövér kiemeléseket a lényeges részeknél (időpontok, pályák, helyszínek) a könnyebb olvashatóságért!
- A stílusod legyen sportszerű, profi, de barátságos és közvetlen.
"""

# 5. Felhasználói felület és keresési logika ÉLŐ GOOGLE GROUNDING-AL
user_query = st.text_input("Mit szeretnél tudni? (pl. 'Ki nyerte a Vegyes páros OB2/B-t?', 'Hol érhetőek el a hétvégi vágatlan meccsvideók?', 'Ki lép fel ma este a Sopron Festen?')", "")

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

st.info("Tipp: Ha a saját menetrendedet vagy eredményedet keresed, pontosan úgy írd be a neved, ahogy a nevezési listában szerepel (pl. 'SIPOS ANNA').")