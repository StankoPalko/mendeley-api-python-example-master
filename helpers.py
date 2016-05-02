import json
import requests

def get_url_from_header(response):

    links_dict = requests.utils.parse_header_links(response.headers['Link'])
    print(links_dict)

    header_has_next = False
    url = None

    for l in links_dict:
        if l['rel'] == 'next':
           print("Has next")
           header_has_next = True
           url = l['url']
           print("URL: "  + url)

    return header_has_next,url

def get_link(doi):
    url = "http://dx.doi.org/" + doi
    source_code = requests.get(url) # type: requests.models.Response
    return source_code.url