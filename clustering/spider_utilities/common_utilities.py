from bs4 import BeautifulSoup
from selectors import sites_selectors, title_selector_index, body_selector_index
import re
import scrapy

# TODO: iba a colocar aqui los metodos de la arana que se encargan de parsear
# el cuerpo de las noticias, pero me parece que esta mezclado con la logica
# propia de lo que hace aquella arana...
def extract_element(response, selector_index):
    ret = None
    selectors = response.meta[selector_index]
    # Try with different selectors
    for selector in selectors:
        selector_result = response.xpath(selector).extract()
        if len(selector_result) == 1:
            element_html = selector_result[0]
            element_parser = BeautifulSoup(element_html, 'html.parser')
            # Delete scripts
            for script in element_parser(["script", "style"]):
                script.extract()

            ret = element_parser.get_text()
            break

    return ret

def generate_appr_request(link, callback):
    """Analizes a string representing a link to a news' site,
        generates a request to that link and selects the apropiate callback
        method to handle the response. Also, saves the article into the
        corpus.

        PARAMS
        link: a string representing the link to the site.
        callback: the callback procedure that will receive the response
                to the request."""
                
    req = None
    for site_link, selectors in sites_selectors.iteritems():
        site_reg_exp = ".*" + site_link + ".*"
        match = re.search(site_reg_exp, link)
        if match:
            req = scrapy.Request(link,
                                callback=callback)
            req.meta["title_selector"] = selectors[title_selector_index]
            req.meta["body_selector"] = selectors[body_selector_index]
            break

    return req
