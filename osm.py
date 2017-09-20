__author__ = 'Zeljko Vukovic zeljkov@uns.ac.rs'

from osmapi import OsmApi
import sys

cyr_to_lat = {
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E',
    'Ж': 'Ž', 'З': 'Z', 'И': 'I', 'Ј': 'J', 'К': 'K', 'Л': 'L',
    'М': 'M', 'Н': 'N', 'Њ': 'Nj', 'О': 'O', 'П': 'P', 'Р': 'R',
    'С': 'S', 'Т': 'T', 'Ћ': 'Ć', 'У': 'U', 'Ф': 'F', 'Х': 'H',
    'Ц': 'C', 'Ч': 'Č', 'Џ': 'Dž', 'Ш': 'Š', 'Ђ': 'Đ', 'Љ': 'Lj',
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e',
    'ж': 'ž', 'з': 'z', 'и': 'i', 'ј': 'j', 'к': 'k', 'л': 'l',
    'љ': 'lj','м': 'm', 'н': 'n', 'њ': 'nj', 'о': 'o', 'п': 'p',
    'р': 'r', 'с': 's', 'т': 't', 'ћ': 'ć', 'у': 'u', 'ф': 'f',
    'х': 'h', 'ц': 'c', 'ч': 'č', 'џ': 'dž', 'ш': 'š', 'ђ': 'đ'}

cyr_to_lat_ai = {
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E',
    'Ж': 'Z', 'З': 'Z', 'И': 'I', 'Ј': 'J', 'К': 'K', 'Л': 'L',
    'М': 'M', 'Н': 'N', 'Њ': 'Nj', 'О': 'O', 'П': 'P', 'Р': 'R',
    'С': 'S', 'Т': 'T', 'Ћ': 'C', 'У': 'U', 'Ф': 'F', 'Х': 'H',
    'Ц': 'C', 'Ч': 'C', 'Џ': 'Dz', 'Ш': 'S', 'Ђ': 'Dj', 'Љ': 'Lj',
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e',
    'ж': 'z', 'з': 'z', 'и': 'i', 'ј': 'j', 'к': 'k', 'л': 'l',
    'љ': 'lj','м': 'm', 'н': 'n', 'њ': 'nj', 'о': 'o', 'п': 'p',
    'р': 'r', 'с': 's', 'т': 't', 'ћ': 'c', 'у': 'u', 'ф': 'f',
    'х': 'h', 'ц': 'c', 'ч': 'c', 'џ': 'dz', 'ш': 's', 'ђ': 'dj'}


def convert(text, mapping):
    out = ''
    for c in text:
        out += mapping[c]
    return out


def is_in_cyrilic(text):
    """

    :rtype : bool
    """
    for char in text:
        if char not in cyr_to_lat.keys():
            return False
    return True


def get_cyrilic_tag(tags):
    for key, value in tags.items():
        if is_in_cyrilic(value):
            return key
    return None


def slicedict(d, s):
    return {k: v for k, v in d.items() if k.startswith(s)}


def get_name_tags(node):
    tags = node['data']['tag']
    tags = slicedict(tags, 'name')

    return tags

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def changeset(nodes_to_fix, conversion, first_tag_choice, second_tag_choice, name):
    if len(nodes_to_fix) == 0:
        return

    question = "Make " + name + " changeset?"
    if not query_yes_no(question, "no"):
        return

    print("Making changeset ...")
    api.ChangesetCreate({u"comment": u"Serbian transliteration bot. Converting cyrilic street names to latin",
                         u"tag": u"mechanical=yes"})

    results = []

    for node in nodes_to_fix:
        tags = get_name_tags(node)
        cir_tag = get_cyrilic_tag(tags)
        in_cyrilic = tags[cir_tag]

        # try not to overwrite existing tags
        tag_name = first_tag_choice
        if tag_name in tags.keys():
            tag_name = second_tag_choice

        node['data']['tag'][tag_name] = convert(in_cyrilic, conversion)
        results.append(api.WayUpdate(node['data']))

    print("Closing...")
    api.ChangesetClose()
    print("Done.")


###################################

if __name__ == "__main__":

    user = input("Username: ")
    passwrd = input("Password: ")
    api = OsmApi(username=user, password=passwrd)

    print('Downloading...')
    box = api.Map(19.978123,45.273014,20.010052,45.286905)
    print('Done.')

    cyr_num = 0
    i = 0
    missing_lat = []
    missing_lat_ai = []

    for node in box:
        if node['type'] == 'way':
            tags = get_name_tags(node)
            cir_tag = get_cyrilic_tag(tags)

            if cir_tag:
                cyr_num += 1

                in_cyrilic = tags[cir_tag]
                in_latin = convert(in_cyrilic, cyr_to_lat)
                in_latin_ai = convert(in_cyrilic, cyr_to_lat_ai)

                if in_latin not in tags.values():
                    missing_lat.append(node)

                if in_latin_ai not in tags.values():
                    missing_lat_ai.append(node)

    print("Number of nodes with cyrilic names: ", cyr_num)
    print("Missing latin: ",  len(missing_lat))
    print("Missing accent-insensitive latin: ", len(missing_lat_ai))

    changeset(missing_lat, cyr_to_lat, u"name:sr-Latn", u"name:sr-Latin-translit_bot", "latin")
    changeset(missing_lat_ai, cyr_to_lat_ai, u"name:sr-Latn-ai", u"name:sr-Latin-ai-translit_bot", "latin case insensitive")