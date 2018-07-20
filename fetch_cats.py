from lxml import html
import click
import collections
import progressbar
import re
import requests


Weight = collections.namedtuple('Weight', 'str int lb oz')
Age = collections.namedtuple('Age', 'str int')

URL_BASE = 'https://www.sfspca.org'


class Cat(object):
    def __init__(self, url, url_base=URL_BASE):
        self.profile_url = url
        self.url_base = url_base
        self.url = '{}{}'.format(self.url_base, self.profile_url)

        r = requests.get(self.url)
        self.tree = html.fromstring(r.content)

        self.name = self.tree.xpath("//div[contains(@class, 'field-name-title')]/h1/text()")[0].strip()

        self.parse_age()
        self.parse_weight()

    def parse_age(self):
        age_xpath = self.tree.xpath("//div[contains(@class, 'field-name-field-animal-age')]/div/text()")
        if len(age_xpath) > 0:
            self.age = Age(age_xpath[0].strip(), 0)
        else:
            self.age = Age('Unknown', 0)

    def parse_weight(self):
        weight_xpath = self.tree.xpath("//div[contains(@class, 'field-name-field-animal-weight')]/div/text()")

        if len(weight_xpath) > 0:
            weight_str = weight_xpath[0].strip()

            weight_lb = re.findall(r'([0-9]+)\s?lbs?\.', weight_str)
            weight_lb = int((weight_lb + [0])[0])

            weight_oz = re.findall(r'([0-9]+)\s?ozs?\.', weight_str)
            weight_oz = int((weight_oz + [0])[0])

            self.weight = Weight(weight_str, (weight_lb * 16 + weight_oz), weight_lb, weight_oz)
        else:
            self.weight = Weight('Unknown', 0, 0, 0)

    def __str__(self):
        return '{: <40}: {}'.format(
            '{}, age {} - {}:'.format(
                self.name,
                self.age.str,
                self.weight.str,
            ),
            self.url,
        )


def fetch_cat_urls():
    cats = []

    new_cats = True
    page = 0
    while new_cats:
        new_cats = False
        click.secho('Reading page {}'.format(page), fg='blue')
        r = requests.get('{}/adoptions/cats?page={}'.format(URL_BASE, page))
        tree = html.fromstring(r.content)
        new_cats = tree.xpath("//a[contains(@href,'/adoptions/pet-details/')]")
        for cat in new_cats:
            if cat.attrib.get('href') and cat.attrib.get('href') not in cats:
                cats.append(cat.attrib.get('href'))
                new_cats = True
        page += 1

    return cats


def parse_cat():
    pass


@click.command()
def main():
    cat_urls = fetch_cat_urls()
    cats = []
    for cat in progressbar.progressbar(cat_urls):
        # print(Cat('/adoptions/pet-details/38019790'))
        cats.append(Cat(cat))

    sorted_cats = sorted(cats, key=lambda k: -k.weight.int)
    print('Ranking:')
    item = 1
    for cat in sorted_cats:
        print('{: >3}. {}'.format(item, cat))
        item += 1


if __name__ == '__main__':
    main()