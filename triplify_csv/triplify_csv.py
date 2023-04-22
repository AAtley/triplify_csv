from rdflib import Graph, Literal, URIRef, Dataset, BNode
import csv
#from rdflib.plugins import sparql
from rdflib.namespace import XSD, RDF, FOAF, Namespace
import re
from itertools import takewhile
import os
import sys, getopt
import urllib.parse
from datetime import datetime
import click


def rr(vocab):
	""" return r2rml vocabulary item """
	rr = u'http://www.w3.org/ns/r2rml#'	
	return rr + vocab
	
class CsvOptions:
	""" Class to represent CSV file options """
	def __init__(self, encoding="utf-8", delimiter=",", dateformat='%Y-%m-%d'):
		self.delimiter = delimiter
		self.encoding = encoding
		self.dateformat = dateformat
		
class CsvInfo:
	""" Handles the opening and reading of csv files """ 
	def __init__(self, path, options = None):
		self.path = path
		self.columnNames = None
		self.columnTypes = None
		self.csvfile = None
		self.reader = None
		self.errors = []
		self.tablename = os.path.splitext(os.path.basename(self.path))[0]
		self.options = options
		if not options:
			self.options = CsvOptions()
			
	def __enter__(self):
		self.reset_file()
		return self
		
	def reset_file(self):
		self.csvfile = open(self.path, encoding=self.options.encoding)
		self.reader = csv.DictReader(self.csvfile,delimiter=self.options.delimiter)
		self.set_column_names()
		return self
		
	def __exit__(self, *args):
		if self.csvfile:
			self.csvfile.close()
			
	def closefile(self):
		if self.csvfile:
			self.csvfile.close()
					
			
	def get_restarted_reader(self):
		if self.csvfile.closed:
			self.reset_file()
		self.csvfile.seek(0)
		return self.reader
		
		
	def set_column_names(self):
		rdr = self.get_restarted_reader()
		try:
			self.columnNames = [name for name in next(rdr)]
		except StopIteration as e:
			self.errors.append('csv file {} may be empty'.format(self.tablename))
			
	def get_contents(self):
		reader = self.get_restarted_reader()
		buf = []
		for line in reader:
			buf.append(line)
			
		return buf
		
class Rml:
	""" Reads config mapping file and applies mappings to the data in one or more csvfiles"""
	def __init__(self):
		# graph to hold triplemap elements
		self.g = Graph()
		
		# graph to hold generated triples
		self.triples = Graph()
		
		# @baseURL of rml file
		self._baseURL = ''
		
		# self.making_quads is true if rml has any triplesmaps that name a non 'defaultGraph'
		self.making_quads = False
		
		self.csv_paths = []
		self.csvInfoList = []
		self.csv_tables = []
		self.errors = []
		
	def loadFile(self, file, csv_arr = [], options = None):
		self.csv_paths = csv_arr
		self.options = options
		self.open_csvs()
		self.g.parse(file, format="ttl")
		self.set_baseURI(file)
		return len(self.g)
		
		
	def open_csvs(self, options = None):
		for csvfile in self.csv_paths:
			with CsvInfo(csvfile, self.options) as csvInfo:
				self.csvInfoList.append(csvInfo)
				self.csv_tables.append(csvInfo.tablename)
				# append errors
				for err in csvInfo.errors:
					self.errors.append(err)
					
					
	def close_csvs(self):
		for csvInfo in self.csvInfoList:
			csvInfo.closefile()
					
					
	# get the csvinfo that matches this tablename
	def get_csvInfo_by_tablename(self, tablename):
		for csvInfo in self.csvInfoList:
			if csvInfo.tablename == tablename:
				return csvInfo
		return None
		
		
	def set_baseURI(self,path):
		with open(path) as file:
			# an entry starts with `#@` line and ends with a blank line
			
			for line in file:
				if line.startswith('@base'):
					buf = [line]
					#       read until blank line
					buf.extend(takewhile(str.strip, file)) #
			#       if just one return it
			if len(buf) == 1:
				self.base= re.findall(r'<([^>]+)>', ''.join(buf))[0]
				
	
	def get_baseURI(self):
		return self.base
	
	'''	
	def runSparql(self,qstring):
		base = Namespace(URIRef(self.base))
		
		rr = Namespace("http://www.w3.org/ns/r2rml#")
		#self.g.bind("base", base)
		
		self.g.namespace_manager.bind('', base)
		q = sparql.prepareQuery(qstring,initNs= {"" : base,"xsd" : XSD, "rdf" : RDF, "rr" : rr})
		
		return self.g.query(q)
	'''	

	def tmaps(self):
		tmaps = {}
		# for each triplemap add a list of dict for predicateObjectMaps called 'poms'
		for tm, p, o in self.g.triples((None, RDF.type, URIRef(rr('TriplesMap')))):
			tmaps[str(tm)] = {
				'poms' : [],
				rr('logicalTable') : {},
				rr('subjectMap') : {}
				}
			# for each predicateObjectMap find its bnode obj
			for tmap, p, bn in self.g.triples((tm, URIRef(rr('predicateObjectMap')), None)):
				pom = {}
				# for each pom's bnode as subject 
				for bnk, pompred, pomobj in self.g.triples((bn, None, None)):
					if not isinstance(pomobj, BNode):
						# if we already have a predicate append obj to list
						if str(pompred) in pom and len(pom[str(pompred)]) > 0:
							pom[str(pompred)] += ',' + str(pomobj)
						else:
							pom[str(pompred)] = str(pomobj)
					else:
						pom[str(pompred)] = {}
						for pmbkn, pmbknp, pmbkno in self.g.triples((pomobj,None,None)):
							if not isinstance(pmbkno, BNode):
								pom[str(pompred)][str(pmbknp)] = str(pmbkno).strip('\""')
							else:
								pom[str(pompred)][str(pmbknp)] = {}
								for js, jp, jo in self.g.triples((pmbkno,None,None)):
									pom[str(pompred)][str(pmbknp)][str(jp)] = str(jo).strip('\""')
								
				tmaps[str(tm)]['poms'].append(pom)
			# use logicalTable's blank node to find all contents
			logtable_bnode = self.g.value(subject = tm, predicate = URIRef(rr('logicalTable')))
			
			for ltbn, ltpred, ltobj in self.g.triples((logtable_bnode, None, None)):
				tmaps[str(tm)][rr('logicalTable')][str(ltpred)] = str(ltobj).strip('\""')
				
			# use subjectMap's blank node to find all contents
			#smap_bnode = self.g.value(subject = tm, predicate = rr('subjectMap'))
			smap_bnode = None
			for x, y, z in self.g.triples((tm, URIRef(rr('subjectMap')), None)):
				if isinstance(z, BNode):
					smap_bnode = z
			
			# may get many obj with same pred e.g. rr:class
			for smbn, smpred, smobj in self.g.triples((smap_bnode, None, None)):
				if not str(smpred) in tmaps[str(tm)][rr('subjectMap')]:
					tmaps[str(tm)][rr('subjectMap')][str(smpred)] = ""
					
				if str(smpred) == rr('class'):
					if len(tmaps[str(tm)][rr('subjectMap')][rr('class')]) > 0:
						tmaps[str(tm)][rr('subjectMap')][rr('class')] += ',' + str(smobj).strip('\""')
					else:
						tmaps[str(tm)][rr('subjectMap')][rr('class')] = str(smobj).strip('\""')
				elif str(smpred) ==  rr('template') and not isinstance(smobj,BNode):
					tmaps[str(tm)][rr('subjectMap')][rr('template')] = str(smobj).strip('\""')
					#if 'graph' in str(smobj).strip('\""'):
						#print('smoobj=' + str(smobj).strip('\""'))
				elif str(smpred) ==  rr('graph'):
					tmaps[str(tm)][rr('subjectMap')][rr('graph')] = str(smobj).strip('\""')
				elif str(smpred) == rr('graphMap'):
					tmaps[str(tm)][rr('subjectMap')][rr('graphMap')] = {}
					for smbkn, smbknp, smbnkno in self.g.triples((smobj,None,None)):					
						tmaps[str(tm)][rr('subjectMap')][rr('graphMap')][str(smbknp)] = str(smbnkno).strip('\""')
		
		for rom, x, y in self.g.triples((None, RDF.type, URIRef(rr('RefObjectMap')))):
			tmaps[str(rom)] = {}
			for refom, ptm, tmref in self.g.triples((rom, URIRef(rr('parentTriplesMap')), None)):
				tmaps[str(rom)][str(ptm)] = str(tmref)
				
		
		return tmaps
	
	def get_Uri_From_Template(self, template, row):
		cols = []
		s = re.sub('[{"}]','', template)
		for match in re.finditer(r'{"([^>]+?)"}', template):
			cols.append(match.group(0).strip('{}"'))
		for col in cols:
			s = s.replace(col,urllib.parse.quote(row[col]))
		return str(s)
		
	
	# use base and the tmap structure populated from the rml file and its named columns in the csv/table named by tablename to create triples in  the triples graph
	def create_triples(self):
	
		tmaps = self.tmaps()
		
		making_quads = False
		
		# for each triple map in rml
		for tk in tmaps.keys():
			
			# skip the ones without subjectMap; they are RefObjectMaps
			if rr('subjectMap') not in tmaps[tk]:
				continue
			
			# determine if we are making quads or triples and get context if quads
			context = ''
			if rr('graph') in tmaps[tk][rr('subjectMap')]:
				context = tmaps[tk][rr('subjectMap')][rr('graph')]
				if not str(context).endswith('defaultGraph'):
					making_quads = True
					self.making_quads = True
				else:
					making_quads = False
				
				
			elif rr('graphMap') in tmaps[tk][rr('subjectMap')]:
					if rr('column') in tmaps[tk][rr('subjectMap')][rr('graphMap')] and rr('termType') in tmaps[tk][rr('subjectMap')][rr('graphMap')] and tmaps[tk][rr('subjectMap')][rr('graphMap')][rr('termType')] == rr('Literal'):
						# cant use a literal as graph uri
						making_quads = False
						self.errors.append('Graph specified should not be a literal value')
						continue
					elif rr('template') in tmaps[tk][rr('subjectMap')][rr('graphMap')]:
						making_quads = True
						self.making_quads = True
						context = tmaps[tk][rr('subjectMap')][rr('graphMap')][rr('template')]
			else:
				making_quads = False
				
			# reinitialise graph as Dataset as it will be holding quads 	
			if making_quads:
				self.triples = Dataset()
			
			# find col names used in this tmap's template
			cols = []
			subjmap_template = tmaps[tk][rr('subjectMap')][rr('template')]
			for match in re.finditer(r'{"([^>]+?)"}',subjmap_template):
				cols.append(match.group(0).strip('{}"'))
				
			
			# use tablename to look in right csv
			logical_table = ''
			csvinfo = None
			if rr('logicalTable') in tmaps[tk] and rr('tableName') in tmaps[tk][rr('logicalTable')]:
				logical_table = tmaps[tk][rr('logicalTable')][rr('tableName')]
			if logical_table:
				csvinfo = self.get_csvInfo_by_tablename(logical_table)		
				
				#print('logical table: ' + logical_table)
				#if csvinfo is not None:
				#	print('found csvinfo: ' + csvinfo.tablename)
			
			# check we have a csv file with the same name as the logical_table in rml
			if csvinfo is None:
				self.errors.append('A csv for table {} was not found'.format(logical_table))
				continue
				
			
			# only continue if fieldnames in cols named of template all appear in column names of table in csv
			if set(cols).issubset(csvinfo.columnNames):
				# construct URIRef for subject
				rdr = csvinfo.get_restarted_reader()
				
				
				next(rdr) # skip the headers
				for row in rdr:				
					# if subjectmap's graph given by template, col names by row values
					if rr('graphMap') in tmaps[tk][rr('subjectMap')]:
						if rr('template') in tmaps[tk][rr('subjectMap')][rr('graphMap')]:
							context = self.get_Uri_From_Template(context,row)
					
					# replace subject template's col names with values from csv
					s = re.sub('[{"}]','',subjmap_template)
					
					for col in cols:			
						s = s.replace(col,urllib.parse.quote(str(row[col])))
					subject = URIRef(s)
					object = None
					predicate = None
					# create triples / quads for each type in class list from rml file
					csv_classes = ''
					if rr('class') in tmaps[tk][rr('subjectMap')]:
						csv_classes = tmaps[tk][rr('subjectMap')][rr('class')]
						classes = csv_classes.split(',')
						for cls in classes:
							predicate = RDF.type
							object = URIRef(cls)
							
							if making_quads:
								self.triples.add((subject, predicate, object,URIRef(context)))
							else:
								self.triples.add((subject, predicate, object))
					
					# iterate through predobjs 
					for pom in tmaps[tk]['poms']:
						predicates = str(pom[rr('predicate')]).split(',')
						for pred_str in predicates:
							predicate = URIRef(pred_str)
						
							pom_column = ''
							pom_object = ''
							literal_lang = ''
							if rr('object') in pom:
								pom_object = pom[rr('object')]
							if rr('objectMap') in pom and rr('column') in pom[rr('objectMap')]:
								pom_column = pom[rr('objectMap')][rr('column')]
								if rr('language') in pom[rr('objectMap')]:
									literal_lang = pom[rr('objectMap')][rr('language')]
								
							# if objectmap in pom and key of this om is also in tmap then it is a refobjmap
							if rr('objectMap') in pom and str(pom[rr('objectMap')]) in tmaps.keys() and rr('parentTriplesMap') in tmaps[str(pom[rr('objectMap')])] and tmaps[str(pom[rr('objectMap')])][rr('parentTriplesMap')] in tmaps.keys():
								rom = pom[rr('objectMap')]
								
								ptm = tmaps[rom][rr('parentTriplesMap')]
								ptmSubjectTemplate = tmaps[ptm][rr('subjectMap')][rr('template')]
								object = URIRef(self.get_Uri_From_Template(ptmSubjectTemplate,row))
								
							elif rr('objectMap') in pom and rr('parentTriplesMap') in pom[rr('objectMap')]:
								rom = pom[rr('objectMap')]
								
								ptm = rom[rr('parentTriplesMap')]
								
								if ptm in tmaps.keys():
									if rr('joinCondition') in rom:
										join = rom[rr('joinCondition')]
										if rr('child') in join and rr('parent') in join:
											child = join[rr('child')]
											childval = row[child]
											# if null or empty no triple to make fir the fk relationship
											if childval is None or str(childval).strip() == '':
												continue
											
											parent = join[rr('parent')]
											
											# get ref tmap's logical table to get csv, get row in that where col parent val is childval
											fklogicaltable = tmaps[ptm][rr('logicalTable')][rr('tableName')]
											fkcsvinfo = self.get_csvInfo_by_tablename(fklogicaltable)
											fkrdr = fkcsvinfo.get_restarted_reader()
											
											next(fkrdr) # skip the headers
											record = None
											
											for fkrow in fkrdr:
												if fkrow[parent] ==  childval:
													record = fkrow
											# get uri from fk csv's template and fk row
											ptmSubjectTemplate = tmaps[ptm][rr('subjectMap')][rr('template')]
											
											object = URIRef(self.get_Uri_From_Template(ptmSubjectTemplate,record))
							
							elif len(pom_column) > 0 and pom_column in row.keys():
								
								object = self.get_literal(row[pom_column],csvinfo.options.dateformat, literal_lang)
							else:
								object = URIRef(pom_object)
	
							# add to Dataset for quads if non-default graph else add just add triple
							if making_quads:
								gc = self.triples.graph(URIRef(context))
								self.triples.add((subject, predicate, object, gc))
								
							else:
								self.triples.add((subject, predicate, object))
			else:
				# cols mentioned in template that are not cols in csv
				self.errors.append('Fields are named in a template that are not columns in a CSV file.')
		# add every namespace from rml file to outputted triple/quad file
		for n in self.g.namespace_manager.namespaces():
			self.triples.namespace_manager.bind(n[0],n[1])
		self.triples.namespace_manager.bind('rdf', RDF)	
	
		# close any open input files
		self.close_csvs()
	
	def get_literal(self, value, dateformat='%Y-%m-%d', lang=''):
		
		try:
			dt = datetime.strptime(value,dateformat).date()
			return Literal(dt, datatype=XSD.date)
		except ValueError:
			pass
		try: 
			i = int(value)
			return Literal(i, datatype=XSD.integer)
		except ValueError:
			pass
		try:
			f = float(value)
			return Literal(f, datatype=XSD.float)
		except ValueError:
			pass
		
		if lang:
			return Literal(value, lang = lang)
		
		return Literal(value)


	def write_file(self, outfile, format="n3"):
		self.triples.serialize(destination=outfile, format=format)
				
										
	def serialise(self):
		return self.triples.serialize(format="turtle").decode("utf-8")
		
@click.command()
@click.option("--map", "-m", "mapfile", required=True,
				type=click.Path(exists=True),
            	help="Path to the Triples Map configuration file")
@click.option("--csvfile", "-c", "csvfile", required=True,
            	type=click.Path(exists=True),
            	help="Path to each CSV file. This option can be specified for each CSV file.",
            	multiple=True)
@click.option("--outfile", "-o", "outfile", required=True, 
				type=click.Path(),
				help="Path to the output file. It should have '.ttl' file type for triples or a '.nq' for nquads when you have specified a named graph other than 'defaultGraph' for the 'rr:graph' setting in the configuration file.")
@click.option("--separator", "-s",
              help="The CSV separator or delimiter. Defaults to comma.",
              default=",")
@click.option("--encoding", "-e",
              help="The input CSV's file encoding. Defaults to 'utf-8'.",
              default="utf-8")
@click.option("--dateformat", "-d",
              help="If you have dates in your CSV files this describes the format they are in. See 'strptime format codes'. Defaults to '%Y-%m-%d', for example 2022-01-31.",     
              default="%Y-%m-%d")
def process(mapfile, csvfile, outfile, separator=',', encoding='utf-8', dateformat='%Y-%m-%d'):
	""" Generates triples or n-quads in outfile from one or more CSV files according to the configuration in the Triples Map configuration file. """
	csvfiles = list(csvfile)
	if not sys.stdin.isatty():
		csvfiles.extend(list(sys.stdin))
		
	s = Rml()
	
	# take option defaults or those entered
	options = CsvOptions(encoding = encoding, delimiter = separator, dateformat = dateformat)
	
	# load one rml and 1 or more csvs
	s.loadFile(mapfile, csvfiles, options)
	s.create_triples()
	try:
	    s.write_file(outfile)
	except Exception as err:
	    print("Error outputting graph: {0}".format(err))
	    raise
	for e in s.errors:
		print(e)
		
	
if __name__ == "__main__":
	process()

