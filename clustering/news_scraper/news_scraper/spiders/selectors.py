sites_selectors = {".*www\.infobae\.com.*" :
                          {"title_selector" : "//header[@class=\"detail-header clearfix\"]/h1[@class=\"entry-title\"]",
                          "body_selector" : "//div[@class=\"cuerposmart clearfix\"]/div"},

                    ".*www\.clarin\.com.*" :
                      {"title_selector" : "//div[@class=\"int-nota-title\"]/h1",
                      "body_selector" : "//div[@class=\"nota\"]"},

                    ".*www\.pagina12\.com\.ar.*" :
                      {"title_selector" : "//div[@class=\"nota ultima-noticia top12\"]/h2",
                      "body_selector" : "//div[@id=\"cuerpo\"]"},

                    ".*www\.lavoz\.com\.ar.*" :
                      {"title_selector" : "//header[@class=\"Main\"]/h1",
                      "body_selector" : "//div[@class=\"field-item even\"]"},

                    ".*www\.lanacion\.com\.ar.*" :
                      {"title_selector" : "//h1[@itemprop=\"headline\"]",
                      "body_selector" : "//section[@id=\"cuerpo\"]"},

                    ".*www\.telam\.com\.ar.*" :
                    {"title_selector" : "//div[@class=\"title\"]/h2",
                    "body_selector" : "//div[@class=\"main-content\"]/div[@class=\"editable-content\"]"},

                    ".*www\.cadena3\.com.*" :
                    {"title_selector" : "//div[@id=\"nota-ampliada\"]/div[@class=\"titulo\"]",
                    "body_selector" : "//div[@id=\"nota-ampliada\"]/div[@class=\"cuerpo\"]"},

                    ".*www\.perfil\.com.*" :
                    {"title_selector" : "//div[@class=\"contenido\"]//header[@id=\"header-noticia\"]/hgroup",
                    "body_selector" : "//div[@class=\"contenido\"]//div[@itemprop=\"articleBody\"]"},

                    ".*www\.ambito\.com.*" :
                    {"title_selector" : "//div[@id=\"contenido\"]//h2[@id=\"tituloDespliegue\"]",
                    "body_selector" : "//div[@id=\"contenido\"]//p[@id=\"textoDespliegue\"]"}}
