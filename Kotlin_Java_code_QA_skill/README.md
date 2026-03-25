# Kotlin/Java Code QA Skill — Oppgavebeskrivelse og retningslinjer

## Bakgrunn

Dette dokumentet beskriver oppgaven med å lage en **code QA skill** for Kotlin og Java,
til bruk i Claude Code og andre agentmiljøer som støtter `npx skills`-systemet.

En skill er en pakket instruksjonsfil (`SKILL.md`) som gir Claude spesialisert kunnskap og
arbeidsflyt for et avgrenset domene. Skills installeres lokalt i et prosjekt og spores via
`skills-lock.json` — en låsefil som fungerer analogt med `package-lock.json` i npm.

---

## Hva skillen skal gjøre

Skillen skal gjennomføre en grundig kodegjennomgang av Kotlin- og/eller Java-kode med fokus på:

- **Korrekthet** — logiske feil, farlige operasjoner, ukorrekt ressurshåndtering
- **Idiomatisk stil** — unødvendig Java-stil i Kotlin, manglende bruk av språkfunksjoner
- **Ytelse** — unødvendige allokeringer, ineffektive collections-operasjoner
- **Sikkerhet** — hardkodede credentials, SQL-injeksjon, usikker deserialisering
- **Testbarhet** — kode som er vanskelig å enhetsteste, manglende isolasjon i tester
- **Arkitektur** — brudd på SOLID-prinsipper, for sterk kobling

---

## Filstruktur

```
kotlin-java-qa/
├── SKILL.md                    ← Hoveddokument (triggering + arbeidsflyt)
└── references/
    ├── kotlin-rules.md         ← Kotlin-spesifikke regler og antipatterns
    ├── java-rules.md           ← Java-spesifikke regler og antipatterns
    └── severity-guide.md       ← Vektingsregler og rapportformat
```

### Prinsipp for selektiv lasting

Skillen skal **bare laste relevante referansefiler**:

- Ren Kotlin-kode → les kun `kotlin-rules.md`
- Ren Java-kode → les kun `java-rules.md`
- Blandet prosjekt → les begge

---

## SKILL.md — Anbefalt innhold

### Frontmatter

```yaml
---
name: kotlin-java-qa
description: >
  Perform thorough code quality review of Kotlin and/or Java codebases or files.
  Use this skill whenever the user asks to review, audit, analyze, QA, or check
  code quality in Kotlin or Java projects — even if they just say "look at this
  code" or "anything wrong here?" and the files are .kt or .java. Covers
  correctness, idiomatic style, performance, security, testability, and
  architecture concerns. Always use this skill for Kotlin/Java QA tasks.
---
```

> **Viktig:** Description-feltet er den primære triggermekanismen. Det må inkludere
> konkrete fraser brukere faktisk bruker ("sjekk koden", "noe galt her", "audit"),
> og eksplisitt nevne `.kt` og `.java` for å unngå undertriggering.

### Arbeidsflyt i SKILL.md

```markdown
## Workflow

### 1. Scope the review
- Enkeltfil, modul eller fullt repo?
- For repos: start med build-filer (build.gradle.kts / pom.xml),
  deretter entry points, domenelogikk, og til slutt tester.

### 2. Gather context
- Detekter språkversjon (Kotlin 1.x/2.x, Java 11/17/21+)
- Detekter rammeverk (Spring Boot, Ktor, Android, plain JVM)
- Noter testframework (JUnit 5, Kotest, Mockk, Mockito)

### 3. Load reference files
- Kotlin → les references/kotlin-rules.md
- Java → les references/java-rules.md

### 4. Analyze
- Gå gjennom koden systematisk etter kategoriene i referansefilene
- Registrer funn med filnavn og linjenummer

### 5. Report
- Bruk standardformatet beskrevet nedenfor
```

---

## Referansefiler

### kotlin-rules.md — Kategorier

| Kategori | Eksempler på funn |
|---|---|
| **Nullability** | `!!`-operatørbruk, unsafe casts, manglende `?.let`-chains |
| **Coroutines** | `runBlocking` i produksjonskode, `GlobalScope`, manglende `SupervisorJob` |
| **Idiomatic Kotlin** | `object : Runnable {}` i stedet for lambda, misbruk av `apply`/`let`/`run` |
| **Data classes** | Mutable `var` i data classes, manglende `copy()`-bruk |
| **Collections** | `.forEach` med sideeffekter, unødvendig `.toList()` |
| **Exceptions** | `catch (e: Exception)` uten re-throw, svelging av exceptions |
| **Testing** | Manglende `@Test`-isolasjon, shared mutable state i tester |
| **Security** | Hardkodede credentials, SQL-strenger uten parameterisering |

### java-rules.md — Kategorier

| Kategori | Eksempler på funn |
|---|---|
| **Null handling** | Manglende `Optional`, NPE-risiko uten null-sjekk |
| **Resource management** | Manglende `try-with-resources`, lekkende streams |
| **Concurrency** | Usikker delt state, manglende `volatile`/`synchronized` |
| **Generics** | Raw types, unødvendige casts |
| **Collections** | Mutable collections eksponert i API, `ArrayList` der `List` holder |
| **Exceptions** | Checked exceptions svelget, for bred `catch` |
| **Modern Java** | `for`-løkker som burde vært streams, `StringBuffer` i stedet for `StringBuilder` |
| **Security** | Hardkodede secrets, usikker deserialisering |

---

## Rapportformat

Skillen skal alltid returnere funn i dette standardformatet:

```
## QA Report: [fil eller modul]
Språk: Kotlin 1.9 / Spring Boot 3.x
Gjennomgått: X filer, Y linjer

---

### 🔴 Critical (N)
- [Filnavn.kt:45] Unsafe `!!` på nullable returnverdi fra ekstern API.
  Risiko: NullPointerException i produksjon.
  Forslag: Bruk `?.let { }` eller eksplisitt feilhåndtering.

- [Filnavn.kt:112] `runBlocking` i UI-thread vil forårsake ANR på Android.
  Forslag: Bruk `lifecycleScope.launch` i stedet.

---

### 🟡 Warning (N)
- [Service.kt:23] `GlobalScope.launch` — bruk strukturert concurrency.
  Forslag: Injiser en `CoroutineScope` via konstruktør.

---

### 🟢 Style / Idiomatic (N)
- [Model.kt:8] `var` i data class bør være `val` om ikke mutabilitet er nødvendig.

---

### ✅ Positive observasjoner
- God bruk av `sealed class` for tilstandsmodellering i [Domain.kt]
- Konsistent bruk av `Result`-type for feilhåndtering

---

### Oppsummering
X critical, Y warnings, Z style-funn.

Prioritert tiltaksliste:
1. Fiks critical-funn i [fil] — linje 45 og 112
2. Erstatt GlobalScope i [Service.kt]
3. Vurder `val` i data classes
```

---

## Test-repo: thunderbird/thunderbird-android

For å teste og validere skillen anbefales **Thunderbird for Android**:

```bash
git clone https://github.com/thunderbird/thunderbird-android
```

**Hvorfor dette repoet er godt egnet:**

- Stor, reell Kotlin/Java-kodebase (e-postklient for Android)
- Blanding av eldre Java og moderne Kotlin — tester begge regelfilene
- Inneholder coroutines, dependency injection og threading-utfordringer
- Har både god kode og teknisk gjeld — gir variasjon i funn
- Aktivt vedlikeholdt og godt kjent prosjekt

**Anbefalte startpunkter for review:**

| Mappe | Innhold |
|---|---|
| `app-k9mail/src/main/java/com/fsck/k9/` | Eldre Java-kode — god for Java-regelsettet |
| `feature/account/src/main/kotlin/` | Nyere Kotlin — god for Kotlin-regelsettet |
| `core/ui/compose/` | Jetpack Compose + coroutines — tester avanserte regler |

---

## Nøkkelråd for implementasjon

### 1. Description-feltet er avgjørende
Inkluder eksplisitt `.kt` og `.java`, og fraser brukere faktisk bruker:
"sjekk koden", "noe galt her", "audit", "review", "QA".
Legg til en tydelig oppfordring om alltid å bruke skillen for Kotlin/Java-oppgaver.

### 2. Bruk severity-nivåer konsekvent
Three nivåer er tilstrekkelig: **Critical / Warning / Style**.
Unngå for mange nivåer — det gjør rapporten vanskeligere å lese.

### 3. Last referansefiler selektivt
Ikke last begge referansefilene for ren Kotlin eller ren Java.
Dette holder kontekstvinduet effektivt og reduserer støy.

### 4. Inkluder positive observasjoner
Et "Positive observasjoner"-felt gjør rapporten mer balansert
og handlingsrettet — ikke bare en feiliste.

### 5. Test mot begge scopes
Skillen bør håndtere både enkeltfiler og hele moduler/repoer.
Test eksplisitt begge variantene under utvikling.

### 6. Inkluder alltid linjenummer
Funn uten linjenummer er vanskelig å handle på.
Format: `[Filnavn.kt:42]` for alle funn.

---

## Neste steg

1. Skriv `SKILL.md` med frontmatter og arbeidsflyt
2. Skriv `references/kotlin-rules.md` og `references/java-rules.md`
3. Klon thunderbird/thunderbird-android
4. Kjør skillen mot utvalgte filer og evaluer rapportkvaliteten
5. Juster regler og severity-grenser basert på funn
6. Pakk skillen: `python -m scripts.package_skill kotlin-java-qa/`
7. Installer: `npx skills add <path-til-.skill-fil>`
