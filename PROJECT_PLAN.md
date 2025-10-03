# 📡 AnomRadar – Full Project Plan

## 🧠 Vision

**AnomRadar** on autonominen OSINT- ja tietoturvaskannerialusta, joka kerää, analysoi ja raportoi julkisesti saatavaa yritystietoa yhdestä hakukentästä. Sen tarkoitus on antaa yrityksille kokonaisvaltainen näkyvyys heidän ulkoiseen hyökkäyspintaansa: mitä tietoa yrityksestä löytyy netistä, mitä voidaan päätellä, mitkä hyökkäyspolut ovat mahdollisia — ja miten riskejä voidaan vähentää ennen kuin joku muu hyödyntää niitä.

Tavoite: Rakentaa **täysin automaattinen ja laajennettava järjestelmä**, joka tekee tietoturvatestaajan tai OSINT-asiantuntijan työn 24/7 – ilman että kukaan klikkaa nappia.

---

## 📍 Kokonaisarkkitehtuuri

### 1. Backend (Node.js + TypeScript)
- Asennetaan **kotipalvelimelle** tai VPS:lle.
- Palvelu toimii Cloudflare Tunnelin kautta julkisessa osoitteessa `https://copilot.anomfin.fi`.
- Vastaa koko tiedonkeruuprosessin orkestroinnista ja analyysistä.

### 2. REST API (PHP + MySQL)
- Hostataan `anomfin.fi` webhotellissa polussa `/api/radar/`.
- Vastaanottaa backendin lähettämän datan ja tallentaa sen **MySQL 8.0** -tietokantaan.
- Luo ja palvelee **HTML- ja PDF-raportteja** sekä teknisiä Markdown-liitteitä.
- Vastaa tietojen säilytys- ja poistopolitiikasta (90 päivän automaattinen poisto).

### 3. Frontend (Static UI)
- Kevyt käyttöliittymä, hostattu `anomfin.fi` alla esim. `/radar-ui/`.
- Käyttöliittymä tarjoaa:
  - Yrityshaun (nimi tai Y-tunnus) PRH/YTJ:n avoimesta rajapinnasta.
  - Rekonisivun, jossa näkyy työn eteneminen ja löydökset.
  - Whitelist-hyväksynnän Telegram- ja WhatsApp-simulaatioita varten.
  - Raporttisivun, josta voi ladata johtotason raportit ja tekniset liitteet.

---

## 🧰 Tietovirta – “Data seuraa dataa”

1. **Syöte:** Käyttäjä antaa yrityksen nimen tai Y-tunnuksen.
2. **PRH/YTJ-integraatio:** Backend hakee yrityksen perustiedot (nimi, y-tunnus, muoto, rekisteröintipäivä jne.).
3. **Domain discovery:** Yrityksen nimen perusteella haetaan ja validoidaan todennäköiset domainit.
4. **DNS- ja sähköpostianalyysi:** SPF-, DKIM- ja DMARC-tietueet, MX-palvelimet, riskitasot.
5. **Verkkopalvelinskanneeraus:** OWASP ZAPin passiivinen analyysi, sivuston rakenteen ja haavoittuvuuksien tunnistus.
6. **Porttiskannaus:** Nmap tarkistaa top-100 portit ja avoimet palvelut.
7. **Yhteystietojen haku:** Sivustolta ja muista julkisista lähteistä kerätään puhelinnumeroita ja sähköpostiosoitteita (robots.txt huomioiden).
8. **Vuototarkistukset:** Valinnaisesti tarkistetaan HIBP-rajapinnan kautta, onko tunnistetietoja vuotanut.
9. **Riskimallinnus:** Kaikki löydökset pisteytetään ja luokitellaan (Low / Medium / High).
10. **Raportointi:** Luodaan Executive PDF, HTML-yhteenveto ja tekninen Markdown-liite.

---

## 🛠️ Tekninen stack

| Komponentti | Teknologia |
|------------|------------|
| Backend | Node.js 20+, TypeScript, Express |
| Data-keruu | DNS (node:dns), Axios/Undici, OWASP ZAP API, Nmap |
| API | PHP 8.3, mysqli, JWT/Bearer + Cloudflare IP-rajaus |
| DB | MySQL 8.0 (utf8mb4), indeksoitu schema |
| UI | HTML5, Tailwind, Vanilla JS |
| Simulaatiot | Telegram Bot API, WhatsApp Cloud API |
| Click tracking | PHP (GET-logger + MySQL) |
| Infra | Cloudflare Tunnel, PM2, cron |

---

## 📊 Tietokantarakenne (pääkohdat)

- `companies`: yrityksen perustiedot
- `domains`: löydetyt domainit ja lähteet
- `scans`: rekonstrun statukset, riskipisteet ja metadata
- `email_auth`: SPF/DKIM/DMARC tulokset ja riskit
- `web_alerts`: ZAPin löytämät High/Medium-riskit
- `ports`: avoimet portit ja palvelut
- `contacts`: löydetyt puhelinnumerot ja sähköpostit (whitelist-info mukana)
- `leaks`: HIBP/vuotojen tulokset
- `reports`: raporttitiedostojen sijainnit ja URL:t

---

## 📡 Simulaatiot ja eettiset rajat

- Oletuksena `simulation_enabled: false`: ei viestien lähetyksiä ennen kuin käyttäjä hyväksyy ne UI:ssa.
- Viestit lähetetään vain **whitelistatuiksi merkityille kontakteille**.
- Klikkilinkit ohjataan `https://test.anomfin.fi` -sandboxiin, joka kirjaa klikkaukset MySQL:ään.
- Robots.txt noudatetaan aina.  
- Kaikki data salataan siirrossa ja PII tallennetaan minimitasolla.

---

## 📈 Riskipisteytys (0–100)

| Tarkistus | Painoarvo |
|----------|-----------|
| DMARC puuttuu | +25 |
| DMARC p=none | +15 |
| SPF puuttuu | +10 |
| Web High riskit | +5 per alert (max +25) |
| Web Medium riskit | +2 per alert (max +10) |
| Avoimet hallintaportit | max +20 |
| HIBP osumat | +10 |
| SMS riskit (Medium/High) | +5 / +10 |

Luokitus:  
- **0–30:** Low  
- **31–60:** Medium  
- **61–100:** High

---

## 📅 Tiekartta

### 🥇 Vaihe 1 – MVP (v1.0)
- PRH/YTJ-haku ja domain discovery
- DNS/SPF/DMARC analyysi
- ZAP-passive & Nmap top-100
- Tietokantamalli ja API
- Executive-raportti (HTML/PDF)

### 🥈 Vaihe 2 – Enrichment (v1.1)
- Contact discovery + vuototarkistus
- HIBP-integraatio
- Riskimallin viimeistely
- Tekninen Markdown-liite

### 🥉 Vaihe 3 – Simulaatiot (v1.2)
- Telegram/WhatsApp whitelist-skenaariot
- Klikkiseuranta sandbox-domainissa
- UI-pohjainen whitelist-hallinta

### 🏁 Vaihe 4 – Automaatio & integraatiot (v1.3+)
- Jatkuva skannaus / ajastukset
- Jira / Slack / Teams -integraatiot
- Multi-domain scanning ja organisaatiotasoinen raportointi
- API-tuki kolmannen osapuolen SIEM/SOC -järjestelmille

---

## 🧱 Turva ja tietosuoja

- **90 päivän poistopolitiikka:** kaikki löydökset, kontaktit ja raportit poistetaan automaattisesti.  
- **Audit-trail:** jokainen pyyntö, skannaus ja raportti kirjataan.  
- **Ei aktiivisia hyökkäyksiä:** vain passiivinen tiedonkeruu ja analyysi.  
- **Lakisääteinen käyttö:** tarkoitettu vain luvalliseen tietoturvatestaamiseen ja omaisuuden suojaukseen.

---

## ✅ Menestysmittarit

- ⏱️ Täydellinen rekoni alle 10 minuutissa.  
- 📊 Riskipisteiden tarkkuus ±5 pisteen sisällä manuaalisesta auditoinnista.  
- 📁 Raportti valmis PDF/HTML-muodossa automaattisesti ilman manuaalista työtä.  
- 📬 100 % viesteistä menee vain whitelistatuiksi merkityille vastaanottajille.  
- 🔁 Päivitykset CI/CD-putkessa alle 5 minuutissa.

---

## 📌 Yhteenveto

**AnomRadar** ei ole yksittäinen työkalu — se on täysi **OSINT-, recon- ja tietoturva-analyysialusta**, joka automatisoi koko prosessin yrityksen julkisen hyökkäyspinnan kartoittamisesta selkeään toimitusjohtajalle tarkoitettuun raporttiin asti. Sen arvo on siinä, että se havaitsee ja esittää *kaiken, minkä hyökkääjä voisi löytää* — mutta ennen kuin kukaan muu tekee sen.
