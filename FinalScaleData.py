import sys
import time

import requests

default_issues = ["RE400706", "0E2985631C05D7F92254E9BD0D691B58", "62E7E82D38A0C88A45955CA41183F542",
          "CB937BB4E379B2458B7612DF2C2DED7C", "RE400578", "SS402304", "SS402321", "ER393822", "ER393847", "ER392850",
          "ES395018", "ER386518", "ES388682", "ES382447", "641869B9A1EC5845761BDEBD726931E6", "ES379407", "EP372247",
          "EP372248", "EA355903", "EA355902", "EA356280", "EA353013", "EA353014", "ER357887", "ER357888",
          "45E869C313B78BE135A80B96C4A9D293", "EA343488", "EA343489", "ER351285", "51DD9ACB2F240BA3C24C8C36EDC3472A",
          "ER348492", "EP349283", "14DAB330FA4831633B7DBDFF3280B896", "9F6DFF11A96F387B19510B3216096BB8", "ER345000",
          "EP341561", "EP341562", "EP341563", "8AA6E62D2B3A88AEF6F49A85397BFB0B", "EP333330", "EP333331", "EP333332",
          "MS69640", "4D2E5F620CEFB5C5D45E62BE34ABE5FB", "MS210583", "B9E972E88D5A4F568CEDED094F7D0748", "MS30053",
          "MS209813", "MS243771", "24422794BA7434DEC265E2268C359B40", "EA357319", "F66BD3BEB8984023558F8966C19CE792",
          "MS135343", "MS134353", "MS21307", "MS34472", "MS20460", "MS272328", "MS199398"]

def GetFinalScaleData(id):
    template = "https://emma.msrb.org/IssueView/GetFinalScaleData?id={}&_={}"
    cookies = {
        'acceptCookies': 'true',
        'Disclaimer4': 'msrborg'
    }

    url = template.format(id, int(time.time()))
    r = requests.request('GET', url, cookies=cookies)
    return r.json()

if __name__=='__main__':
    rows = []

    issues = sys.argv[1:]
    if len(issues) == 0:
        issues = default_issues

    headers = set()
    for idx, id in enumerate(issues):
        for row in GetFinalScaleData(id):
            row['_issuer'] = id
            rows.append(row)
            headers.update(row.keys())
        print(f"{idx} / {len(issues)}")

    headers = list(headers)


    def format(v):
        if v is None: return ""
        if v is True: return "1"
        if v is False: return "0"
        if v.startswith("$"): return v[1:].replace(",", "")
        if v.endswith("%"): return v[:-1]
        return v


    with open('output.csv', 'w') as f:
        print('\t'.join(headers), file=f)
        for r in rows:
            print('\t'.join([format(r[h]) for h in headers]), file=f)
