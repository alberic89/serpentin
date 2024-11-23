#! /bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import time
import random
import yaml
import locale

from PIL import Image, ImageFont, ImageDraw
from slugify import slugify
from datetime import datetime
from tabulate import tabulate as tb


locale.setlocale(locale.LC_TIME, "FR_fr")

new_tabulate = False
try:  # check if tabulate new fmt (after 0.9) is avaible
    import tabulate.version as tb_version

    new_tabulate = True if tb_version.version_tuple[1] >= 9 else False
except ModuleNotFoundError:
    # try to install tabulate for the next execution
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-U", "--user", "tabulate>=0.9.0"]
    )


def get_all_yaml():
    yaml_serpentins = []
    for root, dirs, files in os.walk("."):
        for f in files:
            if os.path.splitext(f)[1] == ".yaml":
                yaml_serpentins.append(
                    yaml.safe_load(
                        open(os.path.join(root, f), "r", encoding="utf_8").read()
                    )
                )
    return yaml_serpentins


def serpentin(classe, salle, rangs_aveugles):
    """!!! Le paramètre classe va être effacé !!!"""

    if len(salle) < rangs_aveugles:
        raise ValueError("La salle est trop petite !")

    classe_rangee = []

    now = time.localtime()

    seed = now[2] * 10000 + now[1] * 100 + now[0]

    random.seed(seed)

    eleves_aveugles = []

    for élève in classe:
        if élève[-1] == "*":
            eleves_aveugles.append(élève[:-1])

    for élève in eleves_aveugles:
        classe.remove(élève + "*")

    nb_places_aveugles = 0

    for rang in salle[:rangs_aveugles]:
        for index, rangée in enumerate(rang):
            if index & 1 == 0:
                nb_places_aveugles += rangée

    if nb_places_aveugles < len(eleves_aveugles):
        raise ValueError("Il n'y a pas assez de rangs aveugles !")

    eleves_heureux = random.sample(classe, nb_places_aveugles - len(eleves_aveugles))

    for élève in eleves_heureux:
        classe.remove(élève)

    eleves_aveugles += eleves_heureux

    random.shuffle(eleves_aveugles)
    random.shuffle(classe)

    classe += eleves_aveugles

    for r, rang in enumerate(salle):
        classe_rangee.append([])
        for rg, rangee in enumerate(rang):
            for place in range(rangee):
                if rg & 1 or len(classe) == 0:
                    classe_rangee[r].append(None)
                else:
                    classe_rangee[r].append(classe.pop())

    return classe_rangee


def print_serpentin(serpentine):
    if new_tabulate:
        table_type = "rounded_grid"
    else:
        table_type = "fancy_grid"

    return tb(
        serpentine,
        tablefmt=table_type,
        stralign="center",
        showindex=True,
    )


def create_serpentin_img(serpentine, classe_name, salle_name, file_name):
    date = datetime.today()
    text_serpentin = (
        f"Classe : {classe_name}      Salle : {salle_name}      Date : {date.strftime('%a %d %b %Y')}\n"
        + print_serpentin(serpentine)
    )

    usr_font = ImageFont.truetype("DejaVuSansMono.ttf", 15)

    image = Image.new("RGBA", (1, 1), (255, 255, 255))

    d_usr = ImageDraw.Draw(image)

    img_sizes = d_usr.multiline_textbbox((7, 7), text_serpentin, font=usr_font)

    image = image.resize((img_sizes[2] + 5, img_sizes[3] + 5))

    d_usr = ImageDraw.Draw(image)

    d_usr = d_usr.multiline_text((7, 7), text_serpentin, (0, 0, 0), font=usr_font)
    image.save(file_name + ".png")


def main():
    yaml_serpentins = get_all_yaml()
    for serpent in yaml_serpentins:
        file_name = slugify(
            serpent["nom de classe"]
            + "_"
            + serpent["nom de salle"]
            + "_"
            + datetime.today().strftime("%d-%m-%Y")
        )
        create_serpentin_img(
            serpentin(serpent["classe"], serpent["salle"], serpent["rangs_aveugles"]),
            serpent["nom de classe"],
            serpent["nom de salle"],
            file_name,
        )


if __name__ == "__main__":
    main()
