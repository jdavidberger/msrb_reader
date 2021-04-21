import json
import numbers
import sys
import time

import requests
import requests_cache

requests_cache.install_cache('msrb_data')

def GetSecurityDetailsForCDSubmission(id):
    cookies = {
        'acceptCookies': 'true',
        'Disclaimer4': 'msrborg'
    }

    url = f"https://emma.msrb.org/MarketActivity/GetSecurityDetailsForCDSubmission/{id}?"
    r = requests.request('GET', url, cookies=cookies)
    return r.json()

def GetIssueId(issue):
    return issue['IssueId'] if len(issue.get('IssueId', '')) > 0 else issue['IssueHashId']

top_schema = {
    'data': {
        '_id': 'Cusip6Id',
        'SubmissionIssues': {
            '_id': GetIssueId,
            'SubmissionSecurities': {
                '_id': 'Cusip9'
            }
        }
    }
}

def get_table_names(schema):
    names = [k for k in schema.keys() if not k.startswith("_")]
    rtn = names.copy()
    for n in names:
        rtn += get_table_names(schema[n])
    return rtn

def tablify(json, table_name = None, parent_id = None, schema=top_schema):
    names = [k for k in schema.keys() if not k.startswith("_")]
    tables = {}
    id_field = schema.get("_id", None)

    id = None
    if id_field is None:
        id = None
    else:
        id = id_field(json) if callable(id_field) else json[id_field]

    for n in names:
        for table_data in json[n]:
            new_tables = tablify(table_data, n, id, schema[n])
            for k in new_tables:
                tables[k] = tables.get(k, []) + new_tables[k]
        json.pop(n, None)

    for n in [k for k in json.keys() if k.endswith("Json")]:
        json.pop(n, None)

    if table_name is not None:
        tables[table_name] = [
            json
        ]
        if id is not None:
            tables[table_name][0]['_id'] = id
        if parent_id is not None:
            tables[table_name][0]['_parent_id'] = parent_id
    return tables


def format(v):
    if v is None: return ""
    if v is True: return "1"
    if v is False: return "0"
    if isinstance(v, numbers.Number):
        return str(v)
    if v.startswith("$"): return v[1:].replace(",", "")
    if v.endswith("%"): return v[:-1]
    return f"'{v}'"

if __name__ == "__main__":
    cd_submission_ids = sys.argv[1:]
    if len(cd_submission_ids) == 0:
        cd_submission_ids = ["P11115213"]

    for id in cd_submission_ids:
        tables = tablify(GetSecurityDetailsForCDSubmission(id))

        for name in tables.keys():
            headers = sorted(list(tables[name][0].keys()), reverse=True)
            with open(f'ContinuingDisclosureDetails_{name}.csv', 'w') as f:
                print('\t'.join(headers), file=f)
                for r in tables[name]:
                    print('\t'.join([format(r[h]) for h in headers]), file=f)
