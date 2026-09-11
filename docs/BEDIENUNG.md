# Bedienung, Offline-Betrieb und Grenzen

## Erkennen und ersetzen

**Lokales Modell + Regeln** verwendet das installierte `de_core_news_lg` über Presidio Analyzer. Es sucht Personen, Orte und Organisationen aus dem Zusammenhang. Aus vollständigen Personennamen werden Bestandteile abgeleitet, um spätere einzelne Nachnamen im selben Dokument zu ersetzen. Das Modell wird nicht auf den eingegebenen Transkripten nachtrainiert.

**Nur Regeln** führt kein Modell aus. Es verwendet Namenslisten und Muster für Anreden, Beziehungen und Sprecher sowie Kontakte. Unbekannte Nachnamen und Orte können dabei besonders häufig fehlen. Zusätzliche wörtliche Suchlisten für Personen, Orte, Organisationen und andere Angaben sind optional. Je Ausdruck eine Zeile; Schreibvarianten separat ergänzen. Keine automatische Gleichsetzung aller Varianten.

Personen werden normalerweise `[Person]`, Orte `[Ort]`, Organisationen `[Unternehmen]`. E-Mails, typische Telefonnummern, Links, IBANs und numerische Datumsangaben werden zusätzlich über Suchmuster gesucht; diese Muster sind nicht vollständig. Optional alle Ziffernfolgen durch `[Zahl]` ersetzen. Ausgeschriebene Zahlen bleiben erhalten. Sprecheranfänge werden ohne eigene Regel `[Sprecher]:`; die Heuristik kann kurze Überschriften vor einem Doppelpunkt ebenfalls treffen.

## Ausnahmen und Rollen

Unter **Ausnahmen & Rollen festlegen → Regel hinzufügen** Suchausdruck, Aktion und gegebenenfalls Ersatztext eintragen. Beispiel: `Sebastian / Ersetzen durch / Coach` und `Petra / Ersetzen durch / Kundin`. Alternativ `Sebastian / Beibehalten`, um den Namen ausdrücklich lesbar zu lassen.

Die Regeln gelten für alle Dateien des aktuellen Stapels und im gesamten Text. Sie haben Vorrang vor automatischen Treffern, Zusatzlisten und abgewählten Fundlisten-Einträgen. Sie werden genau einmal gegen das Original angewandt; ein Ersatztext wird nicht erneut automatisch ersetzt. Groß-/Kleinschreibung ist egal, einfache Personengenitive werden berücksichtigt. Längere passende Ausdrücke haben Vorrang. Widersprüchliche Regeln für denselben Ausdruck werden abgewiesen.

Vollständige Namen und abweichende Sprecherlabels bei Bedarf separat ergänzen. Eine Vornamensregel gibt einen danebenstehenden Nachnamen nicht automatisch frei: im Fließtext kann `Sebastian Maier` deshalb `Coach [Person]` ergeben. Mit zusätzlichem Eintrag `Sebastian Maier → Coach` wird daraus `Coach`. Bei Sprecherzeilen mit einer passenden Regel ersetzt die gewählte Bezeichnung die gesamte Sprecherangabe vor dem Doppelpunkt. Bei mehreren passenden Regeln stehen ihre Bezeichnungen mit `/` getrennt dort.

Die Regeln bleiben in der Sitzung, werden beim Leeren verworfen und nicht exportiert. Beibehaltene Namen und Ersatztexte stehen ausdrücklich im Ergebnis. Eine Rolle wie „Kundin“ hält Verbindungen zwischen Nennungen aufrecht; sie ist kein Nachweis rechtlicher Anonymität.

## Durchsehen und speichern

Nach Verarbeitung pro Datei **Automatisch gefundene Angaben prüfen** aufklappen. Falsche Treffer abwählen; die Liste kann unvollständig sein. Ausnahmen haben weiterhin Vorrang. Das Abwählen berechnet den Text aus dem Original neu; bei manuellen Änderungen erscheint vorher ein Hinweis.

Danach den gesamten Ergebnistext prüfen. Übersehene Ausdrücke markieren und durch `[Person]`, `[Ort]`, `[Unternehmen]` oder `[Angabe]` überall ersetzen. Das gilt für alle aktuellen Ergebnisse und erhält andere manuelle Bearbeitungen. Alternativ direkt im Ergebnis schreiben oder Text löschen. Beruf, Arbeitgeber, Beziehungen, Familienkonstellationen und seltene Ereignisse gegebenenfalls verallgemeinern.

Durchsicht bestätigen. Ein bestätigter Text wird direkt als UTF-8-TXT gespeichert; mehrere als ZIP mit TXT-Dateien. Ungeprüfte/fehlerhafte Dateien werden nicht exportiert. Eine Änderung setzt den betroffenen Prüfstatus zurück; geänderte Konfiguration erfordert Neuverarbeitung. Neutrale Dateinamen verhindern, dass der ursprüngliche Dateiname im Export erhalten bleibt. Die Inhalte werden nicht erneut nachträglich umgeschrieben: bewusst beibehaltene Angaben bleiben enthalten.

Der Browser nutzt seinen Download-Ordner oder fragt nach einem Speicherort, wenn diese Option in den Browser-Einstellungen aktiviert ist. Keine automatische Speicherung in den Eingabeordner. Originaldateien bleiben unverändert.

## DOCX und Grenzen

DOCX wird als Klartext gelesen, einschließlich Tabellen im Haupttext. Formatierung, Bilder, Kommentare, Fuß-/Endnoten, Kopf-/Fußzeilen und Dokumentmetadaten werden nicht exportiert. Änderungsverfolgung, Textboxen und eingebettete Fremdinhalte werden abgewiesen; gegebenenfalls vorher in Word bewusst als TXT exportieren. TXT muss UTF-8-kodiert sein. Maximal 2 Millionen Zeichen je Dokument.

**Keine Garantie vollständiger, unwiederherstellbarer Anonymität.** Das Modell kann Namen übersehen oder unvollständig abgrenzen; Regeln können harmlose Wörter treffen. Der Kontext kann Personen trotz ersetzter Namen verraten. Die Tests verwenden erfundene Texte, keine repräsentative Evaluation von Coaching-Gesprächen. Ungeklärte sensible Passagen nicht ungeprüft weitergeben.

## Daten auf dem Gerät

Browser und Dienst halten Texte während der Sitzung im Arbeitsspeicher. Die App schreibt keine Gesprächsprotokolle oder Zuordnungstabellen. `.runtime/state.json` enthält nur lokale Port-/Prozess-/Sitzungsdaten. `sessionStorage` hält nur die Sitzungskennung, keine Transkripte. **Sitzung leeren** entfernt die Inhalte aus der Oberfläche; **Beenden** stoppt zusätzlich den Dienst. Downloads bleiben gespeichert.

Dies ist keine forensische Löschung von Speicher, Originalen oder Backups. Unter Windows ersetzt ein Unix-Dateimodus keine Windows-ACLs; verwende einen nur für dich zugänglichen Benutzerordner. Die Anwendung ist für ein einzelnes vertrauenswürdiges Benutzergerät gedacht, nicht als gemeinsam genutzter Netzwerkdienst. Keine öffentlichen Ports, Container-Cloud oder Reverse-Proxies für echte Transkripte einrichten.
