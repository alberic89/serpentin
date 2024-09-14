from tabulate import tabulate
from PIL import Image, ImageFont, ImageDraw
import random
import yaml
import os
from slugify import slugify
from datetime import datetime


def get_all_yaml():
    yaml_serpentins = []
    for root, dirs, files in os.walk('.'):
        for f in files:
            # print(os.path.join(root,f))
            if os.path.splitext(f)[1] == ".yaml":
                yaml_serpentins.append(
                    yaml.safe_load(
                        open(os.path.join(root, f), "r")
                    )
                )
    return yaml_serpentins


def salle_check(salle):
    n = max(sum(_) for _ in salle)
    for r, rang in enumerate(salle):
        if sum(rang) != n:
            salle[r][-1] = n - sum(rang[:-1])
    return None


def serpentin(classe, salle):
    salle_check(salle)

    classe_cpy = classe.copy()
    classe_rangee = []

    random.seed()
    random.shuffle(classe_cpy)

    for r, rang in enumerate(salle):
        classe_rangee.append([])
        for rg, rangee in enumerate(rang):
            for place in range(rangee):
                if rg & 1 or len(classe_cpy) == 0:
                    classe_rangee[r].append(None)
                else:
                    classe_rangee[r].append(classe_cpy.pop())

    return classe_rangee


def print_serpentin(serpentin):
    return tabulate(
        serpentin,
        tablefmt="rounded_grid",
        stralign="center",
        showindex=True,
    )


def create_serpentin_img(serpentin, classe_name, salle_name, file_name):
    text_serpentin = f"CLASSE: {classe_name}         SALLE: {salle_name}\n" + \
        print_serpentin(serpentin)

    usr_font = ImageFont.truetype("DejaVuSansMono.ttf", 15)

    image = Image.new(
        "RGBA", (1, 1), (255, 255, 255)
    )

    d_usr = ImageDraw.Draw(image)

    img_sizes = d_usr.multiline_textbbox(
        (10, 10), text_serpentin, font=usr_font)

    image = image.resize((img_sizes[2] + 15, img_sizes[3] + 10))

    d_usr = ImageDraw.Draw(image)

    d_usr = d_usr.multiline_text(
        (10, 10), text_serpentin, (0, 0, 0), font=usr_font)
    image.save(file_name + ".png")


def main():
    yaml_serpentins = get_all_yaml()
    for serpent in yaml_serpentins:
        file_name = slugify(serpent["nom de classe"] + "_" +
                            serpent["nom de salle"] + "_" +
                            datetime.today().strftime('%d-%m-%Y')
                            )
        create_serpentin_img(
            serpentin(serpent["classe"], serpent["salle"]),
            serpent["nom de classe"], serpent["nom de salle"], file_name
        )


if __name__ == "__main__":
    main()
