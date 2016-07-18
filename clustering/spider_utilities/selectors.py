title_selector_index = "title_selector"
body_selector_index = "body_selector"
rss_index = "rss_index"
# TODO: posiblemente tengamos que agregar aqui el link al rss de cada portal
google_news_main_selectors = {"http://news.google.com/news/story" : {
                "news_selector" :
                    "//div[@class=\"story-page-main\"]//div[@class=\"topic\"]"
                                                                    }
                            }

sites_selectors = {"www\.infobae\.com" :
                          {title_selector_index : ["//header[@class=\"article-header hed-first col-sm-12\"]/h1"],
                          body_selector_index : ["//div[@id=\"article-body\"]/div[@id=\"article-content\"]"],
                          rss_index : "http://cdn01.ib.infobae.com/adjuntos/162/rss/Infobae.xml"},

                    "www\.clarin\.com" :
                      {title_selector_index : ["//div[@class=\"int-nota-title\"]/h1"],
                      body_selector_index : ["//div[@class=\"nota\"]"],
                      rss_index : "http://www.clarin.com/rss/lo-ultimo/"},

                    "www\.pagina12\.com\.ar" :
                      {title_selector_index : ["//div[@class=\"nota ultima-noticia top12\"]/h2",
                                                "//div[@class=\"nota top12\"]/h2",
                                                "//div[@class=\"nota\"]/h2"],
                      body_selector_index : ["//div[@id=\"cuerpo\"]"],
                      rss_index : "http://www.pagina12.com.ar/diario/rss/ultimas_noticias.xml"},

                    "www\.lavoz\.com\.ar" :
                      {title_selector_index : ["//header[@class=\"Main\"]/h1"],
                      body_selector_index : ["//div[@class=\"field-item even\"]"],
                      rss_index : "http://www.lavoz.com.ar/rss.xml"},

                    "www\.lanacion\.com\.ar" :
                      {title_selector_index : ["//h1[@itemprop=\"headline\"]"],
                      body_selector_index : ["//section[@id=\"cuerpo\"]"],
                      rss_index : "http://contenidos.lanacion.com.ar/herramientas/rss-origen=2"},

                    "www\.telam\.com\.ar" :
                    {title_selector_index : ["//div[@class=\"title\"]/h2"],
                    body_selector_index : ["//div[@class=\"main-content\"]/div[@class=\"editable-content\"]"],
                    rss_index : "http://www.telam.com.ar/rss2/ultimasnoticias.xml"},

                    "www\.cadena3\.com" :
                    {title_selector_index : ["//div[@id=\"nota-ampliada\"]/div[@class=\"titulo\"]"],
                    body_selector_index : ["//div[@id=\"nota-ampliada\"]/div[@class=\"cuerpo\"]"],
                    rss_index : "http://cadena3.com/rss/Internacionales.xml"},

                    "www\.perfil\.com" :
                    {title_selector_index : ["//div[@class=\"contenido\"]//header[@id=\"header-noticia\"]/hgroup"],
                    body_selector_index : ["//div[@class=\"contenido\"]//div[@itemprop=\"articleBody\"]"],
                    rss_index : "http://www.perfil.com/rss/ultimomomento.xml"},

                    "www\.ambito\.com" :
                    {title_selector_index : ["//div[@id=\"contenido\"]//h2[@id=\"tituloDespliegue\"]"],
                    body_selector_index : ["//div[@id=\"contenido\"]//div[@id=\"textoDespliegue\"]",
                                            "//div[@id=\"contenido\"]//p[@id=\"textoDespliegue\"]"],
                    rss_index : "http://www.ambito.com/rss/noticiasp.asp"}}
