from engine.l4_singletons import LotusSettings

if __name__ == "__main__":
    settings = LotusSettings(local=True)
    settings.get_google_apikey()
    settings.get_openai_apikey()
    settings.get_searchengine_id()
