import streamlit as st
import google.generativeai as genai

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

# 3. A VERSENY FIX ADATBÁZISA
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
- Óvás: Csak a verseny ideje alatt, írásban, 10.000 Ft óvási díj megfizetésével nyújtható be a versenyző által. Elfogadás esetén visszajár.

=== 2. CSOPORTKÖRÖK ÉS LEBONYOLÍTÁSI REND ===
A csoportok rangsorolása: 1. Több győzelem, 2. Egymás ellen elért eredmény (ha 2 holtverseny van), 3. Pontarány (szerzett/vesztett pontok), 4. Egymás elleni mérkőzés.

Kategóriák továbbjutási rendje:
- Női egyéni OB2/A (7 fő: 1x3 + 1x4 csoport): Főág (1-4. hely): A1-B2, B1-A2. Mellékág (5-7. hely): A3-B4, B3-BYE.
- Női egyéni OB2/B (4 fő: 1x4): Teljes körmérkőzés, nincs egyenes kiesés.
- Női páros OB2/A és OB2/B (8-8 pár: 2x4 csoport): Főág (1-4. hely): A1-B2, B1-A2. Mellékág (5-8. hely): A3-B4, B3-A4.
- Férfi egyéni OB2/A (17 fő: 3x4 + 1x5 csoport): Főág negyeddöntő (1-8. hely): A1-C2, B2-D1, C1-A2, D2-B1. Mellékág (9-12. hely): A3-C3, B3-D3. Vigaszág (13-16. hely): A4-C4, B4-D4. D csoport 5. helyezettje automatikusan 17..
- Férfi egyéni OB2/B, Férfi páros OB2/A, Férfi páros OB2/B, Vegyes páros OB2/B (14-14 induló: 2x3 + 2x4 csoport): Főág QF (1-8. hely): A1-C2, B2-D1, C1-A2, D2-B1. Mellékág (9-12. hely): A3-C3, B3-D3. Helyosztó (13-14. hely): C4-D4.
- Vegyes páros OB2/A (20 pár: 4x5 csoport): Főág QF (1-8. hely): A1-C2, B2-D1, C1-A2, D2-B1. Mellékág 1 (9-12. hely): A3-C3, B3-D3. Mellékág 2 (13-16. hely): A4-C4, B4-D4. Vigaszág (17-20. hely): A5-C5, B5-D5.

=== 3. SZOMBATI MENETREND (2026.07.04.) ===
M1 KÖR (08:00):
- Court 1: A. TAKÁCS / S. TARR vs. C. MAGYAR / P. BERKY (Férfi páros OB2/A - Group C-R1)
- Court 2: B. TOMORI / R. KOMAROMI vs. A. SCHNELL / I. SCHNELL (Férfi páros OB2/A - Group C-R1)
- Court 3: P. FOGARAS / G. FEKETE vs. P. PÜSPÖK / B. KOMOCSIN (Férfi páros OB2/A - Group D-R1)
- Court 4: A. SCHMIDT / I. MAYER vs. Z. KINÁL / C. ENDRE (Férfi páros OB2/A - Group D-R1)
- Court 5: R. RACZ / V. PÉNTEK vs. L. SZELI / D. KÉTSZERI (Férfi páros OB2/B - Group C-R1)
- Court 6: A. TOTH / P. PAWLETKO vs. T. LE / T. LE (Férfi páros OB2/B - Group C-R1)
- Court 7: A. NÉMETH / S. BERTA vs. D. NAGY / J. DINNYÉS (Férfi páros OB2/B - Group D-R1)
- Court 8: S. SOÓS / Z. SIMON vs. L. VISZOKAI / R. MOLNÁR (Férfi páros OB2/B - Group D-R1)

M2 KÖR (08:20):
- Court 1: B. ARMAN GHALEGOLAB / Z. CSENDE vs. D. MAGYAR / B. MAGYAR (Férfi páros OB2/A - Group A-R1)
- Court 2: V. TAKÁCS / Á. HALÁPI vs. L. KÉTSZERI / L. SZELI (Férfi páros OB2/A - Group B-R1)
- Court 3: G. FEKETE / P. FOGARAS vs. Z. KINÁL / C. ENDRE (Férfi páros OB2/A - Group D-R2)
- Court 4: P. PÜSPÖK / B. KOMÓCSIN vs. I. MAYER / A. SCHMIDT (Férfi páros OB2/A - Group D-R2)
- Court 5: B. FÜZI / N. BRUCKNER vs. Z. KARDA / N. GULYÁS (Férfi páros OB2/B - Group A-R1)
- Court 6: G. DECSI / B. PÅL vs. Á. DÁVID / B. FEKETE (Férfi páros OB2/B - Group B-R1)
- Court 7: S. BERTA / A. NÉMETH vs. L. VISZOKAI / R. MOLNÁR (Férfi páros OB2/B - Group D-R2)
- Court 8: J. DINNYÉS / D. NAGY vs. S. SOÓS / Z. SIMON (Férfi páros OB2/B - Group D-R2)

M3 KÖR (08:40):
- Court 1: M. KATONA / A. SZABOLCSI vs. D. MAGYAR / B. MAGYAR (Férfi páros OB2/A - Group A-R2)
- Court 2: A. DOBOS / B. TÖRÖK vs. L. KÉTSZERI / L. SZELI (Férfi páros OB2/A - Group B-R2)
- Court 3: A. TAKÁCS / S. TARR vs. A. SCHNELL / I. SCHNELL (Férfi páros OB2/A - Group C-R2)
- Court 4: P. BERKY / C. MAGYAR vs. R. KOMAROMI / B. TOMORI (Férfi páros OB2/A - Group C-R2)
- Court 5: T. NÉMETH / B. ALASZTICS vs. Z. KARDA / N. GULYÁS (Férfi páros OB2/B - Group A-R2)
- Court 6: K. FEKETE / S. MÉSZÁROS vs. Á. DÁVID / B. FEKETE (Férfi páros OB2/B - Group B-R2)
- Court 7: T. LE / T. LE vs. R. RACZ / V. PÉNTEK (Férfi páros OB2/B - Group C-R2)
- Court 8: P. PAWLETKO / A. TÓTH vs. D. KÉTSZERI / L. SZELI (Férfi páros OB2/B - Group C-R2)

M4 KÖR (09:00):
- Court 1: A. SZABOLCSI / M. KATONA vs. B. ARMAN GHALEGOLAB / Z. CSENDE (Férfi páros OB2/A - Group A-R3)
- Court 2: B. TÖRÖK / Á. DOBOS vs. V. TAKÁCS / Á. HALÁPI (Férfi páros OB2/A - Group B-R3)
- Court 3: G. FEKETE / P. FOGARAS vs. I. MAYER / A. SCHMIDT (Férfi páros OB2/A - Group D-R3)
- Court 4: C. ENDRE / Z. KINÁL vs. P. PÜSPÖK / B. KOMÓCSIN (Férfi páros OB2/A - Group D-R3)
- Court 5: T. NÉMETH / B. ALASZTICS vs. B. FÜZI / N. BRUCKNER (Férfi páros OB2/B - Group A-R3)
- Court 6: K. FEKETE / S. MÉSZÁROS vs. B. PAL / G. DECSI (Férfi páros OB2/B - Group B-R3)
- Court 7: R. MOLNÁR / L. VISZOKAI vs. D. NAGY / J. DINNYÉS (Férfi páros OB2/B - Group D-R3)
- Court 8: S. BERTA / A. NÉMETH vs. S. SOÓS / Z. SIMON (Férfi páros OB2/B - Group D-R3)

M5 KÖRÖK ÉS EGYÉNES KIESÉS KEZDETE (09:20 / 09:40):
- 09:20 C3: A. TAKÁCS / S. TARR vs. B. TOMORI / R. KOMAROMI (Férfi páros OB2/A - Group C-R3)
- 09:20 C4: A. SCHNELL / I. SCHNELL vs. C. MAGYAR / P. BERKY (Férfi páros OB2/A - Group C-R3)
- 09:20 C7: P. PAWLETKO / A. TÓTH vs. V. PÉNTEK / R. RACZ (Férfi páros OB2/B - Group C-R3)
- 09:20 C8: D. KÉTSZERI / L. SZELI vs. T. LE / T. LE (Férfi páros OB2/B - Group C-R3)
- 09:40-től: Férfi páros OB2/A és OB2/B Főági Negyeddöntők (Main QF) az 1-8. helyért.

DÉLUTÁNI EGYÉNI MÉRKŐZÉSEK (SZOMBAT):
- 11:00 C2: A. RÉDECSI vs. P. TÁBORI (Női egyéni OB2/A - Group A-R1)
- 11:00 C3: E. SZABADITS vs. R. KECSKÉS (Női egyéni OB2/A - Group B-R1)
- 11:00 C4: F. TAKÁCS vs. Á. HORVÁTH (Női egyéni OB2/A - Group B-R1)
- 11:20 C2: A. RUPF vs. P. TÁBORI (Női egyéni OB2/A - Group A-R2)
- 11:20 C3: R. KECSKÉS vs. Á. HORVÁTH (Női egyéni OB2/A - Group B-R2)
- 11:20 C4: E. SZABADITS vs. F. TAKÁCS (Női egyéni OB2/A - Group B-R2)
- 11:20 C6: A. SIPOS vs. D. FEKETÉNÉ GYULAI (Női egyéni OB2/B - R1)
- 11:20 C7: K. SZABOLCSINÉ MORVAI vs. V. VISZOKAI (Női egyéni OB2/B - R1)
- 11:40 C2: A. RUPF vs. A. RÉDECSI (Női egyéni OB2/A - Group A-R3)
- 11:40 C3: E. SZABADITS vs. F. TAKÁCS (Női egyéni OB2/A - Group B-R3)
- 11:40 C4: Á. HORVÁTH vs. R. KECSKÉS (Női egyéni OB2/A - Group B-R3)
- 11:40 C6: A. SIPOS vs. V. VISZOKAI (Női egyéni OB2/B - R2)
- 11:40 C7: D. FEKETÉNÉ GYULAI vs. K. SZABOLCSINÉ MORVAI (Női egyéni OB2/B - R2)
- 12:00 C6: A. SIPOS vs. K. SZABOLCSINÉ MORVAI (Női egyéni OB2/B - R3)
- 12:00 C7: V. VISZOKAI vs. D. FEKETÉNÉ GYULAI (Női egyéni OB2/B - R3)

FÉRFI EGYÉNI INDULÁSOK (SZOMBAT KORADÉLUTÁN):
- 12:20 C5: J. DINNYÉS vs. D. TRAN VAN (Férfi egyéni OB2/B - Group C-R1)
- 12:20 C6: L. SZELI vs. V. PÉNTEK (Férfi egyéni OB2/B - Group C-R1)
- 12:20 C7: A. TÓTH vs. T. TOMORI (Férfi egyéni OB2/B - Group D-R1)
- 12:20 C8: B. FEKETE vs. R. RACZ (Férfi egyéni OB2/B - Group D-R1)
- 12:40 C1: I. MAYER vs. P. BERKY (Férfi egyéni OB2/A - Group A-R1)
- 12:40 C2: B. MAGYAR vs. G. FEKETE (Férfi egyéni OB2/A - Group A-R1)
- 12:40 C3: A. TAKÁCS vs. Z. KINÁL (Férfi egyéni OB2/A - Group D-R1)
- 12:40 C4: C. MAGYAR vs. A. SCHMIDT (Férfi egyéni OB2/A - Group D-R1)
- 12:40 C5: D. NAGY vs. Á. DÁVID (Férfi egyéni OB2/B - Group A-R1)
- 12:40 C6: N. BRUCKNER vs. S. MÉSZÁROS (Férfi egyéni OB2/B - Group B-R1)
- 12:40 C7: A. TÓTH vs. R. RACZ (Férfi egyéni OB2/B - Group D-R2)
- 12:40 C8: T. TOMORI vs. B. FEKETE (Férfi egyéni OB2/B - Group D-R2)
- 13:00 C1: M. KATONA vs. B. ALASZTICS (Férfi egyéni OB2/A - Group B-R1)
- 13:00 C2: B. TÖRÖK vs. V. TAKÁCS (Férfi egyéni OB2/A - Group B-R1)
- 13:00 C3: Z. CSENDE vs. A. SCHMIDT (Férfi egyéni OB2/A - Group D-R2)
- 13:00 C4: C. MAGYAR vs. A. TAKÁCS (Férfi egyéni OB2/A - Group D-R2)
- 13:00 C5: D. MAGYAR vs. Á. DÁVID (Férfi egyéni OB2/B - Group A-R2)
- 13:00 C6: P. PAWLETKO vs. S. MÉSZÁROS (Férfi egyéni OB2/B - Group B-R2)
- 13:00 C7: J. DINNYÉS vs. V. PÉNTEK (Férfi egyéni OB2/B - Group C-R2)
- 13:00 C8: D. TRAN VAN vs. L. SZELI (Férfi egyéni OB2/B - Group C-R2)
- 13:20 C1: I. MAYER vs. G. FEKETE (Férfi egyéni OB2/A - Group A-R2)
- 13:20 C2: P. BERKY vs. B. MAGYAR (Férfi egyéni OB2/A - Group A-R2)
- 13:20 C3: P. FOGARAS vs. B. ARMAN GHALEGOLAB (Férfi egyéni OB2/A - Group C-R1)
- 13:20 C4: A. SZABOLCSI vs. B. TOMORI (Férfi egyéni OB2/A - Group C-R1)
- 13:20 C5: D. MAGYAR vs. D. NAGY (Férfi egyéni OB2/B - Group A-R3)
- 13:20 C6: P. PAWLETKO vs. N. BRUCKNER (Férfi egyéni OB2/B - Group B-R3)
- 13:20 C7: A. TÓTH vs. B. FEKETE (Férfi egyéni OB2/B - Group D-R3)
- 13:20 C8: R. RACZ vs. T. TOMORI (Férfi egyéni OB2/B - Group D-R3)
- 13:40 C1: V. TAKÁCS vs. M. KATONA (Férfi egyéni OB2/A - Group B-R2)
- 13:40 C2: B. TÖRÖK vs. B. ALASZTICS (Férfi egyéni OB2/A - Group B-R2)
- 13:40 C3: A. SCHMIDT vs. A. TAKÁCS (Férfi egyéni OB2/A - Group D-R3)
- 13:40 C4: Z. CSENDE vs. Z. KINÁL (Férfi egyéni OB2/A - Group D-R3)
- 13:40 C7: J. DINNYÉS vs. L. SZELI (Férfi egyéni OB2/B - Group C-R3)
- 13:40 C8: V. PÉNTEK vs. D. TRAN VAN (Férfi egyéni OB2/B - Group C-R3)
- 14:00 C1: I. MAYER vs. B. MAGYAR (Férfi egyéni OB2/A - Group A-R3)
- 14:00 C2: G. FEKETE vs. P. BERKY (Férfi egyéni OB2/A - Group A-R3)
- 14:00 C3: A. SZABOLCSI vs. B. ARMAN GHALEGOLAB (Férfi egyéni OB2/A - Group C-R2)
- 14:00 C4: B. TOMORI vs. P. FOGARAS (Férfi egyéni OB2/A - Group C-R2)
- 14:20 C1: B. TÖRÖK vs. M. KATONA (Férfi egyéni OB2/A - Group B-R3)
- 14:20 C2: B. ALASZTICS vs. V. TAKÁCS (Férfi egyéni OB2/A - Group B-R3)
- 14:20 C3: Z. CSENDE vs. A. TAKÁCS (Férfi egyéni OB2/A - Group D-R4)
- 14:20 C4: Z. KINÁL vs. C. MAGYAR (Férfi egyéni OB2/A - Group D-R4)
- 14:40 C1: B. ARMAN GHALEGOLAB vs. B. TOMORI (Férfi egyéni OB2/A - Group C-R3)
- 14:40 C2: A. SZABOLCSI vs. P. FOGARAS (Férfi egyéni OB2/A - Group C-R3)
- 14:40 C3: Z. CSENDE vs. C. MAGYAR (Férfi egyéni OB2/A - Group D-R5)
- 14:40 C4: Z. KINÁL vs. A. SCHMIDT (Férfi egyéni OB2/A - Group D-R5)

15:00-tól szombat késő délutánig: Férfi egyéni OB2/A és OB2/B egyenes kieséses szakaszok (Main QF, SF, döntők és helyosztók).

=== 4. VASÁRNAPI MENETREND (2026.07.05.) ===
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
- 09:40 C1: S. TARR / G. TARRNÉ KAJTÁR vs. M. MÁTÉ-SZALAI / T. TORMA (Vegyes páros OB2/A - Group A-R1)
- 09:40 C2: S. BERTA / G. PETRA vs. E. FANCSALINÉ KOTÁN / L. TORMA (Vegyes páros OB2/B - Group A-R1)
- 09:40 C3/4: B. FEKETE / D. FEKETÉNÉ GYULAI vs. K. JAGICZA / D. TRAN VAN (Vegyes páros OB2/B - Group B-R1); A. SIPOS / A. MÁTÉ vs. R. FEKETE ANDREA / B. FÜZI (Vegyes páros OB2/B - Group C-R1)
- 09:40 C5/6: E. NÉMETH / G. DECSI vs. L. HRANYCZKA / Z. TAKÁCS (Vegyes páros OB2/B - Group C-R1); C. MAGYAR / R. HORVÁTH vs. Á. SÓNYÁK / N. CSIGÓ (Vegyes páros OB2/A - Group C-R1)
- 09:40 C7: A. DAVID / K. STEINWENGERNÉ LUGOSI vs. V. VISZOKAI / L. VISZOKAI (Vegyes páros OB2/B - Group D-R1)
- 09:40 C8: R. KECSKÉS / Z. KARDA vs. S. SOÓS / G. BRINDZA (Vegyes páros OB2/B - Group D-R1)

- 10:00 C2: L. PETROVICS / A. SCHMIDT vs. E. FANCSALINÉ KOTÁN / L. TORMA (Vegyes páros OB2/B - Group A-R2)
- 10:00 C3/4: A. MÁTÉ / A. SIPOS vs. E. NÉMETH / G. DECSI; P. TÁBORI / M. KATONA vs. L. KÉTSZERI / A. KÉTSZERINÉ SZŰCS; N. KECSKÉS AMÁTA / R. MOLNÁR vs. L. HRANYCZKA / Z. TAKÁCS; B. FÜZI / R. FEKETE ANDREA vs. K. JAGICZA / D. TRAN VAN (Mérkőzések a Vegyes páros OB2/A és OB2/B csoportjaiból).
- 10:00 C7: Z. KARDA / R. KECSKÉS vs. V. VISZOKAI / L. VISZOKAI (Vegyes páros OB2/B - Group D-R2)
- 10:00 C8: S. SOÓS / G. BRINDZA vs. K. STEINWENGERNÉ LUGOSI / Á. DÁVID (Vegyes páros OB2/B - Group D-R2)

- 10:20 C2: A. SCHMIDT / L. PETROVICS vs. G. PETRA / S. BERTA (Vegyes páros OB2/B - Group A-R3)
- 10:20 C3/4: A. SIPOS / A. MÁTÉ vs. E. NÉMETH / G. DECSI; R. MOLNÁR / N. KECSKÉS AMÁTA vs. B. FEKETE / D. FEKETÉNÉ GYULAI
- 10:20 C5/6: M. KATONA / P. TÁBORI vs. N. CSIGÓ / Á. SÓNYÁK; Z. TAKÁCS / L. HRANYCZKA vs. B. FÜZI / R. FEKETE ANDREA
- 10:20 C7: R. KECSKÉS / Z. KARDA vs. Á. DÁVID / K. STEINWENGERNÉ LUGOSI
- 10:20 C8: L. VISZOKAI / V. VISZOKAI vs. G. BRINDZA / S. SOÓS

- 11:40 C2: A. SZABOLCSI / K. SZABOLCSINÉ MORVAI vs. B. KOMÓCSIN / L. SZELI (Vegyes páros OB2/A - Group A-R1)
- 11:40 C3: D. MAGYAR / A. CZIRJÁK vs. P. PÜSPÖK / K. MISZLAI-KOMÓCSIN (Vegyes páros OB2/A - Group B-R1)
- 11:40 C4: Z. CSENDE / E. SZABADITS vs. A. CSATÁRI / L. SZELI (Vegyes páros OB2/A - Group B-R1)
- 11:40 C6: V. TAKÁCS / J. POLGÁR vs. L. KÉTSZERI / A. KÉTSZERINÉ SZŰCS (Vegyes páros OB2/A - Group C-R1)
- 11:40 C7: E. HRANYCZKA / L. SZELI vs. M. FÜLES / Z. KINÁL (Vegyes páros OB2/A - Group D-R1)
- 11:40 C8: K. FEKETE / A. RÉDECSI vs. E. HRANYCZKA / L. SZELI (Vegyes páros OB2/A - Group D-R2)

- 12:00 C1: G. FEKETE / F. SZELI vs. T. TORMA / M. MÁTÉ-SZALAI (Vegyes páros OB2/A - Group A-R2)
- 12:00 C2: G. TARRNÉ KAJTÁR / S. TARR vs. A. SZABOLCSI / K. SZABOLCSINÉ MORVAI (Vegyes páros OB2/A - Group A-R2)
- 12:00 C3: A. RUPF / B. TÖRÖK vs. L. SZELI / A. CSATÁRI (Vegyes páros OB2/A - Group B-R2)
- 12:00 C4: Z. CSENDE / E. SZABADITS vs. D. MAGYAR / A. CZIRJÁK (Vegyes páros OB2/A - Group B-R2)
- 12:00 C6: V. TAKÁCS / J. POLGÁR vs. R. HORVÁTH / C. MAGYAR (Vegyes páros OB2/A - Group C-R2)
- 12:00 C7: F. TAKÁCS / P. FOGARAS vs. B. KOMÓCSIN / I. MAYER (Vegyes páros OB2/A - Group D-R2)

- 12:20 C1: G. FEKETE / F. SZELI vs. B. KOMÓCSIN / I. SZELI (Vegyes páros OB2/A - Group A-R3)
- 12:20 C2: T. TORMA / M. MÁTÉ-SZALAI vs. A. SZABOLCSI / K. SZABOLCSINÉ MORVAI (Vegyes páros OB2/A - Group A-R3)
- 12:20 C3: A. CSATÁRI / L. SZELI vs. A. CZIRJÁK / D. MAGYAR (Vegyes páros OB2/A - Group B-R3)
- 12:20 C4: B. TÖRÖK / A. RUPF vs. P. PÜSPÖK / K. MISZLAI-KOMÓCSIN (Vegyes páros OB2/A - Group B-R3)
- 12:20 C5: L. KÉTSZERI / A. KÉTSZERINÉ SZŰCS vs. R. HORVÁTH / C. MAGYAR (Vegyes páros OB2/A - Group C-R3)
- 12:20 C6: F. TAKÁCS / P. FOGARAS vs. M. FÜLES / Z. KINÁL (Vegyes páros OB2/A - Group D-R3)
- 12:20 C8: I. MAYER / B. KOMÓCSIN vs. L. SZELI / E. HRANYCZKA (Vegyes páros OB2/A - Group D-R3)

- 12:40 C1: F. SZELI / G. FEKETE vs. A. SZABOLCSI / K. SZABOLCSINÉ MORVAI (Vegyes páros OB2/A - Group A-R4)
- 12:40 C2: I. SZELI / B. KOMÓCSIN vs. G. TARRNÉ KAJTÁR / S. TARR (Vegyes páros OB2/A - Group A-R4)
- 12:40 C3: A. RUPF / B. TÖRÖK vs. D. MAGYAR / A. CZIRJÁK (Vegyes páros OB2/A - Group B-R4)
- 12:40 C4: K. MISZLAI-KOMÓCSIN / P. PÜSPÖK vs. E. SZABADITS / Z. CSENDE (Vegyes páros OB2/A - Group B-R4)
- 12:40 C5: A. SÓNYÁK / N. CSIGÓ vs. V. TAKÁCS / J. POLGÁR (Vegyes páros OB2/A - Group C-R4)
- 12:40 C6: F. TAKÁCS / P. FOGARAS vs. L. SZELI / E. HRANYCZKA (Vegyes páros OB2/A - Group D-R4)
- 12:40 C7: M. FÜLES / Z. KINÁL vs. K. FEKETE / A. RÉDECSI (Vegyes páros OB2/A - Group D-R4)

- 13:00 C1: F. SZELI / G. FEKETE vs. S. TARR / G. TARRNÉ KAJTÁR (Vegyes páros OB2/A - Group A-R5)
- 13:00 C2: B. KOMÓCSIN / I. SZELI vs. M. MÁTÉ-SZALAI / T. TORMA (Vegyes páros OB2/A - Group A-R5)
- 13:00 C3: A. RUPF / B. TÖRÖK vs. A. CSATÁRI / L. SZELI (Vegyes páros OB2/A - Group B-R5)
- 13:00 C4: P. PÜSPÖK / K. MISZLAI-KOMÓCSIN vs. Z. CSENDE / E. SZABADITS (Vegyes páros OB2/A - Group B-R5)
- 13:00 C5: Á. SÓNYÁK / N. CSIGÓ vs. A. KÉTSZERINÉ SZŰCS / L. KÉTSZERI (Vegyes páros OB2/A - Group C-R5)
- 13:00 C6: F. TAKÁCS / P. FOGARAS vs. K. FEKETE / A. RÉDECSI (Vegyes páros OB2/A - Group D-R5)
- 13:00 C8: Z. KINÁL / M. FÜLES vs. I. MAYER / B. KOMÓCSIN (Vegyes páros OB2/A - Group D-R5)

13:20-tól vasárnap délután végéig: Vegyes páros OB2/A és OB2/B egyenes kieséses rájátszások (Main QF, SF, döntők, vigaszágak és minden helyosztó pozíció).
"""

# 4. Rendszer-utasítások konfigurálása
SYSTEM_INSTRUCTION = f"""
Te egy profi Pickleball Versenybíró és Mentor vagy, aki most Sopronban tartózkodik az Országos Bajnokságon. A küldetésed a játékosok és látogatók maximális kiszolgálása.

A válaszadás során az alábbi prioritási és témakör-rendet kövesd:

1. SOPRONI VERSENYADATOK: Ha a kérdés a konkrét hétvégi soproni menetrendre, játékosokra, helyszínre vagy egyedi szabályokra vonatkozik, KIZÁRÓLAG az alábbi adatokból dolgozhatsz:
{VERSENY_KONTEXTUS}
Amennyiben a kérdés egy konkrét soproni tornára vonatkozó adatra irányul (pl. egy meccs pontszerű végeredménye), ami nincs benne a szövegben, mondd azt: "Erről nincs pontos információm a kiírásban, kérlek fordulj a versenybírósághoz!"

2. ÁLTALÁNOS PICKLEBALL TUDÁS: Ha a kérdés általános pickleball szabályra, kifejezésre, pontozásra, ütésfajtára vagy taktikára vonatkozik, használd a saját széleskörű pickleball szakértelmedet, és válaszolj rá részletesen és segítőkészen.

3. SOPRON VÁROSA ÉS SOPRON FEST: Ha a kérdés Sopron látnivalóira, éttermeire, helyi közlekedésére, vagy a most hétvégén zajló Sopron Fest zenei/kulturális fesztiválra, annak hangulatára, helyszínére vagy részletes napi programjaira vonatkozik, válaszolj bátran a Google Keresés segítségével! Segíts nekik naprakész fesztivál- és városi tippekkel.

4. SZIGORÚ TÉMAKORLÁT: Ha a kérdés egyáltalán NEM kapcsolódik a pickleballhoz, a soproni bajnoksághoz, Sopron városához vagy a Sopron Festhez (pl. iskolai házi feladat, rántott hús recept, programozás, szerelmes versek), akkor NE válaszolj rá! Udvariasan, pici sportos humorral utasítsd vissza, és emlékeztesd a felhasználót, hogy ez az app kizárólag a Sopron Pickleball & Fesztivál hivatalos asszisztense.

Szabályok:
- Használj listákat és félkövér kiemeléseket a lényeges részeknél (időpontok, pályák, helyszínek) a könnyebb olvashatóságért!
- A stílusod legyen sportszerű, profi, de barátságos és közvetlen.
"""

# 5. Felhasználói felület és keresési logika ÉLŐ GOOGLE GROUNDING-AL
user_query = st.text_input("Mit szeretnél tudni? (pl. 'Sipos Anna szombat', 'Kitchen szabály', 'Ki lép fel ma este a Sopron Festen?')", "")

if user_query:
    try:
        genai.configure(api_key=api_key)
        # Itt kapcsoltuk be az élő internetes keresés támogatást (tools='google_search_retrieval')
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_INSTRUCTION,
            tools='google_search_retrieval'
        )
        
        with st.spinner("Asszisztens gondolkodik és keres..."):
            response = model.generate_content(user_query)
            
        st.chat_message("assistant").write(response.text)
        
    except Exception as e:
        st.error(f"Hiba történt a lekérdezés során: {e}")

st.info("Tipp: Ha a saját menetrendedet keresed, pontosan úgy írd be a neved, ahogy a nevezési listában szerepel (pl. 'SIPOS ANNA'). Ha kikapcsolódnál, bátran kérdezz a Sopron Fest mai fellépőiről!")