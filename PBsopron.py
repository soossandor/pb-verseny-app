import streamlit as st
from google import genai
from google.genai import types

# 1. Alapbeállítások és stílus (Mobilra optimalizálva)
st.set_page_config(page_title="Sopron Pickleball Asszisztens", page_icon="🏓", layout="centered")

st.title("🏓 Sopron Pickleball & Fesztivál Asszisztens")
st.write("Írd be a neved vagy a kérdésed! Kikeresem a menetrended, segítek a szabályokban, vagy adok élő tippeket **Sopron városával** and a **Sopron Festtel** kapcsolatban!")

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

# 3. A TELJES HÉTVÉGE HIVATALOS ADATBÁZISA (Kiterjesztett teljes nevekkel és auditált eredményekkel)
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
  * C csoport: Fogaras Pál - Behbahani Arman Ghalegolab 11:0; Tomori Benedek - Szabolcsi Attila 12:10; Szabolcsi Attila - Behbahani Arman Ghalegolab 11:3; Tomori Benedek - Fogaras Pál 11:4; Tomori Benedek - Behbahani Arman Ghalegolab 11:4; Fogaras Pál - Szabolcsi Attila 11:5.
  * D csoport: Takács Attila - Kínál Zoltán 11:6; Magyar Csanád - Schmidt Adam Anton 11:3; Csende Zsolt - Schmidt Adam Anton 11:8; Magyar Csanád - Takács Attila 11:6; Takács Attila - Schmidt Adam Anton 11:3; Csende Zsolt - Kínál Zoltán 13:11; Csende Zsolt - Takács Attila 11:4; Kínál Zoltán - Magyar Csanád 11:6; Csende Zsolt - Magyar Csanád 11:8; Kínál Zoltán - Schmidt Adam Anton 11:9.
- Férfi páros OB2/A csoportmeccsek:
  * A csoport: Behbahani Arman Ghalegolab / Csende Zsolt - Magyar Benedek / Magyar Dániel 11:3; Szabolcsi Attila / Katona Milán - Magyar Benedek / Magyar Dániel 11:7; Szabolcsi Attila / Katona Milán - Behbahani Arman Ghalegolab / Csende Zsolt 11:6.
  * B csoport: Takács Vince / Halápi Ákos - Szeli Lénárd / Kétszeri László 11:4; Dobos Ákos / Török Bence - Szeli Lénárd / Kétszeri László 11:3; Dobos Ákos / Török Bence - Takács Vince / Halápi Ákos 11:3.
  * C csoport: Tarr Sándor / Takács Attila - Magyar Csanád / Berky Péter 11:6; Komáromi Róbert / Tomori Benedek - Schnell Attila / Schnell Imre 11:6; Tarr Sándor / Takács Attila - Schnell Attila / Schnell Imre 11:2; Komáromi Róbert / Tomori Benedek - Magyar Csanád / Berky Péter 11:0; Komáromi Róbert / Tomori Benedek - Takács Attila / Tarr Sándor 11:4; Schnell Attila / Schnell Imre - Magyar Csanád / Berky Péter 11:5.
  * D csoport: Fogaras Pál / Fekete Géza - Püspök Patrik / Komócsin Balázs 11:0; Mayer Iván / Schmidt Adam Anton - Kínál Zoltán / Csernavay Endre 11:5; Fogaras Pál / Fekete Géza - Kínál Zoltán / Csernavay Endre 11:6; Mayer Iván / Schmidt Adam Anton - Komócsin Balázs / Püspök Patrik 11:2; Fogaras Pál / Fekete Géza - Mayer Iván / Schmidt Adam Anton 11:8; Kínál Zoltán / Csernavay Endre - Püspök Patrik / Komócsin Balázs 11:9.
- Férfi egyéni OB2/B csoportmeccsek:
  * A csoport: Dávid Ádám - Nagy Dávid 11:8; Magyar Dániel - Dávid Ádám 11:2; Magyar Dániel - Nagy Dávid 11:9.
  * B csoport: Mészáros Szerhij - Bruckner Nándor 11:3; Pawletko Peter - Mészáros Szerhij 11:9; Pawletko Peter - Bruckner Nándor 11:1.
  * C csoport: Dinnyés János - Tran Van Dat 11:3; Szeli Lénárd - Péntek Vilmos 11:9; Dinnyés János - Péntek Vilmos 11:3; Szeli Lénárd - Tran Van Dat 11:7; Dinnyés János - Szeli Lénárd 11:9; Péntek Vilmos - Tran Van Dat 11:2.
  * D csoport: Tóth András - Tomori Tamás 11:5; Racz Robert - Fekete Barnabás 11:0; Racz Robert - Tóth András 11:8; Tomori Tamás - Fekete Barnabás 11:5; Tóth András - Fekete Barnabás 11:2; Racz Robert - Tomori Tamás 11:0.
- Férfi páros OB2/B csoportmeccsek:
  * A csoport: Gulyás Nándor / Karda Zoltán - Bruckner Nándor / Füzi Benedek 11:2; Alasztics Benjamin / Németh Tamás - Karda Zoltán / Gulyás Nándor 11:3; Alasztics Benjamin / Németh Tamás - Bruckner Nándor / Füzi Benedek 11:2.
  * B csoport: Fekete Barnabás / Dávid Ádám - Decsi Gábor / Pál Barnabás 12:10; Fekete Barnabás / Dávid Ádám - Mészáros Szerhij / Fekete Kristóf 11:3; Fekete Kristóf / Mészáros Szerhij - Decsi Gábor / Pál Barnabás 11:1.
  * C csoport: Péntek Vilmos / Racz Robert - Kétszeri László / Szeli Lénárd 11:6; Pawletko Peter / Tóth András - Tan Minh Le / Tan Dung Le 11:6; Péntek Vilmos / Racz Robert - Tan Minh Le / Tan Dung Le 13:11; Pawletko Peter / Tóth András - Kétszeri László / Szeli Lénárd 11:1; Péntek Vilmos / Racz Robert - Pawletko Peter / Tóth András 11:0; Tan Minh Le / Tan Dung Le - Kétszeri László / Szeli Lénárd 11:0.
  * D csoport: Nagy Dávid / Dinnyés János - Németh Attila / Berta Szabolcs 11:4; Viszokai László / Molnár Róbert - Simon Zsolt / Soós Sándor 11:5; Viszokai László / Molnár Róbert - Németh Attila / Berta Szabolcs 11:7; Dinnyés János / Nagy Dávid - Simon Zsolt / Soós Sándor 11:5; Nagy Dávid / Dinnyés János - Viszokai László / Molnár Róbert 11:4; Berta Szabolcs / Németh Attila - Simon Zsolt / Soós Sándor 12:10.

=== 3. VASÁRNAPI CSOPORTMÉRKŐZÉSEK PONTOS SZÁMSZERŰ EREDMÉNYEI ===
- Női páros OB2/A csoportmeccsek:
  * A csoport: Szeli Fruzsina / Rupf Anna - Polgár Judit / Csatári Andrea 11:1; Kinga Miszlai-Komócsin / Anna Rédecsi - Máté-Szalai Melinda / Sipos Anna 12:10; Szeli Fruzsina / Rupf Anna - Máté-Szalai Melinda / Sipos Anna 11:7; Kinga Miszlai-Komócsin / Anna Rédecsi - Polgár Judit / Csatári Andrea 11:4; Szeli Fruzsina / Rupf Anna - Kinga Miszlai-Komócsin / Anna Rédecsi 11:4; Máté-Szalai Melinda / Sipos Anna - Csatári Andrea / Polgár Judit 12:10.
  * B csoport: Csigó Nóra / Horváth Eszter - Horváth Renáta / Lukács Kinga 11:6; Tábori Petra / Takács Flóra - Hranyczka Emma / Hranyczka Lászlóné 11:1; Tábori Petra / Takács Flóra - Horváth Renáta / Lukács Kinga 11:1; Hranyczka Emma / Hranyczka Lászlóné - Csigó Nóra / Horváth Eszter 11:7; Tábori Petra / Takács Flóra - Csigó Nóra / Horváth Eszter 11:5; Horváth Renáta / Lukács Kinga - Hranyczka Emma / Hranyczka Lászlóné 11:7.
- Női páros OB2/B csoportmeccsek:
  * A csoport: Jagicza Kata / Mojzer Katalin - Szabolcsiné Morvai Katalin / Kecskés Rita 11:6; Csillag Mariann / Fancsaliné Kotán Edit - Feketéné Gyulai Dóra / Fekete Andrea Rozália 11:1; Katalin Szabolcsiné Morvai / Rita Kecskés - Csillag Mariann / Fancsaliné Kotán Edit 11:9; Jagicza Kata / Mojzer Katalin - Feketéné Gyulai Dóra / Fekete Andrea Rozália 11:0; Jagicza Kata / Mojzer Katalin - Csillag Mariann / Fancsaliné Kotán Edit 11:0; Kecskés Rita / Szabolcsiné Morvai Katalin - Feketéné Gyulai Dóra / Fekete Andrea Rozália 11:0.
  * B csoport: Komócsin Balázsné / Kétszeriné Szűcs Anita - Gyimesi-Varga Petra / Rubint Erika 11:6; Petrovics Laura / Kecskés Amáta Nóra - Brindza Gyöngyike / Németh Eszter 11:1; Petrovics Laura / Kecskés Amáta Nóra - Rubint Erika / Gyimesi-Varga Petra 12:10; Brindza Gyöngyike / Németh Eszter - Komócsin Balázsné / Kétszeriné Szűcs Anita 11:5; Petrovics Laura / Kecskés Amáta Nóra - Komócsin Balázsné / Kétszeriné Szűcs Anita 11:4; Rubint Erika / Gyimesi-Varga Petra - Brindza Gyöngyike / Németh Eszter 11:8.
- Vegyes páros OB2/A csoportmeccsek:
  * A csoport: Tarr Sándor / Tarrné Kajtár Gabriella - Torma Tibor / Máté-Szalai Melinda 11:6; Szabolcsi Attila / Szabolcsiné Morvai Katalin - Komócsin Balázs / Szeli Ibolya 11:7; Szeli Fruzsina / Fekete Géza - Torma Tibor / Máté-Szalai Melinda 11:3; Tarr Sándor / Tarrné Kajtár Gabriella - Szabolcsi Attila / Szabolcsiné Morvai Katalin 11:5; Szeli Fruzsina / Fekete Géza - Komócsin Balázs / Szeli Ibolya 11:2; Torma Tibor / Máté-Szalai Melinda - Szabolcsi Attila / Szabolcsiné Morvai Katalin 11:4; Szeli Fruzsina / Fekete Géza - Szabolcsi Attila / Szabolcsiné Morvai Katalin 11:9; Komócsin Balázs / Szeli Ibolya - Tarr Sándor / Tarrné Kajtár Gabriella 11:1; Szeli Fruzsina / Fekete Géza - Tarr Sándor / Tarrné Kajtár Gabriella 11:2; Komócsin Balázs / Szeli Ibolya - Torma Tibor / Máté-Szalai Melinda 11:7.
  * B csoport: Czirják Anna / Magyar Dániel - Püspök Patrik / Miszlai-Komócsin Kinga 11:2; Csende Zsolt / Szabadits Eszter - Csatári Andrea / Szeli László 11:7; Török Bence / Rupf Anna - Csatári Andrea / Szeli László 11:4; Csende Zsolt / Szabadits Eszter - Czirják Anna / Magyar Dániel 11:4; Csatári Andrea / Szeli László - Czirják Anna / Magyar Dániel 11:1; Török Bence / Rupf Anna - Püspök Patrik / Miszlai-Komócsin Kinga 11:3; Török Bence / Rupf Anna - Czirják Anna / Magyar Dániel 11:4; Csende Zsolt / Szabadits Eszter - Püspök Patrik / Miszlai-Komócsin Kinga 11:2; Török Bence / Rupf Anna - Csende Zsolt / Szabadits Eszter 11:6; Csatári Andrea / Szeli László - Püspök Patrik / Miszlai-Komócsin Kinga 11:7.
  * C csoport: Magyar Csanád / Horváth Renáta - Csigó Nóra / Sónyák Ákos 11:9; Polgár Judit / Takács Vince - Kétszeri László / Kétszeriné Szűcs Anita 11:7; Tábori Petra / Katona Milán - Kétszeri László / Kétszeriné Szűcs Anita 11:5; Polgár Judit / Takács Vince - Magyar Csanád / Horváth Renáta 11:9; Tábori Petra / Katona Milán - Csigó Nóra / Sónyák Ákos 11:7; Magyar Csanád / Horváth Renáta - Kétszeri László / Kétszeriné Szűcs Anita 11:4; Tábori Petra / Katona Milán - Magyar Csanád / Horváth Renáta 11:4; Ákos Sónyák / Nóra Csigó - Polgár Judit / Takács Vince 11:6; Tábori Petra / Katona Milán - Polgár Judit / Takács Vince 11:6; Ákos Sónyák / Nóra Csigó - Kétszeriné Szűcs Anita / Kétszeri László 11:3.
  * D csoport: Hranyczka Emma / Szeli Lénárd - Kínál Zoltán / Füles Mónika 11:2; Fekete Kristóf / Rédecsi Anna - Mayer Iván / Komócsin Balázsné 11:5; Fogaras Pál / Takács Flóra - Mayer Iván / Komócsin Balázsné 11:6; Fekete Kristóf / Rédecsi Anna - Hranyczka Emma / Szeli Lénárd 11:4; Fogaras Pál / Takács Flóra - Kínál Zoltán / Füles Mónika 11:1; Mayer Iván / Komócsin Balázsné - Hranyczka Emma / Szeli Lénárd 11:9; Fogaras Pál / Takács Flóra - Hranyczka Emma / Szeli Lénárd 11:3; Fekete Kristóf / Rédecsi Anna - Kínál Zoltán / Füles Mónika 11:7; Fogaras Pál / Takács Flóra - Fekete Kristóf / Rédecsi Anna 11:6; Mayer Iván / Komócsin Balázsné - Kínál Zoltán / Füles Mónika 11:6.
- Vegyes páros OB2/B csoportmeccsek:
  * A csoport: Berta Szabolcs / Gyimesi-Varga Petra - Fancsaliné Kotán Edit / Torma László 11:5; Petrovics Laura / Schmidt Adam Anton - Fancsaliné Kotán Edit / Torma László 11:2; Petrovics Laura / Schmidt Adam Anton - Berta Szabolcs / Gyimesi-Varga Petra 12:10.
  * B csoport: Fekete Barnabás / Feketéné Gyulai Dóra - Jagicza Kata / Tran Van Dat 11:2; Molnár Róbert / Kecskés Amáta Nóra - Jagicza Kata / Tran Van Dat 11:2; Molnár Róbert / Kecskés Amáta Nóra - Feketéné Gyulai Dóra / Fekete Barnabás 11:2.
  * C csoport: Máté Attila / Sipos Anna - Füzi Benedek / Fekete Andrea Rozália 11:8; Németh Eszter / Decsi Gábor - Takács Zsolt / Hranyczka Lászlóné 12:10; Máté Attila / Sipos Anna - Hranyczka Lászlóné / Takács Zsolt 11:2; Máté Attila / Sipos Anna - Németh Eszter / Decsi Gábor 11:2.
  * D csoport: Karda Zoltán / Kecskés Rita - Viszokai László / Viszokai Viktória 11:2; Soós Sándor / Brindza Gyöngyike - Dávid Ádám / Steinwengerné Lugosi Katalin 11:2; Karda Zoltán / Kecskés Rita - Dávid Ádám / Steinwengerné Lugosi Katalin 11:6; Soós Sándor / Brindza Gyöngyike - Viszokai László / Viszokai Viktória 16:14.

=== 4. HIVATALOS RÁJÁTSZÁS ÉS HELYOSZTÓ MÉRKŐZÉSEK EREDMÉNYEI ===
- NŐI PÁROS OB2/A:
  * Elődöntők: Szeli Fruzsina / Rupf Anna - Csigó Nóra / Horváth Eszter 11:3; Takács Flóra / Tábori Petra - Kinga Miszlai-Komócsin / Anna Rédecsi 11:1.
  * Döntő: Fruzsina Szeli / Anna Rupf - Flóra Takács / Petra Tábori 11:5.
  * 3. helyért: Nóra Csigó / Eszter Horváth - Kinga Miszlai-Komócsin / Anna Rédecsi 11:5.
- NŐI PÁROS OB2/B:
  * Elődöntők: Jagicza Kata / Mojzer Katalin - Komócsin Balázsné / Kétszeriné Szűcs Anita 12:10; Szabolcsiné Morvai Katalin / Kecskés Rita - Brindza Gyöngyike / Németh Eszter 12:10.
  * Döntő: Kata Jagicza / Katalin Mojzer - Katalin Szabolcsiné Morvai / Rita Kecskés 11:3.
  * 3. helyért: Gyöngyike Brindza / Eszter Németh - Balázsné Komócsin / Anita Kétszeriné Szűcs 11:0.
- VEGYES PÁROSOK OB2/A:
  * Negyeddöntők: Szeli Fruzsina / Fekete Géza - Csigó Nóra / Sónyák Ákos 11:3; Fogaras Pál / Takács Flóra - Szabadits Eszter / Csende Zsolt 11:3; Tábori Petra / Katona Milán - Szabolcsi Attila / Szabolcsiné Morvai Katalin 11:4; Török Bence / Rupf Anna - Fekete Kristóf / Rédecsi Anna 11:8.
  * Elődöntők: Szeli Fruzsina / Fekete Géza - Fogaras Pál / Takács Flóra 11:7; Török Bence / Rupf Anna - Tábori Petra / Katona Milán 11:7.
  * Döntő: Fruzsina Szeli / Géza Fekete - Bence Török / Anna Rupf 11:3.
  * 3. helyért: Pál Fogaras / Flóra Takács - Petra Tábori / Milán Katona 11:8.
  * 5. helyért: Kristof Fekete / Anna Rédecsi - Eszter Szabadits / Zsolt Csende 11:8.
  * 7. helyért: Nóra Csigó / Ákos Sónyák - Attila Szabolcsi / Katalin Szabolcsiné Morvai 11:8.
- VEGYES PÁROSOK OB2/B:
  * Negyeddöntők: Berta Szabolcs / Gyimesi-Varga Petra - Decsi Gábor / Németh Eszter 11:5; Jagicza Kata / Tran Van Dat - Karda Zoltán / Kecskés Rita 11:7; Schmidt Adam Anton / Laura Petrovics - Máté Attila / Sipos Anna 11:2; Molnár Róbert / Kecskés Amáta Nóra - Soós Sándor / Brindza Gyöngyike 11:3.
  * Elődöntők: Jagicza Kata / Tran Van Dat - Berta Szabolcs / Gyimesi-Varga Petra 11:7; Molnár Róbert / Kecskés Amáta Nóra - Schmidt Adam Anton / Laura Petrovics 13:11.
  * Döntő: Kata Jagicza / Dat Tran Van - Róbert Molnár / Nóra Kecskés Amáta 11:7.
  * 3. helyért: Szabolcs Berta / Petra Gyimesi-Varga - Adam Anton Schmidt / Laura Petrovics 11:8.
  * 7. helyért: Karda Zoltán / Kecskés Rita - Soós Sándor / Brindza Gyöngyike 11:3.
- FIXÁLT SZOMBATI HELYOSZTÓ KORREKCIÓK:
  * 5. helyért: Csende Zsolt - Magyar Csanád 11:2 (frissítve a meccsnapló pontos állása szerint).
  * 13. helyért (Férfi páros OB2/B): Lénárd Szeli / Dániel Kétszeri - Sándor Soós / Zsolt Simon 11:1.

=== 5. HIVATALOS MÉRKŐZÉSNAP VÉGEREDMÉNYEK (DOBOGÓSOK) ===
1. Női egyéni OB2/A: 1. Takács Flóra, 2. Tábori Petra, 3. Rupf Anna.
2. Női egyéni OB2/B: 1. Sipos Anna, 2. Viszokai Viktória, 3. Szabolcsiné Morvai Katalin.
3. Férfi egyéni OB2/A: 1. Mayer Iván, 2. Tomori Benedek, 3. Török Bence.
4. Férfi páros OB2/A: 1. Dobos Ákos / Török Bence, 2. Szabolcsi Attila / Katona Milán, 3. Komáromi Róbert / Tomori Benedek.
5. Férfi egyéni OB2/B: 1. Mészáros Szerhij, 2. Dinnyés János, 3. Szeli Lénárd.
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

2. ÁLTALÁNOS PICKLEBALL TUDÁS: Ha a kérdés általános pickleball szabályra, kifejezésre, pontozásra, ütésfajtára vagy taktikára vonatkozik, használd a saját széleskörű pickleball szakértelmedet, and válaszolj rá részletesen és segítőkészen.

3. SOPRON VÁROSA ÉS SOPRON FEST: Ha a kérdés Sopron látnivalóira, éttermeire, helyi közlekedésére, vagy a most hétvégén zajló Sopron Fest zenei/kulturális fesztiválra, annak hangulatára, helyszínére vagy részletes napi programjaira vonatkozik, használd bátran a Google Keresés segítségével! Segíts nekik naprakész fesztivál- és városi tippekkel.

4. SZIGORÚ TÉMAKORLÁT: Ha a kérdés egyáltalán NEM kapcsolódik a pickleballhoz, a soproni bajnoksághoz, Sopron városához vagy a Sopron Festhez, akkor NE válaszolj rá! Udvariasan, pici sportos humorral utasítsd vissza, and emlékeztesd a felhasználót, hogy ez az app kizárólag a Sopron Pickleball & Fesztivál hivatalos asszisztense.

Szabályok:
- Használj listákat and félkövér kiemeléseket a lényeges részeknél (időpontok, pályák, helyszínek) a könnyebb olvashatóságért!
- A stílusod legyen sportszerű, profi, de barátságos and közvetlen.
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