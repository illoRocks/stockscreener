#!/usr/bin/env python3.6

import xml.etree.ElementTree as ET
from _collections import defaultdict
from datetime import datetime
from io import StringIO
from os import makedirs, path
from re import search, sub, findall, IGNORECASE, compile
import time
import requests
import logging

logger = logging.getLogger(__name__)


''' TODO: rename '''
pattern = compile("^(-[0-9]+)|([0-9]+)$")


class XbrlCrawler:
    """load filings from SEC and save them to objects"""

    def __init__(self, url, cik=None, date=None):
        self.url = 'https://www.sec.gov/Archives/%s' % url.replace(
            'https://www.sec.gov/Archives/', '')
        self.cik = cik if cik is not None else url.split('/')[-2]
        self.date = date
        self.accession = url.split('/')[-1][:-4]
        self.files = {}

    def download(self):
        """download and save sec files"""

        try:
            resp = requests.get(self.url, stream=True)

            header = True
            start_xml = False
            commit = False
            filename = 'header.txt'

            for line in resp.iter_lines():

                if not commit and search(b'(<filename>)', line, flags=IGNORECASE):
                    filename = line[10:].decode("utf-8")

                if not commit and \
                        filename is not None and \
                        search(b'(<xbrl>|<sec-header>)', line, flags=IGNORECASE):
                    self.files[filename] = ''
                    commit = True

                if commit and not start_xml and search(b'(<?xml)', line, flags=IGNORECASE):
                    start_xml = True

                if commit and (start_xml or header):
                    self.files[filename] += '%s\n' % sub(
                        '\n', '', line.decode("utf-8"))

                if commit and search(b'(</sec-header>|</xbrl>|</xbrli:xbrl>)', line, flags=IGNORECASE):
                    self.files[filename] = sub(
                        '<xbrl>\n', '', self.files[filename], flags=IGNORECASE)  # </xbrl>|
                    commit = False
                    filename = None
                    start_xml = False
                    header = True

            resp.close()

        except Exception as inst:
            logging.error('error in requests\n\t%s' % inst.args)
            quit()

    def clean_file(self, filename):
        ''' clean file from not necessary content '''

        self.files[filename] = sub(
            '(<link:footnoteLink((.|\n)*?)footnoteLink>)', '', self.files[filename])
        linebreak = findall('</((.|\n)*?)>', self.files[filename])
        for b in linebreak:
            cleaned = sub('\n', '', b[0])
            self.files[filename] = sub(b[0], cleaned, self.files[filename])

        self.files[filename] = sub('&', '', self.files[filename])
        self.files[filename] = sub('<\n', '<', self.files[filename])
        self.files[filename] = sub(
            '(us.{1,4}gaap:)', 'us-gaap:', self.files[filename])

    def save_documents(self, target_path):
        """save whole documents in path"""

        file_path = path.join(target_path, self.cik, self.accession)

        if len(self.files) > 0:
            logger.debug('write to: %s' % file_path)
        else:
            logger.error('no files downloaded!!!')
            quit()

        makedirs(file_path, exist_ok=True)
        for filename, txt in self.files.items():
            with open(file_path + '/' + filename, 'w') as file:
                file.write('%s\n' % txt)

    def parse(self):
        """create SAX-Parser and parse the xbrl"""

        t = time.time()
        xbrl = False
        for f in self.files:
            if not search('(header.txt|FilingSummary|\.xsd|defnref|(pre|lab|def|cal|ref|R[0-9]{1,3})\.xml)', f):
                xbrl = True
                logger.debug('parse: %s in %s' % (f, self.url))
                filename = f
                self.clean_file(filename=filename)
                break

        if not xbrl:
            f = ''.join('\t' + f + '\n' for f in self.files)
            logger.warning(
                'no xbrl found. please change criterion: \n%s\t%s' % (f, self.url))
            return 'no xbrl found!'

        it = ET.iterparse(StringIO(self.files[filename]))
        # strip all namespaces
        try:
            for _, el in it:
                if '}' in el.tag:
                    el.tag = el.tag.split('}', 1)[1]

        except ET.ParseError as err:
            logger.error('''
                Something went wrong
                file is stored under: %s
                please check the failure in the xml and fix this bug
                error: %s
                ''' % ('errors/' + self.cik + '/' + self.accession + '/' + filename, err))
            self.save_documents("logs/errors")
            quit()

        def num(s):
            try:
                return int(s)
            except ValueError:
                return float(s)

        root = it.root
        context = defaultdict(dict)
        data = defaultdict(dict)
        misc = {}
        for child in root:
            child.tag = child.tag.replace(".", "")
            if child.tag == 'context':
                for period in child.findall('period'):
                    for date in period:
                        context[child.attrib['id']][date.tag] = date.text
            elif search('EntityRegistrantName|TradingSymbol|CurrentFiscalYearEndDate|CommonStockDescription', child.tag, flags=IGNORECASE):
                misc[child.tag] = child.text
            elif pattern.match(str(child.text)):
                data[child.attrib['contextRef']][child.tag] = num(child.text)

        content = defaultdict(dict)
        for ref, values in data.items():
            for item in values:
                content[item].setdefault('$each', []).append(
                    {**context[ref],  # startDate and endDate
                     'updated': self.date,
                     'value': data[ref][item]})

        if content is None or len(content) == 0:
            return "error no items in %s" % self.url

        query_company = {'filter': {'_id': self.cik},
                        'update': {"$set": {'lastDocument': self.date,
                                            'lastUpdate': datetime.today()},
                                    '$inc': {'NumberOfDocuments': 1} },
                        'upsert': True}

        query_financial_positions = {'filter': {'_id': self.cik},
                 'update': {'$addToSet': {**content} },
                 'upsert': True}

        for k, v in misc.items():
            query_company['update']['$set'][k] = v

        return { 
            'query_company': query_company, 
            'query_financial_positions': query_financial_positions,
            'cik': self.cik, 
            'edgar_path': self.url.replace('https://www.sec.gov/Archives/', '')
        }

    def __str__(self):
        return '''
            Classname: %s
            Parameters: url = %s
                        cik = %s
                        date = %s
                        accession = %s
                        files = %s
            ''' % (__class__.__name__, self.url, self.cik, self.date, self.accession, self.files)


if __name__ == '__main__':

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s/%(module)s/%(funcName)s %(message)s'
    )

    crawler = XbrlCrawler(
        'https://www.sec.gov/Archives/edgar/data/104169/0001193125-10-202779.txt')
    print(crawler)
    crawler.download()
    crawler.parse()

    # crawler.save_documents(join(dirname(abspath(__file__)), 'temp'))
