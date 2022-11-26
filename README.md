# Tangram Bot

Dieses Repository beinhaltet den Quellcode, welcher im Rahmen unserer Studienarbeit entwickelt wurde.


## Ausführung

Vor der Ausführung des Codes müssen folgende Schritte durchgeführt werden:

1) **Kameraauflösung**: Auf dem Raspberry Pi des Roboterarms muss die Kameraauflösung in den Konfigurationsdateien `video_server_setup.yaml` und `cam_intrinsics.yaml` auf 1920x1080 Pixel gesetzt werden

2) **Umgebungsvariablen**: In diesem Repository muss eine Kopie der Datei `.env.example` unter dem Namen `.env` angelegt und die darin deklarierten Variablen auf den eigenen Aufbau angepasst werden

Im Anschluss kann der Code über folgenden Befehl ausgeführt werden:

```bash
python src/main.py -e prod
```

### Argumente

| Kurzform | Langform  | Beschreibung | Werte | Default |
|----------|-----------|--------------|-------|---------|
|-e        | --env       | Mit Roboter verbinden oder Mock-Bilder zum Testen nutzen? | `dev` - Mock-Bilder nutzen <br>`prod` - mit Roboter verbinden | `dev`
|-tb       | --trackbars | Config-Fenster mit Slidern sichtbar machen | gesetzt/nicht gesetzt | nicht gesetzt |
|-s        | --sound     | Tonausgabe aktivieren | gesetzt / nicht gesetzt | nicht gesetzt |
