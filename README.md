# Transkript-Werkstatt

[![Mac, Windows and Linux](https://github.com/SebastianMaierOfficial/transkript-werkstatt/actions/workflows/tests.yml/badge.svg)](https://github.com/SebastianMaierOfficial/transkript-werkstatt/actions/workflows/tests.yml)

Eine kleine, lokal laufende Browser-Anwendung, die beim Bereinigen deutschsprachiger Coaching-Transkripte hilft. Mehrere TXT- oder DOCX-Dateien auswählen, personenbezogene Angaben ersetzen, Ergebnisse durchsehen und speichern. Nach einmaliger Installation funktioniert die Verarbeitung ohne Internet und ohne Cloud-KI. Kein Konto, kein API-Schlüssel und kein Codex erforderlich.

**Experimentelles Werkzeug zum Ausprobieren, keine garantierte Anonymisierung.** Die Erkennung kann Angaben übersehen oder falsch ersetzen. Auch Lebensgeschichten, Berufe und Beziehungen können Personen identifizierbar machen. Jeden Ergebnistext vor einer Weitergabe vollständig prüfen. Das Projekt ersetzt weder Datenschutzprüfung noch fachliche oder rechtliche Beratung.

## Was es kann

- Lokales deutsches spaCy-Modell über Presidio Analyzer: Personen, Orte und Organisationen aus dem Zusammenhang suchen; Namenslisten und Muster ergänzen die Erkennung.
- Optionaler Modus **Nur Regeln**, der kein KI-Modell ausführt.
- Allgemeine Hinweise wie `[Person]`, `[Ort]`, `[Unternehmen]`, `[E-Mail]` statt individueller Nummern oder reversibler Codes.
- Eigene Ausnahmen: `Sebastian → Coach`, `Petra → Kundin` oder einen Namen bewusst beibehalten. Die Regeln gelten auch für Sprecherzeilen.
- Fundlisten prüfen, Fehlalarme abwählen und Ergebnistext direkt bearbeiten.
- **Ein geprüfter Text als TXT; mehrere geprüfte Texte als ZIP.** Neutrale Dateinamen; keine Originale, Fundlisten oder Zuordnungstabellen im Export.
- Ein erfundenes Beispiel zum Testen ohne echte Gesprächsdaten.

Beispiel mit den beiden Rollenregeln:

```text
Sebastian: Wie geht es Petra?
Petra: Ich habe Thomas Müller in München getroffen.
```

```text
Coach: Wie geht es Kundin?
Kundin: Ich habe [Person] in [Ort] getroffen.
```

Das ist ein Funktionsbeispiel, kein Nachweis einer vollständigen Erkennungsquote.

## Installation und Start

1. [Quellcode herunterladen](https://github.com/SebastianMaierOfficial/transkript-werkstatt/archive/refs/heads/main.zip) und **vollständig entpacken**, oder das Repository klonen.
2. Python **3.12** oder [uv](https://docs.astral.sh/uv/getting-started/installation/) bereitstellen. uv kann die passende Python-Version installieren.
3. **Mac:** `Install-Mac.command` ausführen. **Windows:** `Install-Windows.cmd` ausführen. Die Installation lädt Softwarepakete und das Modell herunter und führt einen Offline-Selbsttest aus.
4. Danach **`Start-Mac.command`** bzw. **`Start-Windows.cmd`** öffnen. Der Standardbrowser öffnet die Anwendung auf `127.0.0.1`. Beim normalen Start wird nichts nachgeladen.

Die [ausführliche Installationsanleitung](docs/INSTALLATION.md) enthält Terminal-Befehle, Windows-Hinweise und Lösungen für typische Startprobleme. [AGENTS.md](AGENTS.md) erklärt Coding-Agents den Installations-, Test- und Übergabeablauf.

Die Python-Umgebung wird lokal im Projektordner `.venv` angelegt. Das Modell hat ungefähr 568 MB Downloadgröße; zusätzlich werden Python und Bibliotheken benötigt. Mehrere GB freier Speicher sind sinnvoll. Das ist eine Quellcode-Veröffentlichung mit Startskripten, keine signierte `.app` oder `.exe`.

## Nutzung und Speicherort

1. TXT (UTF-8) oder DOCX auswählen. Bis zu 50 Dateien, je 10 MB, insgesamt 40 MB.
2. Modellmodus auswählen. Bei Bedarf unter **Ausnahmen & Rollen festlegen** Regeln ergänzen. Die anderen Korrekturfelder können leer bleiben.
3. Verarbeiten, automatische Funde und den **gesamten Inhalt** prüfen. Übersehene Angaben markieren und überall ersetzen oder direkt bearbeiten.
4. Durchsicht pro Text bestätigen und speichern. Nach Regeländerungen erneut verarbeiten; nach Textänderungen erneut prüfen.
5. **Sitzung leeren** verwirft Inhalte und Regeln aus der Oberfläche. **Beenden** stoppt zusätzlich den lokalen Dienst. Ein geschlossener Tab allein beendet ihn nicht.

Der Browser bestimmt den Speicherort, normalerweise seinen Download-Ordner. In Chrome/Edge lässt sich unter **Einstellungen → Downloads → Vor dem Download nach dem Speicherort fragen** die Ordnerwahl aktivieren. [Chrome-Dokumentation](https://support.google.com/chrome/answer/95759?hl=de). Die Website kann den Download-Ordner nicht stillschweigend umstellen. Ein einzelner Text heißt `transkript-001.txt`; mehrere liegen als TXT-Dateien in `gepruefte-transkripte.zip`. Bereits vorhandene gleichnamige Dateien behandelt der Browser nach seinen Einstellungen.

Mehr zu Regeln, DOCX-Grenzen und Offline-Nutzung: [Bedienung und Datenschutz](docs/BEDIENUNG.md).

## Lokal bedeutet hier

Die Anwendung sendet keine Transkripte an externe Dienste. Sie lädt weder externe Schriftarten noch Telemetrie. Browser und Python-Dienst kommunizieren ausschließlich über die lokale Loopback-Adresse. Der Dienst verarbeitet Inhalte im Arbeitsspeicher und führt keine Transkriptprotokolle. Zur Laufzeit werden ausgehende Python-Socket- und DNS-Aufrufe zusätzlich gesperrt; der Modelladapter lädt nur das bereits installierte Modell. Fehler führen nicht zu einem stillen Wechsel auf eine schwächere Erkennung.

Die Sperre ist keine Betriebssystem-Firewall. Browser-Erweiterungen, Cloud-Synchronisierung von Downloads, Betriebssystem-Auslagerung und Backups liegen außerhalb dieses Tools. Originaldateien werden nicht gelöscht; es gibt keine forensische Speicherbereinigung. Verwende passende lokale Ordner und prüfe deine Geräte- und Browserkonfiguration.

## Verwendete Projekte und Lizenzen

Dieses Projekt steht unter der [MIT-Lizenz](LICENSE). Es nutzt:

| Projekt | Zweck | Lizenz / Quelle |
| --- | --- | --- |
| [Presidio](https://presidio.dataprivacystack.org/) | Erkennung integrieren und Treffer ersetzen | MIT, [Repository](https://github.com/data-privacy-stack/presidio) |
| [spaCy](https://spacy.io/) | Lokale Eigennamenerkennung | MIT, [Repository](https://github.com/explosion/spaCy) |
| [de_core_news_lg 3.8.0](https://github.com/explosion/spacy-models/releases/tag/de_core_news_lg-3.8.0) | Deutsches trainiertes Modell | MIT; zusätzliche Quellenhinweise des Modells beachten |
| [Faker 37.12.0](https://github.com/joke2k/faker/tree/v37.12.0/faker/providers/person) | Herkunft der statischen Namenslisten | MIT; Faker läuft nicht während der Verarbeitung |
| [Python](https://www.python.org/) | Lokaler Dienst und Dateiverarbeitung | PSF License; separat installiert |
| [uv](https://docs.astral.sh/uv/) (optional) | Python für die Installation bereitstellen | MIT / Apache-2.0; separat installiert |

Lizenztexte und genaue Herkunft: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Modellgewichte, Python und Drittbibliotheken werden nicht in diesem Quellcode-Repository mitgeliefert. Es besteht keine offizielle Verbindung zu oder Empfehlung durch die genannten Projekte.

## Verantwortung und Grenzen

Die Software wird **„wie besehen“ ohne Zusicherung oder Gewährleistung** bereitgestellt. Nutzung und Entscheidung über die Weitergabe von Ergebnissen liegen bei den Nutzenden. Die MIT-Lizenz enthält einen Gewährleistungs- und Haftungsausschluss; dieser gilt nur im rechtlich zulässigen Umfang. Zwingende gesetzliche Rechte werden dadurch nicht ausgeschlossen.

Es gibt keine Zusage vollständiger Anonymität, DSGVO-Konformität, AI-Act-Ausnahme, Sicherheitszertifizierung, Wartung oder Eignung für einen bestimmten Zweck. Das Modell ist auf geschriebenen deutschen Nachrichtentexten trainiert, nicht speziell auf Coaching-Sessions. „Kundin“ enthält zwar keinen Originalnamen, erhält aber Zusammenhänge ihrer Erwähnungen. Auch solche Ergebnisse können personenbezogen bleiben.

Bitte **keine echten Transkripte, Namen, Screenshots mit Klientendaten oder Sitzungskennungen in GitHub-Issues hochladen**. Fehler ausschließlich anhand erfundener Beispiele beschreiben. Siehe [SECURITY.md](SECURITY.md).

## Entwicklung und Tests

```sh
# Mac / Linux, nach Installation
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python offline_check.py
node --test tests/replacement.test.cjs
```

Unter Windows `.venv\Scripts\python.exe` verwenden. Node wird nur für die JavaScript-Tests benötigt, nicht für die Anwendung. GitHub Actions prüft frische Installationen, Modellbetrieb ohne ausgehende Python-Netzwerkaufrufe, HTTP-Verarbeitung, DOCX, Rollen, Export und Prüfstatus auf macOS, Windows und Linux. Den tatsächlichen aktuellen Teststatus zeigt der Workflow oben; automatisierte Tests ersetzen keinen manuellen Test jeder Geräte-/Browserkombination.
