import sys
import urllib.request
import urllib.error
import json
from collections import defaultdict

# program prebere vsebino računa iz spletnega vira, jo formatira in jo izpiše na ekran
class DataProcessingError(Exception):
    pass

class Receipt:

    def __init__(self, arg):
        ## branje argumenta, nalaganje podatkov
        if type(arg) == dict:
            self.data = arg
        else:
            self.data = _fetch_load_json_(arg)

        ## definicije formatov izpisa ter procesiranja podatkov
        self.print_function_map = {
            'a': ('{}\n{}\n{}\nID za DDV:{}\n', lambda e: e.split('#')),
            'b': ('Prodajalec: {}', None),
            'c': ('Račun št.: {}', None),
            'd': ('Čas: {}, {}', lambda e: e.split('+')[0].split('T')),
            'e': ('Stopnja DDV: {:.1f} %\nNeto vrednost: {:.2f} €\nDDV: {:.2f} €\nBruto vrednost: {:.2f} €\n',
                  lambda e: self.__proc_e__(e)),
            'f': ('ZOI: {}', None),
            'g': ('EOR: {}', None),
            'z': ('\nSkupaj: {:.2f} €\n', lambda e: (self.__proc_z__(e),)),
        }

        ## inicializacija spremenljivk
        self.output = defaultdict(str)
        self.suma = 0

        ## nastavljanje privzetega reda izpisa podatkov
        self.__print_order = None
        self.set_print_order('aczebdfg')
        self.__process_data__()


    def set_print_order(self, order):
        ## preverjanje ustreznosti podanega reda izpisa
        for e in order:
            if not (e in self.data.keys() and e in self.print_function_map.keys()):
                raise ValueError('Neveljaven argument za zaporedje izpisa "{}": {}'.format(e, order))

        self.__print_order = order

    def __process_data__(self):
        ## vsak element reda izpisa se prebere iz vhodnih podatkov, sprocesira in doda v izhodni slovar
        for element in self.__print_order:
            dat = self.data.get(element)
            txt, function = self.print_function_map[element]
            p = txt.format(*(dat,) if function is None
            else function(dat)) + '\n'
            self.output[element] += p

    ## funkcija za procesiranje spiska artiklov
    def __proc_z__(self, postavke):
        z = '\nArtikli\n--------------------\n'
        for item in postavke:
            s = item.get('b') * item.get('c')
            self.suma += s
            z += '{}\n{} x {:.2f} € = {:.2f}\n'.format(
                item.get('a'), item.get('b'), item.get('c'), s)
        self.output['z'] += z
        return self.suma

    ## funkcija za izračun davka
    def __proc_e__(self, tax_rate):
        neto = self.suma * (1 - tax_rate)
        ddv = self.suma - neto
        return tax_rate * 100, neto, ddv, self.suma

    ## funkcija za izpis podatkov
    def to_string(self):
        out = ''
        for e in self.__print_order:
            out += self.output[e]
        return out



## funkcija za nalaganje podatkov
def _fetch_load_json_(url):
    data = None
    ex = None
    try:
        fetch_response = urllib.request.urlopen(url)  # odpre url
        enc = fetch_response.headers.get_content_charset() # prebere kodiranje podatkov
        if enc is None:
            enc = 'utf-8'
        decoded = fetch_response.read().decode(enc)  # dekodira podatke
        data = json.loads(decoded)  # prebere json podatke v slovar
        if data.get('ErrCode') != 0:  # preveri ali je status odgovora brez napake
            raise DataProcessingError('Napaka strežnika %(ErrCode)d:\n%(ErrDesc)s\n%(ErrArgs)s' % data)
        else:
            data = data.get('Data')
    except (AttributeError, KeyError, urllib.error.URLError, json.JSONDecodeError, ValueError) as e:
        ex = e
        data = json.loads(open(url, 'r').read())
    finally:
        if data != None:
            return data
        else: raise ex #DataProcessingError('Napaka pri obdelavi podatkov, preveri povezavo in vir podatkov') from ex


def main():
    try:
        re = Receipt(sys.argv[1] if len(sys.argv) > 1 else 'https://apica.iplus.si/api/Naloga?API_KEY=B70DBCDB-51C3-4A07-B6CE-6C83FAE0AD2E')
        if len(sys.argv) > 2:
            re.set_print_order(sys.argv[2])
        print(re.to_string())
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()



