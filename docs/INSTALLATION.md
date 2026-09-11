# Installation auf Mac und Windows

Benötigt: ein beschreibbarer lokaler Ordner, Internet für die Ersteinrichtung, ein aktueller Browser sowie Python 3.12. Empfohlener Weg: **uv** stellt eine aktuelle Python-3.12-Version bereit. Python und die installierten Pakete bleiben nach der Einrichtung auf dem Gerät; spätere Verarbeitung braucht keine Internetverbindung. Keine API-Schlüssel erforderlich.

## 1. Projekt herunterladen

[Download ZIP](https://github.com/SebastianMaierOfficial/transkript-werkstatt/archive/refs/heads/main.zip), danach vollständig entpacken. Nicht aus der ZIP heraus starten. Lege den Ordner an einen lokalen, beschreibbaren Ort. Alternativ:

```sh
git clone https://github.com/SebastianMaierOfficial/transkript-werkstatt.git
cd transkript-werkstatt
```

Den gesamten Ordner zusammenlassen. Eine installierte `.venv` kann nicht zuverlässig auf einen anderen Rechner oder Pfad kopiert werden: auf dem Zielgerät neu installieren.

## 2. Python bereitstellen

Falls bereits eine aktuelle Python-3.12-Version installiert ist, kann sie direkt verwendet werden. Ansonsten uv über die [offizielle Anleitung](https://docs.astral.sh/uv/getting-started/installation/) installieren. Beispiele für vorhandene Paketmanager:

Mac mit Homebrew:

```sh
brew install uv
```

Windows mit WinGet:

```powershell
winget install --id=astral-sh.uv -e
```

Danach das Terminal neu öffnen, damit `uv` gefunden wird. Ohne diese Paketmanager die offiziellen uv-Installationsmöglichkeiten verwenden. Die folgenden Installationsskripte nutzen `uv run --python 3.12 --no-project install.py`; uv lädt bei Bedarf Python 3.12. Die Anwendung selbst startet später direkt über `.venv`, ohne uv oder Downloads aufzurufen.

## 3. Einmalig installieren

**Mac:** `Install-Mac.command` doppelklicken. Alternativ im Terminal im entpackten Projektordner:

```sh
bash Install-Mac.command
```

**Windows:** `Install-Windows.cmd` doppelklicken. Alternativ in PowerShell im Projektordner:

```powershell
.\Install-Windows.cmd
```

Für Agents / Terminals ohne interaktive Pause, auf beiden Systemen:

```sh
uv run --python 3.12 --no-project install.py
```

Mit vorhandenem Python statt uv: `python3.12 install.py` auf Mac oder `py -3.12 install.py` auf Windows.

Die Installation erstellt `.venv`, installiert die festgelegten Paketversionen von PyPI und das deutsche Modell aus dem offiziellen spaCy-Release. Das Modell allein ist etwa 568 MB groß; insgesamt mehrere GB freien Platz einplanen. Die Laufzeit erhält keine Gesprächsdateien. Zum Schluss muss **Offline-Selbsttest OK** erscheinen. Bei einem Fehler nicht mit echten Daten weiterarbeiten: Fehlermeldung prüfen und Installation erneut ausführen. Nicht TLS-Prüfung oder Systemschutz ausschalten.

## 4. Starten – danach auch offline

Mac: `Start-Mac.command` doppelklicken oder `bash Start-Mac.command` ausführen.

Windows: `Start-Windows.cmd` doppelklicken oder `.\Start-Windows.cmd` ausführen.

Der Standardbrowser öffnet die lokale Adresse `http://127.0.0.1:…`. Diese Adresse ist kein öffentliches Hosting. Die Sitzungskennung in der Startadresse nicht weitergeben. Nach dem Öffnen entfernt die Oberfläche sie aus der sichtbaren Adresszeile. Bei einem neuen Start kann sich der Port ändern: lieber das Startskript benutzen als ein altes Lesezeichen.

Zunächst **Mit erfundenem Beispiel ausprobieren** nutzen. Erst nach erfolgreichem Test eigene Dateien auswählen. Über **Beenden** den lokalen Dienst stoppen; ein geschlossenes Browserfenster allein stoppt ihn nicht.

## Offline selbst prüfen

Nach abgeschlossener Installation WLAN bzw. Internet trennen, Startskript öffnen, Beispiel verarbeiten und speichern. Die Anwendung muss dabei wie zuvor funktionieren.

Zusätzlicher technischer Selbsttest mit aktiver Sperre ausgehender Python-Verbindungen:

```sh
# Mac
.venv/bin/python offline_check.py
```

```powershell
# Windows
.venv\Scripts\python.exe offline_check.py
```

Dieser Test lädt das Modell und verarbeitet nur erfundene Angaben. Er ist kein Beweis, dass andere Programme, Browser-Erweiterungen oder synchronisierte Ordner keine Daten übertragen.

## Speicherort, Updates und Fehler

- Einzelne Ergebnisse werden als TXT, mehrere als ZIP heruntergeladen. Es gilt der Download-Ordner des Browsers. Für eine Ordnerauswahl dessen Einstellung **Vor dem Download nach dem Speicherort fragen** aktivieren.
- Keine Administratorrechte für das Projekt erforderlich. Unter Windows einen beschreibbaren Benutzerordner verwenden, nicht `Program Files`. Windows ARM und ältere macOS-Versionen sind nicht separat validiert; die Verfügbarkeit der Python-Paket-Wheels ist entscheidend.
- macOS kann heruntergeladene Skripte zurückhalten; es gibt keine signierte App. Den Quellcode prüfen und die oben genannte Terminal-Alternative verwenden. Sicherheitsmechanismen nicht pauschal deaktivieren. In verwalteten Umgebungen die IT einbeziehen.
- Falls sich `.command` nicht ausführen lässt: `bash Start-Mac.command` verwenden. Beim Klonen sind die Ausführungsrechte enthalten; manche ZIP-Programme erhalten sie nicht.
- Falls `uv` fehlt: Terminal neu öffnen oder dessen Installation prüfen. Alternativ die passende Python-Version direkt benutzen.
- Falls der Browser nicht aufgeht: Das Startskript zeigt bei fehlgeschlagenem automatischem Öffnen die lokale URL an. Diese im Browser öffnen. Nicht `app/index.html` direkt öffnen.
- Für Updates erst Ergebnisse speichern und **Beenden**, dann Quellcode aktualisieren und Installation erneut ausführen. Keine automatische Aktualisierung während der Verarbeitung.
- Zum Deinstallieren zuerst **Beenden**, dann den Projektordner über den Papierkorb entfernen. Downloads und Originaldateien bleiben bestehen. Python/uv separat nur entfernen, wenn andere Anwendungen sie nicht brauchen.
