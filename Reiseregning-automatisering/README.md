# 💻 Claude Code oppgave: Reiseregning-automatisering

## 🎯 Mål

Deltakerne skal:

- bruke Claude Code i **planning mode**
- la agenten designe arkitektur
- få den til å generere kode
- iterere som en “tech lead”

---

## 🧱 Hva de skal bygge

En enkel CLI-app som:

- tar inn en kvittering (tekst/mock)  
- ekstraherer info (fake AI / parsing)  
- validerer data  
- gir feedback til bruker  
- lager en “expense report”  

👉 **Viktig:** ikke perfeksjon — fokus på agentisk flyt

---

## ⚙️ Setup

Dere skal **ikke kode manuelt**.  
Dere skal styre Claude.

---

## 🔁 STEG 1: Start i planning mode

Skriv i Claude Code:

```text
You are a senior software architect.

Do NOT write any code yet.

I want to build a CLI tool for handling expense reports.

The tool should:

accept receipt input (text for now)
extract relevant fields (date, amount, category)
validate the data
output a structured expense report

First:

ask clarifying questions
identify edge cases
propose possible architectures

Wait for my answers before continuing.
```

### 💡 Hva skjer her

Claude vil:

- stille spørsmål som:
  - “What format is the input?”
  - “Should validation follow rules?”
- foreslå arkitektur  

👉 Dette er **agentisk kickoff**

---

## 🧩 STEG 2: Svar + få plan

Etter spørsmålene:

```text
Answer with reasonable assumptions if something is unclear.

Now create a detailed implementation plan.

Include:

project structure
modules/functions
data flow
validation logic
future extensibility
```

💥 **Viktig:**  
👉 Ikke godta første plan – forbedre den

---

## 🔍 STEG 3: Kritisk review

```text
Critically review this plan:

what is overengineered?
what is missing?
how can we simplify it for an MVP?
Then improve the plan.
```

---

## 🧱 STEG 4: Generer kode (nå skjer det)

```text
Now implement the project based on the improved plan.

Requirements:

simple and clean code
runnable locally
include sample input
include basic validation

Explain how to run it.
```

### 💡 Typisk output

Claude lager f.eks:

```
expense_app/
├── main.py
├── parser.py
├── validator.py
└── models.py
```

---

## ▶️ STEG 5: Kjør og test

Etter kjøring:

```text
Create 3 test cases:

valid receipt
missing date
suspiciously high amount

Show expected outputs.
```

---

## 🔁 STEG 6: Iterasjon (her skjer magien)

Be dem bruke Claude som utvikler:

**Eksempler:**

- Improve error handling  
- Refactor the code to be more modular  
- Add logging to show agent-like steps  
- Make the CLI interactive  

---

## 🤖 STEG 7: Gjør det “agentisk”

```text
Transform this into a multi-agent system.

Define:

a parser agent
a validation agent
a feedback agent

Refactor the code to reflect this architecture.
```

💥 Nå begynner du å “tenke agenter i kode”

---

## 🚀 STEG 8: (BONUS) Simuler ekte AI

```text
Replace the parser with a mock AI function that simulates OCR extraction.

Make it slightly unreliable to simulate real-world issues.
```

---

## 🌍 STEG 9: (BONUS) Deploy mindset

```text
How could this be turned into:

an API
a web app

Give a step-by-step plan.
```

---

## 🌍 STEG 10: (CRITICAL) MEASURE EFFECT

Hvordan kan vi måle om dette systemet er vellykket?

Gi konkrete KPIer og hvordan de måles.
- 💡 Typiske KPIer:
- ⏱️ behandlingstid (fra 10 dager → 1 dag)
- ❌ feilrate
- 😊 bruker-tilfredshet
- 🔁 antall manuelle steg
---


## 🧑‍🏫 Hvordan du fasiliterer live

### ⏱️ Tidsplan (45–60 min)

- Planning mode → 10 min  
- Plan + review → 10 min  
- Code gen → 10 min  
- Testing → 10 min  
- Iteration → 10 min  
- Demo → 10 min  

---

## 🔥 Viktige læringspoeng

- **Intent > kode**  
  → “Dere skrev nesten ingen kode – men bygde en app”

- **Planning mode = cheat code**  
  → “Dette er forskjellen på mediocre og powerful bruk”

- **Claude = team**  
  → “Dette er ikke et verktøy – det er et team”

---

## ⚠️ Vanlige feil

- Hopper over planning mode  
- Tar første svar som fasit  
- Itererer ikke  
- Gjør manuell kode i stedet for å styre AI  
