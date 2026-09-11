# Sicherheit und Fehlerberichte

Experimentelles lokales Tool ohne zugesagte Wartung oder garantierte Reaktionszeit. Keine zertifizierte Anonymisierung.

Bitte keine echten Coaching-Transkripte, Namen, Dateinamen, Screenshots mit personenbezogenen Inhalten, `.runtime/state.json`, Browser-Sitzungskennungen oder Zugangsdaten in Issues/PRs einstellen. Erkennungsfehler mit frei erfundenen Beispielen reproduzieren. Auch Fehlermeldungen vor dem Teilen prüfen.

Sicherheitslücken, die sensible Daten offenlegen könnten, wenn möglich über GitHubs private Schwachstellenmeldung im Security-Bereich melden, falls verfügbar. Andernfalls zuerst ohne technische Exploit- oder private Datendetails nach einem vertraulichen Kontaktweg fragen. Keine aktive Ausnutzung auf fremden Daten.

Das Projekt lauscht nur auf 127.0.0.1, prüft Host/Origin/Sitzung, lädt nur lokale Webressourcen und sperrt ausgehende Python-Netzwerkaufrufe im Verarbeitungsprozess. Das schützt nicht vor bösartigen Browser-Erweiterungen, Schadsoftware, anderen Benutzern mit Dateizugriff, Betriebssystem-Auslagerung oder Cloud-Backups. Eigene Rollen und Beibehalten-Regeln können bewusst personenbezogene Daten im Ergebnis belassen.

Abhängigkeiten sind für reproduzierbare Tests versioniert. Keine automatische Aktualisierung im Hintergrund. Sicherheitsupdates müssen bewusst geprüft, getestet und veröffentlicht werden.
