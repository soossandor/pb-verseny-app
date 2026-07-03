import streamlit as streamlit
import google.generativeai as genai

# 1. Alapbeállítások és stílus (Mobilra optimalizálva)
st.set_page_config(page_title="Sopron Pickleball Asszisztens", page_icon="🏓", layout="centered")

st.title("🏓 Sopron Pickleball Asszisztens")
st.write("Írd be a neved vagy a kérdésed, és a mesterséges intelligencia azonnal kikeresi a menetrended vagy a szabályokat!")

# 2. A Gemini API kulcs kezelése
# Biztonsági okokból érdemes a Streamlit Secrets-be tenni, de teszteléshez itt egy mező:
api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Kérj egy ingyenes kulcsot a Google AI Studio-ban!")

# 3. A VERSENY FIX ADATBÁZISA (Ide ágyazzuk be a PDF-ek tartalmát)
VERSENY_KONTEXTUS = """
=== 1. ÁLTALÁNOS VERSENYINFORMÁCIÓK ÉS SZABÁLYOK ===
- Verseny megnevezése: Magyar Országos Pickleball Bajnokság 2026 - Másodosztály - 3. forduló[cite: 1, 184].
- Időpont: 2026. július 4-05. (Szombat és Vasárnap) [cite: 4, 24, 190].
- Helyszín: 9400 Sopron, Lővér krt. 1., SVSE Sporttelep[cite: 191].
- Versenybizottság: Böhm Zoltán (+36 30/458-1231), Miklós László (+36 30/274-9423), Takács Attila (Póttag: Komáromi Róbert)[cite: 195, 196, 198].
- Hivatalos Labda: Franklin márkájú kültéri labda[cite: 222]. A labda színével megegyező vagy ahhoz nagyon hasonló felszerelés (ruha) viselése TILOS[cite: 223]!
- Bemelegítés: Minden mérkőzés előtt pontosan 2 perc áll rendelkezésre[cite: 225]. Ha a játékos a bemelegítés végére nem jelenik meg, leléptethető[cite: 226].
- Pontozólapok kezelése: A mérkőzés előtt a menetrendben elöl/bal oldalon szereplő csapat veszi át a zsűriasztalnál[cite: 233]. A meccs után a győztes feladata a helyes kitöltés és a leadás a befejezést követő 2 percen belül[cite: 234].
- Mérkőzések menete: 1 nyert játszmáig (szettig) tartanak[cite: 236]. A győzelemhez 11 pontot kell elérni, legalább 2 pont különbséggel[cite: 236].
- Térfélcsere: Amikor a mérkőzésen vezető játékos/páros eléri a 6 pontot, térfélcserére kerül sor[cite: 237].
- Időkérés: Meccsenként minden játékosnak/párosnak pontosan 1 db időkérési lehetősége van[cite: 238].
- Mérkőzésvezetés: Külön mérkőzésvezető nincs (kivéve esetleg a rájátszást), a játékosok a fair-play alapján maguknak bíráskodnak[cite: 386].
- Óvás: Csak a verseny ideje alatt, írásban, 10.000 Ft óvási díj megfizetésével nyújtható be a versenyző által[cite: 388, 395, 396]. Elfogadás esetén visszajár[cite: 395].

=== 2. CSOPORTKÖRÖK ÉS LEBONYOLÍTÁSI REND ===
A csoportok rangsorolása: 1. Több győzelem [cite: 242], 2. Egymás elleni eredmény (ha 2 holtverseny van) [cite: 243], 3. Pontarány (szerzett/vesztett pontok) [cite: 244], 4. Egymás elleni mérkőzés[cite: 245].

Kategóriák továbbjutási rendje:
- Női egyéni OB2/A (7 fő: 1x3 + 1x4 csoport) [cite: 182, 248]: Főág (1-4. hely): A1-B2, B1-A2[cite: 182, 254, 255, 256]. Mellékág (5-7. hely): A3-B4, B3-BYE[cite: 182, 257, 258, 260].
- Női egyéni OB2/B (4 fő: 1x4): Teljes körmérkőzés, nincs egyenes kiesés[cite: 182, 262].
- Női páros OB2/A és OB2/B (8-8 pár: 2x4 csoport) [cite: 183, 265, 273]: Főág (1-4. hely): A1-B2, B1-A2[cite: 183, 266, 267, 268, 274, 275, 276]. Mellékág (5-8. hely): A3-B4, B3-A4[cite: 183, 269, 270, 271, 277, 278, 279].
- Férfi egyéni OB2/A (17 fő: 3x4 + 1x5 csoport) [cite: 182, 281]: Főág negyeddöntő (1-8. hely): A1-C2, B2-D1, C1-A2, D2-B1[cite: 182, 287, 288, 289, 291, 292]. Mellékág (9-12. hely): A3-C3, B3-D3[cite: 182, 293, 294, 295]. Vigaszág (13-16. hely): A4-C4, B4-D4[cite: 182, 296, 297, 298]. D csoport 5. helyezettje automatikusan 17.[cite: 182, 299].
- Férfi egyéni OB2/B, Férfi páros OB2/A, Férfi páros OB2/B, Vegyes páros OB2/B (14-14 induló: 2x3 + 2x4 csoport) [cite: 182, 183, 301, 315, 336, 372]: Főág QF (1-8. hely): A1-C2, B2-D1, C1-A2, D2-B1[cite: 182, 183, 302, 305, 306, 307, 308, 337, 338, 339, 341, 342, 373, 375, 376, 377, 378]. Mellékág (9-12. hely): A3-C3, B3-D3[cite: 182, 183, 309, 310, 311, 343, 344, 345, 379, 380, 381]. Helyosztó (13-14. hely): C4-D4[cite: 182, 183, 312, 313, 333, 334, 346, 347, 382, 383].
- Vegyes páros OB2/A (20 pár: 4x5 csoport) [cite: 183, 349]: Főág QF (1-8. hely): A1-C2, B2-D1, C1-A2, D2-B1[cite: 183, 350, 352, 353, 354, 355]. Mellékág 1 (9-12. hely): A3-C3, B3-D3[cite: 183, 356, 357, 358]. Mellékág 2 (13-16. hely): A4-C4, B4-D4[cite: 183, 365, 366, 367]. Vigaszág (17-20. hely): A5-C5, B5-D5[cite: 183, 368, 369, 370].

=== 3. SZOMBATI MENETREND (2026.07.04.) ===
M1 KÖR (08:00):
- Court 1: A. TAKÁCS / S. TARR vs. C. MAGYAR / P. BERKY (Férfi páros OB2/A - Group C-R1) [cite: 28]
- Court 2: B. TOMORI / R. KOMAROMI vs. A. SCHNELL / I. SCHNELL (Férfi páros OB2/A - Group C-R1) [cite: 28]
- Court 3: P. FOGARAS / G. FEKETE vs. P. PÜSPÖK / B. KOMOCSIN (Férfi páros OB2/A - Group D-R1) [cite: 28]
- Court 4: A. SCHMIDT / I. MAYER vs. Z. KINÁL / C. ENDRE (Férfi páros OB2/A - Group D-R1) [cite: 28]
- Court 5: R. RACZ / V. PÉNTEK vs. L. SZELI / D. KÉTSZERI (Férfi páros OB2/B - Group C-R1) [cite: 28]
- Court 6: A. TOTH / P. PAWLETKO vs. T. LE / T. LE (Férfi páros OB2/B - Group C-R1) [cite: 28]
- Court 7: A. NÉMETH / S. BERTA vs. D. NAGY / J. DINNYÉS (Férfi páros OB2/B - Group D-R1) [cite: 28]
- Court 8: S. SOÓS / Z. SIMON vs. L. VISZOKAI / R. MOLNÁR (Férfi páros OB2/B - Group D-R1) [cite: 28]

M2 KÖR (08:20):
- Court 1: B. ARMAN GHALEGOLAB / Z. CSENDE vs. D. MAGYAR / B. MAGYAR (Férfi páros OB2/A - Group A-R1) [cite: 28]
- Court 2: V. TAKÁCS / Á. HALÁPI vs. L. KÉTSZERI / L. SZELI (Férfi páros OB2/A - Group B-R1) [cite: 28]
- Court 3: G. FEKETE / P. FOGARAS vs. Z. KINÁL / C. ENDRE (Férfi páros OB2/A - Group D-R2) [cite: 28]
- Court 4: P. PÜSPÖK / B. KOMÓCSIN vs. I. MAYER / A. SCHMIDT (Férfi páros OB2/A - Group D-R2) [cite: 28]
- Court 5: B. FÜZI / N. BRUCKNER vs. Z. KARDA / N. GULYÁS (Férfi páros OB2/B - Group A-R1) [cite: 28]
- Court 6: G. DECSI / B. PÅL vs. Á. DÁVID / B. FEKETE (Férfi páros OB2/B - Group B-R1) [cite: 28]
- Court 7: S. BERTA / A. NÉMETH vs. L. VISZOKAI / R. MOLNÁR (Férfi páros OB2/B - Group D-R2) [cite: 28]
- Court 8: J. DINNYÉS / D. NAGY vs. S. SOÓS / Z. SIMON (Férfi páros OB2/B - Group D-R2) [cite: 28]

M3 KÖR (08:40):
- Court 1: M. KATONA / A. SZABOLCSI vs. D. MAGYAR / B. MAGYAR (Férfi páros OB2/A - Group A-R2) [cite: 28]
- Court 2: A. DOBOS / B. TÖRÖK vs. L. KÉTSZERI / L. SZELI (Férfi páros OB2/A - Group B-R2) [cite: 28]
- Court 3: A. TAKÁCS / S. TARR vs. A. SCHNELL / I. SCHNELL (Férfi páros OB2/A - Group C-R2) [cite: 28]
- Court 4: P. BERKY / C. MAGYAR vs. R. KOMAROMI / B. TOMORI (Férfi páros OB2/A - Group C-R2) [cite: 28]
- Court 5: T. NÉMETH / B. ALASZTICS vs. Z. KARDA / N. GULYÁS (Férfi páros OB2/B - Group A-R2) [cite: 28]
- Court 6: K. FEKETE / S. MÉSZÁROS vs. Á. DÁVID / B. FEKETE (Férfi páros OB2/B - Group B-R2) [cite: 28]
- Court 7: T. LE / T. LE vs. R. RACZ / V. PÉNTEK (Férfi páros OB2/B - Group C-R2) [cite: 28]
- Court 8: P. PAWLETKO / A. TÓTH vs. D. KÉTSZERI / L. SZELI (Férfi páros OB2/B - Group C-R2) [cite: 28]

M4 KÖR (09:00):
- Court 1: A. SZABOLCSI / M. KATONA vs. B. ARMAN GHALEGOLAB / Z. CSENDE (Férfi páros OB2/A - Group A-R3) [cite: 31]
- Court 2: B. TÖRÖK / Á. DOBOS vs. V. TAKÁCS / Á. HALÁPI (Férfi páros OB2/A - Group B-R3) [cite: 31]
- Court 3: G. FEKETE / P. FOGARAS vs. I. MAYER / A. SCHMIDT (Férfi páros OB2/A - Group D-R3) [cite: 31]
- Court 4: C. ENDRE / Z. KINÁL vs. P. PÜSPÖK / B. KOMÓCSIN (Férfi páros OB2/A - Group D-R3) [cite: 31]
- Court 5: T. NÉMETH / B. ALASZTICS vs. B. FÜZI / N. BRUCKNER (Férfi páros OB2/B - Group A-R3) [cite: 31]
- Court 6: K. FEKETE / S. MÉSZÁROS vs. B. PAL / G. DECSI (Férfi páros OB2/B - Group B-R3) [cite: 31]
- Court 7: R. MOLNÁR / L. VISZOKAI vs. D. NAGY / J. DINNYÉS (Férfi páros OB2/B - Group D-R3) [cite: 31]
- Court 8: S. BERTA / A. NÉMETH vs. S. SOÓS / Z. SIMON (Férfi páros OB2/B - Group D-R3) [cite: 31]

M5 KÖRŐK ÉS EGYÉNES KIESÉS KEZDETE (09:20 / 09:40):
- 09:20 C3: A. TAKÁCS / S. TARR vs. B. TOMORI / R. KOMAROMI (Férfi páros OB2/A - Group C-R3) [cite: 31]
- 09:20 C4: A. SCHNELL / I. SCHNELL vs. C. MAGYAR / P. BERKY (Férfi páros OB2/A - Group C-R3) [cite: 31]
- 09:20 C7: P. PAWLETKO / A. TÓTH vs. V. PÉNTEK / R. RACZ (Férfi páros OB2/B - Group C-R3) [cite: 31]
- 09:20 C8: D. KÉTSZERI / L. SZELI vs. T. LE / T. LE (Férfi páros OB2/B - Group C-R3) [cite: 31]
- 09:40-től: Férfi páros OB2/A és OB2/B Főági Negyeddöntők (Main QF) az 1-8. helyért[cite: 31].

DÉLUTÁNI EGYÉNI MÉRKŐZÉSEK (SZOMBAT):
- 11:00 C2: A. RÉDECSI vs. P. TÁBORI (Női egyéni OB2/A - Group A-R1) [cite: 32]
- 11:00 C3: E. SZABADITS vs. R. KECSKÉS (Női egyéni OB2/A - Group B-R1) [cite: 32]
- 11:00 C4: F. TAKÁCS vs. Á. HORVÁTH (Női egyéni OB2/A - Group B-R1) [cite: 32]
- 11:20 C2: A. RUPF vs. P. TÁBORI (Női egyéni OB2/A - Group A-R2) [cite: 32]
- 11:20 C3: R. KECSKÉS vs. Á. HORVÁTH (Női egyéni OB2/A - Group B-R2) [cite: 32]
- 11:20 C4: E. SZABADITS vs. F. TAKÁCS (Női egyéni OB2/A - Group B-R2) [cite: 32]
- 11:20 C6: A. SIPOS vs. D. FEKETÉNÉ GYULAI (Női egyéni OB2/B - R1) [cite: 32, 42]
- 11:20 C7: K. SZABOLCSINÉ MORVAI vs. V. VISZOKAI (Női egyéni OB2/B - R1) [cite: 32, 42]
- 11:40 C2: A. RUPF vs. A. RÉDECSI (Női egyéni OB2/A - Group A-R3) [cite: 32]
- 11:40 C3: E. SZABADITS vs. F. TAKÁCS (Női egyéni OB2/A - Group B-R3) [cite: 33]
- 11:40 C4: Á. HORVÁTH vs. R. KECSKÉS (Női egyéni OB2/A - Group B-R3) [cite: 33]
- 11:40 C6: A. SIPOS vs. V. VISZOKAI (Női egyéni OB2/B - R2) [cite: 32, 42]
- 11:40 C7: D. FEKETÉNÉ GYULAI vs. K. SZABOLCSINÉ MORVAI (Női egyéni OB2/B - R2) [cite: 33, 42]
- 12:00 C6: A. SIPOS vs. K. SZABOLCSINÉ MORVAI (Női egyéni OB2/B - R3) [cite: 32, 42]
- 12:00 C7: V. VISZOKAI vs. D. FEKETÉNÉ GYULAI (Női egyéni OB2/B - R3) [cite: 33, 42]

FÉRFI EGYÉNI INDULÁSOK (SZOMBAT KORADÉLUTÁN):
- 12:20 C5: J. DINNYÉS vs. D. TRAN VAN (Férfi egyéni OB2/B - Group C-R1) [cite: 32, 127]
- 12:20 C6: L. SZELI vs. V. PÉNTEK (Férfi egyéni OB2/B - Group C-R1) [cite: 33, 127]
- 12:20 C7: A. TÓTH vs. T. TOMORI (Férfi egyéni OB2/B - Group D-R1) [cite: 33, 131]
- 12:20 C8: B. FEKETE vs. R. RACZ (Férfi egyéni OB2/B - Group D-R1) [cite: 32, 131]
- 12:40 C1: I. MAYER vs. P. BERKY (Férfi egyéni OB2/A - Group A-R1) [cite: 32, 60]
- 12:40 C2: B. MAGYAR vs. G. FEKETE (Férfi egyéni OB2/A - Group A-R1) [cite: 33, 60]
- 12:40 C3: A. TAKÁCS vs. Z. KINÁL (Férfi egyéni OB2/A - Group D-R1) [cite: 33, 72]
- 12:40 C4: C. MAGYAR vs. A. SCHMIDT (Férfi egyéni OB2/A - Group D-R1) [cite: 33, 72]
- 12:40 C5: D. NAGY vs. Á. DÁVID (Férfi egyéni OB2/B - Group A-R1) [cite: 32, 100]
- 12:40 C6: N. BRUCKNER vs. S. MÉSZÁROS (Férfi egyéni OB2/B - Group B-R1) [cite: 33, 123]
- 12:40 C7: A. TÓTH vs. R. RACZ (Férfi egyéni OB2/B - Group D-R2) [cite: 33, 131]
- 12:40 C8: T. TOMORI vs. B. FEKETE (Férfi egyéni OB2/B - Group D-R2) [cite: 131]
- 13:00 C1: M. KATONA vs. B. ALASZTICS (Férfi egyéni OB2/A - Group B-R1) [cite: 32, 64]
- 13:00 C2: B. TÖRÖK vs. V. TAKÁCS (Férfi egyéni OB2/A - Group B-R1) [cite: 33, 64]
- 13:00 C3: Z. CSENDE vs. A. SCHMIDT (Férfi egyéni OB2/A - Group D-R2) [cite: 32, 72]
- 13:00 C4: C. MAGYAR vs. A. TAKÁCS (Férfi egyéni OB2/A - Group D-R2) [cite: 72]
- 13:00 C5: D. MAGYAR vs. Á. DÁVID (Férfi egyéni OB2/B - Group A-R2) [cite: 32, 100]
- 13:00 C6: P. PAWLETKO vs. S. MÉSZÁROS (Férfi egyéni OB2/B - Group B-R2) [cite: 33, 123]
- 13:00 C7: J. DINNYÉS vs. V. PÉNTEK (Férfi egyéni OB2/B - Group C-R2) [cite: 33, 127]
- 13:00 C8: D. TRAN VAN vs. L. SZELI (Férfi egyéni OB2/B - Group C-R2) [cite: 33, 127]
- 13:20 C1: I. MAYER vs. G. FEKETE (Férfi egyéni OB2/A - Group A-R2) [cite: 33, 60]
- 13:20 C2: P. BERKY vs. B. MAGYAR (Férfi egyéni OB2/A - Group A-R2) [cite: 34, 60]
- 13:20 C3: P. FOGARAS vs. B. ARMAN GHALEGOLAB (Férfi egyéni OB2/A - Group C-R1) [cite: 34, 68]
- 13:20 C4: A. SZABOLCSI vs. B. TOMORI (Férfi egyéni OB2/A - Group C-R1) [cite: 34, 68]
- 13:20 C5: D. MAGYAR vs. D. NAGY (Férfi egyéni OB2/B - Group A-R3) [cite: 32, 100]
- 13:20 C6: P. PAWLETKO vs. N. BRUCKNER (Férfi egyéni OB2/B - Group B-R3) [cite: 33, 123]
- 13:20 C7: A. TÓTH vs. B. FEKETE (Férfi egyéni OB2/B - Group D-R3) [cite: 33, 131]
- 13:20 C8: R. RACZ vs. T. TOMORI (Férfi egyéni OB2/B - Group D-R3) [cite: 131]
- 13:40 C1: V. TAKÁCS vs. M. KATONA (Férfi egyéni OB2/A - Group B-R2) [cite: 33, 64]
- 13:40 C2: B. TÖRÖK vs. B. ALASZTICS (Férfi egyéni OB2/A - Group B-R2) [cite: 34, 64]
- 13:40 C3: A. SCHMIDT vs. A. TAKÁCS (Férfi egyéni OB2/A - Group D-R3) [cite: 34, 72]
- 13:40 C4: Z. CSENDE vs. Z. KINÁL (Férfi egyéni OB2/A - Group D-R3) [cite: 34, 72]
- 13:40 C7: J. DINNYÉS vs. L. SZELI (Férfi egyéni OB2/B - Group C-R3) [cite: 34, 127]
- 13:40 C8: V. PÉNTEK vs. D. TRAN VAN (Férfi egyéni OB2/B - Group C-R3) [cite: 33, 127]
- 14:00 C1: I. MAYER vs. B. MAGYAR (Férfi egyéni OB2/A - Group A-R3) [cite: 33, 60]
- 14:00 C2: G. FEKETE vs. P. BERKY (Férfi egyéni OB2/A - Group A-R3) [cite: 34, 60]
- 14:00 C3: A. SZABOLCSI vs. B. ARMAN GHALEGOLAB (Férfi egyéni OB2/A - Group C-R2) [cite: 34, 68]
- 14:00 C4: B. TOMORI vs. P. FOGARAS (Férfi egyéni OB2/A - Group C-R2) [cite: 34, 68]
- 14:20 C1: B. TÖRÖK vs. M. KATONA (Férfi egyéni OB2/A - Group B-R3) [cite: 33, 64]
- 14:20 C2: B. ALASZTICS vs. V. TAKÁCS (Férfi egyéni OB2/A - Group B-R3) [cite: 34, 64]
- 14:20 C3: Z. CSENDE vs. A. TAKÁCS (Férfi egyéni OB2/A - Group D-R4) [cite: 35, 72]
- 14:20 C4: Z. KINÁL vs. C. MAGYAR (Férfi egyéni OB2/A - Group D-R4) [cite: 35, 72]
- 14:40 C1: B. ARMAN GHALEGOLAB vs. B. TOMORI (Férfi egyéni OB2/A - Group C-R3) [cite: 34, 68]
- 14:40 C2: A. SZABOLCSI vs. P. FOGARAS (Férfi egyéni OB2/A - Group C-R3) [cite: 35, 68]
- 14:40 C3: Z. CSENDE vs. C. MAGYAR (Férfi egyéni OB2/A - Group D-R5) [cite: 34, 72]
- 14:40 C4: Z. KINÁL vs. A. SCHMIDT (Férfi egyéni OB2/A - Group D-R5) [cite: 35, 72]

15:00-tól szombat késő délutánig: Férfi egyéni OB2/A és OB2/B egyenes kieséses szakaszok (Main QF, SF, döntők és helyosztók)[cite: 34, 35, 36].

=== 4. VASÁRNAPI MENETREND (2026.07.05.) ===
M1 KÖR - NŐI PÁROSOK KEZDETE (08:00):
- Court 1: F. SZELI / A. RUPF vs. J. POLGÁR / A. CSATÁRI (Női páros OB2/A - Group A-R1) [cite: 7]
- Court 2: K. MISZLAI-KOMÓCSIN / A. RÉDECSI vs. M. MÁTÉ-SZALAI / A. SIPOS (Női páros OB2/A - Group A-R1) [cite: 7]
- Court 3: N. CSIGÓ / E. HORVÁTH vs. R. HORVÁTH / K. LUKÁCS (Női páros OB2/A - Group B-R1) [cite: 7]
- Court 4: P. TABORI / F. TAKÁCS vs. E. HRANYCZKA / L. HRANYCZKA (Női páros OB2/A - Group B-R1) [cite: 7]
- Court 5: K. JAGICZA / K. MOJZER vs. R. KECSKÉS / K. SZABOLCSINÉ MORVAI (Női páros OB2/B - Group A-R1) [cite: 7]
- Court 6: E. FANCSALINÉ KOTÁN / M. CSILLAG vs. R. FEKETE ANDREA / D. FEKETÉNÉ GYULAI (Női páros OB2/B - Group A-R1) [cite: 7]
- Court 7: A. KÉTSZERINÉ SZŰCS / B. KOMÓCSIN vs. G. PETRA / E. RUBINT (Női páros OB2/B - Group B-R1) [cite: 7]
- Court 8: N. KECSKÉS AMÁTA / L. PETROVICS vs. E. NÉMETH / G. BRINDZA (Női páros OB2/B - Group B-R1) [cite: 7]

M2 KÖR (08:20):
- Court 1: A. RUPF / F. SZELI vs. M. MÁTÉ-SZALAI / A. SIPOS (Női páros OB2/A - Group A-R2) [cite: 7]
- Court 2: J. POLGÁR / A. CSATÁRI vs. K. MISZLAI-KOMÓCSIN / A. RÉDECSI (Női páros OB2/A - Group A-R2) [cite: 7]
- Court 3: P. TABORI / F. TAKÁCS vs. K. LUKÁCS / R. HORVÁTH (Női páros OB2/A - Group B-R2) [cite: 7]
- Court 4: E. HRANYCZKA / L. HRANYCZKA vs. N. CSIGÓ / E. HORVÁTH (Női páros OB2/A - Group B-R2) [cite: 7]
- Court 5: K. JAGICZA / K. MOJZER vs. D. FEKETÉNÉ GYULAI / R. FEKETE ANDREA (Női páros OB2/B - Group A-R2) [cite: 7]
- Court 6: K. SZABOLCSINÉ MORVAI / R. KECSKÉS vs. M. CSILLAG / E. FANCSALINÉ KOTÁN (Női páros OB2/B - Group A-R2) [cite: 7]
- Court 7: L. PETROVICS / N. KECSKÉS AMÁTA vs. G. PETRA / E. RUBINT (Női páros OB2/B - Group B-R2) [cite: 7]
- Court 8: G. BRINDZA / E. NÉMETH vs. B. KOMÓCSIN / A. KÉTSZERINÉ SZŰCS (Női páros OB2/B - Group B-R2) [cite: 7]

M3 KÖR (08:40):
- Court 1: F. SZELI / A. RUPF vs. K. MISZLAI-KOMÓCSIN / A. RÉDECSI (Női páros OB2/A - Group A-R3) [cite: 7]
- Court 2: M. MÁTÉ-SZALAI / A. SIPOS vs. A. CSATÁRI / J. POLGÁR (Női páros OB2/A - Group A-R3) [cite: 7]
- Court 3: F. TAKÁCS / P. TÁBORI vs. E. HORVÁTH / N. CSIGÓ (Női páros OB2/A - Group B-R3) [cite: 7]
- Court 4: K. LUKÁCS / R. HORVÁTH vs. L. HRANYCZKA / E. HRANYCZKA (Női páros OB2/A - Group B-R3) [cite: 7]
- Court 5: K. JAGICZA / K. MOJZER vs. E. FANCSALINÉ KOTÁN / M. CSILLAG (Női páros OB2/B - Group A-R3) [cite: 7]
- Court 6: D. FEKETÉNÉ GYULAI / R. FEKETE ANDREA vs. R. KECSKÉS / K. SZABOLCSINÉ MORVAI (Női páros OB2/B - Group A-R3) [cite: 7]
- Court 7: N. KECSKÉS AMÁTA / L. PETROVICS vs. A. KÉTSZERINÉ SZŰCS / B. KOMÓCSIN (Női páros OB2/B - Group B-R3) [cite: 7]
- Court 8: E. RUBINT / G. PETRA vs. E. NÉMETH / G. BRINDZA (Női páros OB2/B - Group B-R3) [cite: 7]

09:00-tól: Női páros elődöntők, helyosztók és döntők (OB2/A és OB2/B)[cite: 14].

VASÁRNAP DELES ÉS DÉLUTÁNI VEGYES PÁROSOK:
- 09:40 C1: S. TARR / G. TARRNÉ KAJTÁR vs. M. MÁTÉ-SZALAI / T. TORMA (Vegyes páros OB2/A - Group A-R1) [cite: 14]
- 09:40 C2: S. BERTA / G. PETRA vs. E. FANCSALINÉ KOTÁN / L. TORMA (Vegyes páros OB2/B - Group A-R1) [cite: 14]
- 09:40 C3/4: B. FEKETE / D. FEKETÉNÉ GYULAI vs. K. JAGICZA / D. TRAN VAN (Vegyes páros OB2/B - Group B-R1)[cite: 14]; A. SIPOS / A. MÁTÉ vs. R. FEKETE ANDREA / B. FÜZI (Vegyes páros OB2/B - Group C-R1) [cite: 14]
- 09:40 C5/6: E. NÉMETH / G. DECSI vs. L. HRANYCZKA / Z. TAKÁCS (Vegyes páros OB2/B - Group C-R1)[cite: 14]; C. MAGYAR / R. HORVÁTH vs. Á. SÓNYÁK / N. CSIGÓ (Vegyes páros OB2/A - Group C-R1) [cite: 14]
- 09:40 C7: A. DAVID / K. STEINWENGERNÉ LUGOSI vs. V. VISZOKAI / L. VISZOKAI (Vegyes páros OB2/B - Group D-R1) [cite: 14]
- 09:40 C8: R. KECSKÉS / Z. KARDA vs. S. SOÓS / G. BRINDZA (Vegyes páros OB2/B - Group D-R1) [cite: 14]

- 10:00 C2: L. PETROVICS / A. SCHMIDT vs. E. FANCSALINÉ KOTÁN / L. TORMA (Vegyes páros OB2/B - Group A-R2) [cite: 14]
- 10:00 C3/4: A. MÁTÉ / A. SIPOS vs. E. NÉMETH / G. DECSI[cite: 14]; P. TÁBORI / M. KATONA vs. L. KÉTSZERI / A. KÉTSZERINÉ SZŰCS[cite: 14]; N. KECSKÉS AMÁTA / R. MOLNÁR vs. L. HRANYCZKA / Z. TAKÁCS[cite: 14]; B. FÜZI / R. FEKETE ANDREA vs. K. JAGICZA / D. TRAN VAN (Mérkőzések a Vegyes páros OB2/A és OB2/B csoportjaiból)[cite: 14].
- 10:00 C7: Z. KARDA / R. KECSKÉS vs. V. VISZOKAI / L. VISZOKAI (Vegyes páros OB2/B - Group D-R2) [cite: 14]
- 10:00 C8: S. SOÓS / G. BRINDZA vs. K. STEINWENGERNÉ LUGOSI / Á. DÁVID (Vegyes páros OB2/B - Group D-R2) [cite: 14]

- 10:20 C2: A. SCHMIDT / L. PETROVICS vs. G. PETRA / S. BERTA (Vegyes páros OB2/B - Group A-R3) [cite: 15]
- 10:20 C3/4: A. SIPOS / A. MÁTÉ vs. E. NÉMETH / G. DECSI[cite: 15]; R. MOLNÁR / N. KECSKÉS AMÁTA vs. B. FEKETE / D. FEKETÉNÉ GYULAI [cite: 15]
- 10:20 C5/6: M. KATONA / P. TÁBORI vs. N. CSIGÓ / Á. SÓNYÁK[cite: 15]; Z. TAKÁCS / L. HRANYCZKA vs. B. FÜZI / R. FEKETE ANDREA [cite: 15]
- 10:20 C7: R. KECSKÉS / Z. KARDA vs. Á. DÁVID / K. STEINWENGERNÉ LUGOSI [cite: 15]
- 10:20 C8: L. VISZOKAI / V. VISZOKAI vs. G. BRINDZA / S. SOÓS [cite: 15]

- 11:40 C2: A. SZABOLCSI / K. SZABOLCSINÉ MORVAI vs. B. KOMÓCSIN / L. SZELI (Vegyes páros OB2/A - Group A-R1) [cite: 16]
- 11:40 C3: D. MAGYAR / A. CZIRJÁK vs. P. PÜSPÖK / K. MISZLAI-KOMÓCSIN (Vegyes páros OB2/A - Group B-R1) [cite: 16]
- 11:40 C4: Z. CSENDE / E. SZABADITS vs. A. CSATÁRI / L. SZELI (Vegyes páros OB2/A - Group B-R1) [cite: 16]
- 11:40 C6: V. TAKÁCS / J. POLGÁR vs. L. KÉTSZERI / A. KÉTSZERINÉ SZŰCS (Vegyes páros OB2/A - Group C-R1) [cite: 16]
- 11:40 C7: E. HRANYCZKA / L. SZELI vs. M. FÜLES / Z. KINÁL (Vegyes páros OB2/A - Group D-R1) [cite: 16]
- 11:40 C8: K. FEKETE / A. RÉDECSI vs. E. HRANYCZKA / L. SZELI (Vegyes páros OB2/A - Group D-R2) [cite: 16]

- 12:00 C1: G. FEKETE / F. SZELI vs. T. TORMA / M. MÁTÉ-SZALAI (Vegyes páros OB2/A - Group A-R2) [cite: 14]
- 12:00 C2: G. TARRNÉ KAJTÁR / S. TARR vs. A. SZABOLCSI / K. SZABOLCSINÉ MORVAI (Vegyes páros OB2/A - Group A-R2) [cite: 16]
- 12:00 C3: A. RUPF / B. TÖRÖK vs. L. SZELI / A. CSATÁRI (Vegyes páros OB2/A - Group B-R2) [cite: 16]
- 12:00 C4: Z. CSENDE / E. SZABADITS vs. D. MAGYAR / A. CZIRJÁK (Vegyes páros OB2/A - Group B-R2) [cite: 16]
- 12:00 C6: V. TAKÁCS / J. POLGÁR vs. R. HORVÁTH / C. MAGYAR (Vegyes páros OB2/A - Group C-R2) [cite: 16]
- 12:00 C7: F. TAKÁCS / P. FOGARAS vs. B. KOMÓCSIN / I. MAYER (Vegyes páros OB2/A - Group D-R2) [cite: 16]

- 12:20 C1: G. FEKETE / F. SZELI vs. B. KOMÓCSIN / I. SZELI (Vegyes páros OB2/A - Group A-R3) [cite: 15]
- 12:20 C2: T. TORMA / M. MÁTÉ-SZALAI vs. A. SZABOLCSI / K. SZABOLCSINÉ MORVAI (Vegyes páros OB2/A - Group A-R3) [cite: 16]
- 12:20 C3: A. CSATÁRI / L. SZELI vs. A. CZIRJÁK / D. MAGYAR (Vegyes páros OB2/A - Group B-R3) [cite: 16]
- 12:20 C4: B. TÖRÖK / A. RUPF vs. P. PÜSPÖK / K. MISZLAI-KOMÓCSIN (Vegyes páros OB2/A - Group B-R3) [cite: 16]
- 12:20 C5: L. KÉTSZERI / A. KÉTSZERINÉ SZŰCS vs. R. HORVÁTH / C. MAGYAR (Vegyes páros OB2/A - Group C-R3) [cite: 16]
- 12:20 C6: F. TAKÁCS / P. FOGARAS vs. M. FÜLES / Z. KINÁL (Vegyes páros OB2/A - Group D-R3) [cite: 16]
- 12:20 C8: I. MAYER / B. KOMÓCSIN vs. L. SZELI / E. HRANYCZKA (Vegyes páros OB2/A - Group D-R3) [cite: 16]

- 12:40 C1: F. SZELI / G. FEKETE vs. A. SZABOLCSI / K. SZABOLCSINÉ MORVAI (Vegyes páros OB2/A - Group A-R4) [cite: 15]
- 12:40 C2: I. SZELI / B. KOMÓCSIN vs. G. TARRNÉ KAJTÁR / S. TARR (Vegyes páros OB2/A - Group A-R4) [cite: 16]
- 12:40 C3: A. RUPF / B. TÖRÖK vs. D. MAGYAR / A. CZIRJÁK (Vegyes páros OB2/A - Group B-R4) [cite: 16]
- 12:40 C4: K. MISZLAI-KOMÓCSIN / P. PÜSPÖK vs. E. SZABADITS / Z. CSENDE (Vegyes páros OB2/A - Group B-R4) [cite: 16]
- 12:40 C5: A. SÓNYÁK / N. CSIGÓ vs. V. TAKÁCS / J. POLGÁR (Vegyes páros OB2/A - Group C-R4) [cite: 16]
- 12:40 C6: F. TAKÁCS / P. FOGARAS vs. L. SZELI / E. HRANYCZKA (Vegyes páros OB2/A - Group D-R4) [cite: 16]
- 12:40 C7: M. FÜLES / Z. KINÁL vs. K. FEKETE / A. RÉDECSI (Vegyes páros OB2/A - Group D-R4) [cite: 16]

- 13:00 C1: F. SZELI / G. FEKETE vs. S. TARR / G. TARRNÉ KAJTÁR (Vegyes páros OB2/A - Group A-R5) [cite: 15]
- 13:00 C2: B. KOMÓCSIN / I. SZELI vs. M. MÁTÉ-SZALAI / T. TORMA (Vegyes páros OB2/A - Group A-R5) [cite: 17]
- 13:00 C3: A. RUPF / B. TÖRÖK vs. A. CSATÁRI / L. SZELI (Vegyes páros OB2/A - Group B-R5) [cite: 17]
- 13:00 C4: P. PÜSPÖK / K. MISZLAI-KOMÓCSIN vs. Z. CSENDE / E. SZABADITS (Vegyes páros OB2/A - Group B-R5) [cite: 17]
- 13:00 C5: Á. SÓNYÁK / N. CSIGÓ vs. A. KÉTSZERINÉ SZŰCS / L. KÉTSZERI (Vegyes páros OB2/A - Group C-R5) [cite: 17]
- 13:00 C6: F. TAKÁCS / P. FOGARAS vs. K. FEKETE / A. RÉDECSI (Vegyes páros OB2/A - Group D-R5) [cite: 17]
- 13:00 C8: Z. KINÁL / M. FÜLES vs. I. MAYER / B. KOMÓCSIN (Vegyes páros OB2/A - Group D-R5) [cite: 16]

13:20-tól vasárnap délután végéig: Vegyes páros OB2/A és OB2/B egyenes kieséses rájátszások (Main QF, SF, döntők, vigaszágak és minden helyosztó pozíció)[cite: 15, 17].
"""

SYSTEM_INSTRUCTION = f"""
Te egy profi Pickleball Versenybíró és Mentor vagy. A küldetésed, hogy a megadott versenyadatok alapján pontosan, röviden és barátságosan válaszolj a játékosok kérdéseire.
Kizárólag az alábbi adatokból dolgozhatsz:
{VERSENY_KONTEXTUS}

Szabályok:
1. Ha a játékos a nevére keres, listázd ki az összes meccsét időponttal, ellenféllel és pályaszámmal!
2. SOHA NE hallucinálj! Ha valami nem szerepel az adatok között, mondd azt: "Erről nincs pontos információm a kiírásban, kérlek fordulj a versenybírósághoz!"
3. Használj félkövér kiemeléseket a lényeges részeknél (időpont, pálya)!
"""

# 4. Felhasználói felület és logika
user_query = st.text_input("Mit szeretnél tudni? (pl. 'Sipos Anna szombat', vagy 'Hány pontig tart egy szett?')", "")

if user_query:
        try:
            # Gemini konfigurálása
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash", # Szupergyors és olcsó/ingyenes modell
                system_instruction=SYSTEM_INSTRUCTION
            )
            
            with st.spinner("Versenybíró gondolkodik..."):
                response = model.generate_content(user_query)
                
            st.chat_message("assistant").write(response.text)
            
        except Exception as e:
            st.error(f"Hiba történt a lekérdezés során: {e}")

st.info("Tipp: Ha a saját menetrendedet keresed, pontosan úgy írd be a neved, ahogy a nevezési listában szerepel (pl. 'SIPOS ANNA').")