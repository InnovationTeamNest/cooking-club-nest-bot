# -*- coding: utf-8 -*-
from api import api
from common import MAX_MESSAGES

if __name__ == "__main__":
    import os

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

    name = "Sofia"
    try:
        found = 0
        results = []

        for number, member in api.get_number_members_tuple():
            if name.lower() in member.lower():
                results.append(f"\n{member} si trova nel gruppo {str(number)}")
                found += 1
        # E' necessario gestire sia zero persone che troppe (20+) in questo caso
        if found == 0:
            text = "Persona non trovata."
        elif 0 < found < MAX_MESSAGES:
            text = "".join(results)
        else:
            text = f"Troppi risultati trovati ({str(found)}+), prova con un parametro più restrittivo."
    except Exception as ex:
        text = "Errore! Parametro di ricerca non valido."

    print(text)