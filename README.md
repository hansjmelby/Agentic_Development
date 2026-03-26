# Før workshoppen
- Installer en agent (vi bruker claude som demo, men du kan bruke hva du vil)

## installasjon MAC OS
- mac : brew install --cask claude-code (prøv dette først)
alternativt 
- [Innstallasjon MAC OS](./installation-commands-mac.pdf)
- export ANTHROPIC_API_KEY="din_api_nøkkel_her"

## installasjon Windows
- [Innstallasjon Windows](./installation-commands-windows.pdf)
- export ANTHROPIC_API_KEY="din_api_nøkkel_her"

# 🚀 Introduksjon til Agentisk Utvikling

Agentisk utvikling handler om å bygge systemer der autonome eller semi-autonome "agenter" kan ta beslutninger, utføre oppgaver og samarbeide for å løse komplekse problemer. Disse agentene bruker ofte store språkmodeller (LLMs), verktøy og minne for å handle mer selvstendig enn tradisjonell programvare.

I stedet for at utviklere spesifiserer hver eneste regel, designer man systemer som kan *resonnere*, *planlegge* og *tilpasse seg* dynamisk.

Teoretiske slider med tips og råd finnes her : https://docs.google.com/presentation/d/1qQKs8Z7BUh-pL1uqy_PsXe_6NK8SNvv19kAhVV640Oc/edit?usp=sharing

---

## 🧠 Hva er en agent?

En agent er typisk en komponent som:
- Forstår en oppgave (prompt eller mål)
- Planlegger hvordan den skal løses
- Utfører handlinger (f.eks. API-kall, kodekjøring)
- Evaluerer resultatet og justerer seg

Eksempler:
- En AI som skriver og tester kode automatisk
- En chatbot som kan booke møter via eksterne systemer
- Et system som analyserer data og tar beslutninger kontinuerlig

---

## 🔥 Hvorfor er dette viktig?

Agentisk utvikling er viktig fordi:

### 1. Økt automatisering
Oppgaver som tidligere krevde manuell oppfølging kan nå utføres autonomt.

### 2. Mer robuste systemer
Agenter kan håndtere uforutsette situasjoner ved å tilpasse seg i sanntid.

### 3. Høyere utviklerproduktivitet
Utviklere kan fokusere på mål og arkitektur fremfor detaljerte implementasjoner.

### 4. Fundamentet for fremtidens applikasjoner
Mange moderne AI-systemer (Copilots, autonome workflows, AI-assistenter) er bygget på agentiske prinsipper.

---

## 🧩 Hva du lærer i dette repoet

Dette repoet gir deg en praktisk introduksjon til agentisk utvikling:

- Hvordan bygge en enkel agent
- Hvordan bruke verktøy (tools) i agent-systemer
- Hvordan håndtere minne og kontekst
- Hvordan strukturere agent workflows

---

## 📁 Eksempler/Oppgaver

Se sub kataloger for  konkrete implementasjoner/maler:

- `Reiseregning-automatisering/` – Oppgave : En beskrivelse av steg for å sette opp en flyt for å registrere reise regninger
- `Reiseregning-demo/` – resultat : hva som skjer om man følegr oppskriften rått og brutalt uten å gjøre noen endringer, samt ikke bry seg om alt vi har snakket om i teori biten
- `google-workspace-cli/` – en referanse til et eget google workspace CLI som en agent kan utnytte for å hente informasjon fra gmail, calender osv
- Get-Shit-Done/` – en referanse til GSD rammeverket som er rammeverk for utvikling, oppfølging osv.
- teacher-assistent - et eksempel på ren wibe coding i Claude uten særlig mye info i claude.md fil, men en veldig! detalkert prompt
- Kotlin_Java_code_QA_skill - Oppgave der du skal lage en egen skill som gjør kode QA av et stort repo vi vinner på nettet


---

## 🛠️ Teknologier

Du kan bruke valgfri stack, men typisk:
- Python / TypeScript
- LLM API (f.eks. OpenAI)
- Rammeverk (valgfritt): LangChain, Semantic Kernel, etc.

---

## 🎯 Mål

Etter å ha jobbet gjennom dette repoet skal du:
- Forstå hva agentisk utvikling er
- Kunne bygge en enkel agent
- Se hvordan dette kan brukes i virkelige systemer

---

## 📚 Videre lesning

- Prompt engineering
- Tool calling / function calling
- Multi-agent systems
- AI orchestration

---

Happy building! 🤖
