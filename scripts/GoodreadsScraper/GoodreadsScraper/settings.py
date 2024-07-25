BOT_NAME = 'GoodreadsScraper'

SPIDER_MODULES = ['GoodreadsScraper.spiders']
NEWSPIDER_MODULE = 'GoodreadsScraper.spiders'


# Obey robots.txt rules
ROBOTSTXT_OBEY = True

DOWNLOAD_DELAY = 0.1


# Configure item pipelines
ITEM_PIPELINES = {
    'GoodreadsScraper.pipelines.JsonLineItemSegregator': 300,
}

