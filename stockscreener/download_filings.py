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
import pymongo
from bson.objectid import ObjectId

logger = logging.getLogger(__name__)

try:
    from .helper import parse_date, num
except (ImportError, SystemError):
    from helper import parse_date, num


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

    # def parseLocalFile(local_path):
    #     self.parse({}, local_path=local_path)

    def parse(self, local_path=None):
        """create SAX-Parser and parse the xbrl"""

        if local_path == None:
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

        else:
            with open(local_path, 'r') as f:
                xbrl = f.read()
            it = ET.iterparse(StringIO(xbrl))

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

        root = it.root
        context = defaultdict(dict)
        data = defaultdict(dict)
        misc = {}
        for child in root:
            child.tag = child.tag.replace(".", "")
            if child.tag == 'context':
                for period in child.findall('period'):
                    for date in period:
                        date.text = parse_date(date.text)
                        context[child.attrib['id']][date.tag] = date.text
                for entity in child.findall('entity'):
                    for segment in entity.findall('segment'):

                        if len(segment.findall('explicitMember')) != 0:
                            segment_arr = [
                                m.text for m in segment.findall('explicitMember')]
                        else:
                            # TODO: is this a general rule??
                            segment_arr = [segment[0].tag, ]

                        for member in segment_arr:
                            if ':' in member:
                                member = member.split(':', 1)[1]
                            if 'segment' in context[child.attrib['id']]:
                                context[child.attrib['id']
                                        ]['segment'].append(member)
                            else:
                                context[child.attrib['id']]['segment'] = [
                                    member, ]

            elif search('EntityRegistrantName|TradingSymbol|CurrentFiscalYearEndDate|CommonStockDescription', child.tag, flags=IGNORECASE):
                misc[child.tag] = child.text
            elif pattern.match(str(child.text)):
                data[child.attrib['contextRef']][child.tag] = num(child.text)

        query_reports = []
        query_segment = []
        report_ids = []
        for ref, values in data.items():
            ref_ids = []
            for item in values:
                _id = ObjectId()
                c = {
                    '_id': _id,
                    'company': self.cik,
                    # startDate & endDate || instant || segment
                    **context[ref],
                    'updated': parse_date(self.date),
                    'value': data[ref][item],
                    'label': item
                }
                if 'startDate' in c:
                    c['duration'] = (c['endDate'] - c['startDate']).days
                query_reports.append(pymongo.InsertOne(c))
                ref_ids.append(_id)
                report_ids.append(_id)

            if 'segment' in context[ref]:
                query_segment.extend(
                    [pymongo.UpdateOne(
                        {'_id': l}, 
                        {'$addToSet': {'reports': {'$each': ref_ids}}},
                        upsert=True)
                     for l in context[ref]['segment']])

        if query_reports is None or len(query_reports) == 0:
            return "error no items in %s" % self.url

        query_company = {'filter': {'cik': self.cik},
                         'update': {'$set': {'lastDocument': self.date,
                                             'lastUpdate': datetime.today()},
                                    '$inc': {'NumberOfDocuments': 1},
                                    '$addToSet': {'reports': {'$each': report_ids}}},
                         'upsert': True}

        for k, v in misc.items():
            query_company['update']['$set'][k] = v

        return {
            'query_company': query_company,
            'query_financial_positions': query_reports,
            'query_segment': query_segment,
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
        'https://www.sec.gov/Archives/edgar/data/796343/0001104659-07-072546.txt')
    # crawler.download()

    crawler.parse(
        '/home/olli/Repositories-Next/Bots/stockscreener/test/796343/0001104659-07-072546/adbe-20070917.xml')

    # target = path.join(path.dirname(path.abspath(__file__)), '..', 'test')
    # crawler.save_documents(target)
