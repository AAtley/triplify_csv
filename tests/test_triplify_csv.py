from triplify_csv.triplify_csv import rr, Rml, process, CsvOptions
from click.testing import CliRunner
import pytest
import rdflib
from rdflib import Literal, Dataset, XSD
import csv
from rdflib.plugins import sparql
from rdflib import Namespace, Graph, URIRef
from rdflib.namespace import XSD, RDF, RDFS, FOAF, NamespaceManager
import re
from collections import namedtuple
from itertools import takewhile
import os
from pathlib import Path

DATA_DIR = str(Path(__file__).parent / "data")

def path_as_str(tmpdir_factory, outfile):
	return str(tmpdir_factory.mktemp("triples").join(outfile))


@pytest.fixture
def R2RMLTC0007a():
	return DATA_DIR + "/R2RMLTC0007a.ttl"
	

@pytest.fixture
def R2RMLTC0007b():
	return DATA_DIR + "/R2RMLTC0007b.ttl"


@pytest.fixture
def R2RMLTC0007c():
	return DATA_DIR + "/R2RMLTC0007c.ttl"


@pytest.fixture
def R2RMLTC0007d():
	return DATA_DIR + "/R2RMLTC0007d.ttl"

	
@pytest.fixture
def R2RMLTC0007e():
	return DATA_DIR + "/R2RMLTC0007e.ttl"
	
	
@pytest.fixture
def R2RMLTC0007f():
	return DATA_DIR + "/R2RMLTC0007f.ttl"		
	
		
@pytest.fixture
def R2RMLTC0007g():
	return DATA_DIR + "/R2RMLTC0007g.ttl"		

				
@pytest.fixture
def R2RMLTC0007h():
	return DATA_DIR + "/R2RMLTC0007h.ttl"		
				

@pytest.fixture
def R2RMLTC0008a():
	return DATA_DIR + "/R2RMLTC0008a.ttl"		
				

@pytest.fixture
def R2RMLTC0008b():
	return DATA_DIR + "/R2RMLTC0008b.ttl"	
		
		
@pytest.fixture
def R2RMLTC0008c():
	return DATA_DIR + "/R2RMLTC0008c.ttl"	
		

@pytest.fixture
def R2RMLTC0009a():
	return DATA_DIR + "/R2RMLTC0009a.ttl"	
	
	
@pytest.fixture
def R2RMLTC0015a():
	return "./data/R2RMLTC0015a.ttl"
	
	
@pytest.fixture
def Student():
	return DATA_DIR + "/Student.csv"


@pytest.fixture
def Student2():
	return DATA_DIR + "/Student2/Student.csv"
	
	
@pytest.fixture
def Student3():
	return DATA_DIR + "/Student3/Student.csv"

@pytest.fixture
def Sport():
	return DATA_DIR + "/Student3/Sport.csv"

@pytest.fixture
def Emptycsv():
	return DATA_DIR + "/empty.csv"


@pytest.fixture
def not_student():
	return DATA_DIR + "/not_student.csv"


@pytest.fixture
def labels_en():
	return "./data/labels_en.csv"
	
	
@pytest.fixture
def labels_es():
	return "./data/labels_es.csv"
	

@pytest.fixture(scope='session')
def outputfile_ttl(tmpdir_factory):
	return path_as_str(tmpdir_factory,"output.ttl")

	
@pytest.fixture(scope='session')
def outputfile_7b_nquad(tmpdir_factory):
	return path_as_str(tmpdir_factory,"output7b.nq")
	
	
@pytest.fixture(scope='session')
def outputfile_7c(tmpdir_factory):
	return path_as_str(tmpdir_factory,"output7c.ttl")
	
	
@pytest.fixture(scope='session')
def outputfile_7d(tmpdir_factory):
	return path_as_str(tmpdir_factory,"output7d.ttl")
	
	
@pytest.fixture(scope='session')
def outputfile_7e(tmpdir_factory):
	return path_as_str(tmpdir_factory,"output7e.nq")


@pytest.fixture(scope='session')
def outputfile_7f(tmpdir_factory):
	return path_as_str(tmpdir_factory,"output7f.nq")


@pytest.fixture(scope='session')
def outputfile_7g(tmpdir_factory):
	return path_as_str(tmpdir_factory,"output7g.ttl")
	
	
@pytest.fixture(scope='session')
def outputfile_7h(tmpdir_factory):
	return path_as_str(tmpdir_factory,"output7h.ttl")
	
	
@pytest.fixture
def outputfile_8a(tmpdir_factory):
	return path_as_str(tmpdir_factory,"output8a.ttl")
	
	
@pytest.fixture(scope='session')
def outputfile_8b(tmpdir_factory):
	return path_as_str(tmpdir_factory,"output8b.ttl")
	
	
@pytest.fixture(scope='session')
def outputfile_8c(tmpdir_factory):
	return path_as_str(tmpdir_factory,"output8c.ttl")
	
	
@pytest.fixture(scope='session')
def outputfile_9a(tmpdir_factory):
	return path_as_str(tmpdir_factory,"output9a.ttl")


@pytest.fixture(scope='session')
def outputfile_15a(tmpdir_factory):
	return path_as_str(tmpdir_factory,"output15a.ttl")
	
	
@pytest.fixture
def Datecsv():
	return DATA_DIR + "/date.csv"

	
@pytest.fixture
def Dateutfcsv():
	return DATA_DIR + "/dateutf.csv"

	
@pytest.fixture
def Daterml():
	return DATA_DIR + "/daterml.ttl"

	
@pytest.fixture
def Datermlutf():
	return DATA_DIR + "/datermlutf.ttl"

	
@pytest.fixture(scope='session')
def outputfile_date_ttl(tmpdir_factory):
	return path_as_str(tmpdir_factory,"output_date.ttl")
	
	
@pytest.fixture(scope='session')
def outputfile_dateutf_ttl(tmpdir_factory):
	return path_as_str(tmpdir_factory,"output_dateutf.ttl")
	
	
@pytest.fixture(scope='session')
def outputfile_sep_ttl(tmpdir_factory):
	return path_as_str(tmpdir_factory,"output_sep.ttl")	


@pytest.fixture
def sepcsv():
	return DATA_DIR + "/sep.csv"
	
	
@pytest.fixture
def seprml():
	return DATA_DIR + "/sep.ttl"	
	



def test_triplify_csv_help():
  runner = CliRunner()
  result = runner.invoke(process, ['--help'])
  helptext = "Generates triples or n-quads in outfile from one or more CSV files"
  assert result.exit_code == 0
  assert helptext in result.output
  

def test_triplify_csv_examples(tmp_path, Student, R2RMLTC0007a):
	runner = CliRunner()
	with runner.isolated_filesystem(temp_dir=tmp_path) as td:
		# output to outf_name
		outf_name = 'outfile.ttl'
		try:
			result = runner.invoke(process, ['-m', R2RMLTC0007a, '-c', Student, '-o', outf_name])
		except Exception as err:
			print("Error outputting graph: {0}".format(err))
			
			
		assert result.exit_code == 0
		
		# use td and outfile to read graph and test it has a triple
		g = Graph()
		g.parse(outf_name, format="ttl")
		
		i = 0
		for subj, pred, obj in g:
			#count them
			i+=1
		assert i == 1
		
		
  
	
def test_create_triples7a(R2RMLTC0007a, Student):
	rml = Rml()
	# load one rml and 1 or more csvs
	rml.loadFile(R2RMLTC0007a, [Student])
	#rml.add_triples()
	rml.create_triples()
	i = 0
	for s, p, o in rml.triples.triples((None, RDF.type, FOAF.Person)):
		i += 1
		print(f"{s} is the subject 7a")
		print(f"{p} is a predicate 7a")
		print(f"{o} is an object 7a")
	assert i == 1
	
def test_create_triples7b(R2RMLTC0007b, Student):
	rml = Rml()
	# load one rml and 1 or more csvs
	rml.loadFile(R2RMLTC0007b, [Student])
	#rml.add_triples()
	rml.create_triples()
	i = 0

	for s, p, o, c in rml.triples.quads((None, None, None, None)):
		i += 1
		print(f"{s} is the subject")
		print(f"{p} is a predicate")
		print(f"{o} is an object")
		print(f"{c} is the graph")
	assert i == 2
	i = 0
	for s, p, o, c in rml.triples.quads((None, FOAF.name, Literal('Venus'), URIRef('http://example.com/PersonGraph'))):
		i += 1
		print(f"{o} is the name")
		print(f"{c} is the graph")
		assert str(c) == 'http://example.com/PersonGraph'
	assert i == 1
	

def test_create_triples7c(R2RMLTC0007c, Student):
	rml = Rml()
	
	rml.loadFile(R2RMLTC0007c, [Student])
	#rml.add_triples()
	rml.create_triples()
	# one Person
	i = 0
	for s, p, o in rml.triples.triples((None, RDF.type, FOAF.Person)):
		i += 1
		print(f"{s} is the subject 7c")
		print(f"{p} is a predicate 7c")
		print(f"{o} is an object 7c")
	assert i == 1
	
	# one student
	i = 0
	for s, p, o in rml.triples.triples((None, RDF.type, URIRef('http://example.com/Student'))):
		i += 1
		print(f"{s} is the subject 7c")
		print(f"{p} is a predicate 7c")
		print(f"{o} is an object 7c")
	assert i == 1
	
	# their name
	i = 0
	for s, p, o in rml.triples.triples((URIRef('http://example.com/Student/10/Venus'), FOAF.name, Literal('Venus'))):
		i += 1
		print(f"{s} is the subject 7c")
		print(f"{p} is a predicate 7c")
		print(f"{o} is an object 7c")
	assert i == 1
	
	# their ID
	i = 0
	for s, p, o in rml.triples.triples((URIRef('http://example.com/Student/10/Venus'), URIRef('http://example.com/id'), Literal(10))):
		i += 1
		print(f"{s} is the subject 7c")
		print(f"{p} is a predicate 7c")
		print(f"{o} is an object 7c")
	assert i == 1

def test_create_write_out7a(R2RMLTC0007a, Student, outputfile_ttl):
	rml = Rml()
	# load one rml and 1 or more csvs
	rml.loadFile(R2RMLTC0007a, [Student])
	#rml.add_triples()
	rml.create_triples()
	rml.write_file(outputfile_ttl)
	g = Graph()
	g.parse(outputfile_ttl, format='ttl')
	i = 0
	for subj, pred, obj in g:
		#count them
		i+=1
	assert i == 1
	

def test_load_create_write_out7b(R2RMLTC0007b, Student, outputfile_7b_nquad):
		rml = Rml()
		# load one rml and 1 or more csvs
		rml.loadFile(R2RMLTC0007b, [Student])
#		rml.add_triples()

		rml.create_triples()
		rml.write_file(outputfile_7b_nquad,format="nquads")
		g = Dataset() 
		g.parse(outputfile_7b_nquad, format="nquads") 
		i = 0
		for s, p, o, c in g.quads((None, None, None, None)):
			i += 1
			print(f"{s} is the subject")
			print(f"{p} is a predicate")
			print(f"{o} is an object")
			print(f"{c} is the graph")
			
		assert i == 2
		
		i = 0
		for s, p, o, c in g.quads((None, FOAF.name, Literal('Venus'), URIRef('http://example.com/PersonGraph'))):
			i += 1
			print(f"{o} is the name")
			print(f"{c} is the graph")
			assert str(c) == 'http://example.com/PersonGraph'
			
		assert i == 1


def test_load_create_write_out7c(R2RMLTC0007c, Student, outputfile_7c):
		rml = Rml()
		# load one rml and 1 or more csvs
		rml.loadFile(R2RMLTC0007c, [Student])
#		rml.add_triples()
		rml.create_triples()
		rml.write_file(outputfile_7c)
		g = Graph() 
		g.parse(outputfile_7c, format="ttl") 
		i = 0
		for s, p, o  in g.triples((None, None, None)):
			i += 1
			print(f"{s} is the subject")
			print(f"{p} is a predicate")
			print(f"{o} is an object")
			
		assert i == 4
		
		#  Venus's name is 'Venus'
		i = 0
		for s, p, o in g.triples((URIRef('http://example.com/Student/10/Venus'), FOAF.name, Literal('Venus'))):
			i += 1
		assert i == 1
		
		#  Venus's ID is 10
		i = 0
		for s, p, o in g.triples((URIRef('http://example.com/Student/10/Venus'), URIRef('http://example.com/id'), Literal(10))):
			i += 1	
		assert i == 1
		
		#  Venus is a Person
		i = 0
		for s, p, o in g.triples((URIRef('http://example.com/Student/10/Venus'), RDF.type, FOAF.Person)):
			i += 1	
		assert i == 1

		#  Venus is a Student
		i = 0
		for s, p, o in g.triples((URIRef('http://example.com/Student/10/Venus'), RDF.type, URIRef('http://example.com/Student'))):
			i += 1	
		assert i == 1
		
		
def test_create_write_out7d(R2RMLTC0007d, Student, outputfile_7d):
		rml = Rml()
		# load one rml and 1 or more csvs
		rml.loadFile(R2RMLTC0007d, [Student])
		#rml.add_triples()
		rml.create_triples()
		rml.write_file(outputfile_7d)
		g = Graph() 
		g.parse(outputfile_7d, format="ttl") 
		i = 0
		for s, p, o  in g.triples((None, None, None)):
			i += 1
			print(f"{s} is the subject")
			print(f"{p} is a predicate")
			print(f"{o} is an object")
			
		assert i == 4
		
		#  Venus's name is 'Venus'
		i = 0
		for s, p, o in g.triples((URIRef('http://example.com/Student/10/Venus'), FOAF.name, Literal("Venus"))):
			i += 1
		assert i == 1
		
		#  Venus's ID is 10
		i = 0
		for s, p, o in g.triples((URIRef('http://example.com/Student/10/Venus'), URIRef('http://example.com/id'), Literal(10))):
			i += 1	
		assert i == 1
		
		#  Venus is a Person
		i = 0
		for s, p, o in g.triples((URIRef('http://example.com/Student/10/Venus'), RDF.type, FOAF.Person)):
			i += 1	
		assert i == 1

		#  Venus is a Student
		i = 0
		for s, p, o in g.triples((URIRef('http://example.com/Student/10/Venus'), RDF.type, URIRef('http://example.com/Student'))):
			i += 1	
		assert i == 1
		
def test_create_write_out7e(R2RMLTC0007e, Student, outputfile_7e):
		rml = Rml()
		# load one rml and 1 or more csvs
		rml.loadFile(R2RMLTC0007e, [Student])
		#rml.add_triples()
		rml.create_triples()
		rml.write_file(outputfile_7e, format="nquads")
		g = Dataset() 
		g.parse(outputfile_7e, format="nquads") 
		i = 0
		for s, p, o, c in g.quads((None, None, None, None)):
			i += 1
			print(f"{s} is the subject")
			print(f"{p} is a predicate")
			print(f"{o} is an object")
			print(f"{c} is an graph")
		assert i == 3
		
		#  Venus's name is 'Venus'
		i = 0
		for s, p, o, c in g.quads((URIRef('http://example.com/Student/10/Venus'), FOAF.name, Literal('Venus'),URIRef('http://example.com/PersonGraph'))):
			i += 1
		assert i == 1
		
		#  Venus's ID is 10
		i = 0
		for s, p, o, c in g.quads((URIRef('http://example.com/Student/10/Venus'), URIRef('http://example.com/id'), Literal(10),URIRef('http://example.com/PersonGraph'))):
			i += 1	
		assert i == 1
		
		#  Venus is a Person
		i = 0
		for s, p, o, c in g.quads((URIRef('http://example.com/Student/10/Venus'), RDF.type, FOAF.Person,URIRef('http://example.com/PersonGraph'))):
			i += 1	
		assert i == 1


def test_create_write_out7f(R2RMLTC0007f, Student, outputfile_7f):
		rml = Rml()
		# load one rml and 1 or more csvs
		rml.loadFile(R2RMLTC0007f, [Student])
		rml.create_triples()
		rml.write_file(outputfile_7f, format="nquads")
		g = Dataset() 
		g.parse(outputfile_7f, format="nquads") 
		i = 0
		for s, p, o, c in g.quads((None, None, None, None)):
			i += 1
			print(f"{s} is the subject")
			print(f"{p} is a predicate")
			print(f"{o} is an object")
			print(f"{c} is an graph")
		assert i == 3
		
		#  Venus's name is 'Venus'
		i = 0
		for s, p, o, c in g.quads((URIRef('http://example.com/Student/10/Venus'), FOAF.name, Literal('Venus'),URIRef('http://example.com/PersonGraph'))):
			i += 1
		assert i == 1
		
		#  Venus's ID is 10
		i = 0
		for s, p, o, c in g.quads((URIRef('http://example.com/Student/10/Venus'), URIRef('http://example.com/id'), Literal(10),URIRef('http://example.com/PersonGraph'))):
			i += 1	
		assert i == 1
		
		#  Venus is a Person
		i = 0
		for s, p, o, c in g.quads((URIRef('http://example.com/Student/10/Venus'), RDF.type, FOAF.Person,URIRef('http://example.com/PersonGraph'))):
			i += 1	
		assert i == 1
		


def test_create_write_out7g(R2RMLTC0007g, Student, outputfile_7g):
		rml = Rml()
		# load one rml and 1 or more csvs
		rml.loadFile(R2RMLTC0007g, [Student])
		rml.create_triples()
		rml.write_file(outputfile_7g)
		g = Graph() 
		g.parse(outputfile_7g, format="ttl") 
		i = 0
		for s, p, o in g.triples((None, None, None)):
			i += 1
			print(f"{s} is the subject")
			print(f"{p} is a predicate")
			print(f"{o} is an object")
		assert i == 2
		
		#  Venus's name is 'Venus'
		i = 0
		for s, p, o  in g.triples((URIRef('http://example.com/Student/10/Venus'), FOAF.name, Literal('Venus'))):
			i += 1
		assert i == 1	
		
		#  Venus is a Person
		i = 0
		for s, p, o in g.triples((URIRef('http://example.com/Student/10/Venus'), RDF.type, FOAF.Person)):
			i += 1	
		assert i == 1	

def test_tmaps7g(R2RMLTC0007g, Student, outputfile_7g):
	# use rml triples directly as config file parsed structure
	rml = Rml()
	rml.loadFile(R2RMLTC0007g, [Student])
	
	tmaps = rml.tmaps()
	
	tkey = ''
	for key in tmaps.keys():
		tkey = key
		print(tmaps[key].keys())
	
	assert "http://example.com/base/TriplesMap1" in tmaps
	
	assert len(tmaps[key]['poms']) == 2
	for pom in tmaps[key]['poms']:
		print(pom)
		
	if rr('objectMap') in tmaps[tkey]['poms'][0].keys():
		assert tmaps[tkey]['poms'][0][rr('objectMap')][rr('column')] == "Name"
		assert tmaps[tkey]['poms'][1][rr('object')] == "http://xmlns.com/foaf/0.1/Person"
	else:
		assert tmaps[tkey]['poms'][1][rr('objectMap')][rr('column')] == "Name"
		assert tmaps[tkey]['poms'][0][rr('object')] == "http://xmlns.com/foaf/0.1/Person"
		
	assert tmaps[tkey][rr('logicalTable')][rr('tableName')] == 'Student'
	
	assert tmaps[tkey][rr('subjectMap')][rr('template')] == 'http://example.com/Student/{\"ID\"}/{\"Name\"}'
	
	
def test_tmaps7h(R2RMLTC0007h, Student):
	s = Rml()
	s.loadFile(R2RMLTC0007h,[Student])
	tmaps = s.tmaps()
	
	tkey = ''
	for key in tmaps.keys():
		tkey = key
		print(tmaps[key].keys())
		
	assert rr('graphMap') in tmaps[tkey][rr('subjectMap')]
	
	assert rr('column') in tmaps[tkey][rr('subjectMap')][rr('graphMap')]
	
	assert rr('termType') in tmaps[tkey][rr('subjectMap')][rr('graphMap')]
	
def test_declared_defaultGraph(R2RMLTC0007g, Student):
	s = Rml()
	s.loadFile(R2RMLTC0007g,[Student])
	s.create_triples()
	
	assert not s.making_quads
	
def test_create_triple_but_table_csv_dont_match7a(R2RMLTC0007a, not_student):
	s = Rml()
	# load one rml and 1 or more csvs
	s.loadFile(R2RMLTC0007a, [not_student])
	s.create_triples()
	assert len(s.errors) == 1
	assert s.errors[0] == 'A csv for table Student was not found'
	
def test_create_triple_but_csv_empty7a(R2RMLTC0007a, Emptycsv):
	s = Rml()
	# load one rml and 1 or more csvs
	s.loadFile(R2RMLTC0007a, [Emptycsv])
	s.create_triples()
	assert len(s.errors) == 2
	assert s.errors[0] == 'csv file empty may be empty'
	assert s.errors[1] == 'A csv for table Student was not found'
	
def test_create_write_out7h(R2RMLTC0007h, Student, outputfile_7h):
		rml = Rml()
		# load one rml and 1 or more csvs
		rml.loadFile(R2RMLTC0007h, [Student])
		rml.create_triples()
		rml.write_file(outputfile_7h)
		g = Graph() 
		g.parse(outputfile_7h, format="ttl") 
		i = 0
		for s, p, o in g.triples((None, None, None)):
			i += 1
			print(f"{s} is the subject")
			print(f"{p} is a predicate")
			print(f"{o} is an object")
		assert i == 0
		
		assert len(rml.errors) == 1
		assert rml.errors[0] == 'Graph specified should not be a literal value'
		
def test_tmaps8a(R2RMLTC0008a, Student2, outputfile_8a):
	# use rml triples directly as config file parsed structure
	rml = Rml()
	rml.loadFile(R2RMLTC0008a, [Student2])
	
	tmaps = rml.tmaps()
	
	tkey = ''
	for key in tmaps.keys():
		tkey = key
		print(tmaps[key].keys())
	
	assert "http://example.com/base/TriplesMap1" in tmaps
	
	assert len(tmaps[key]['poms']) == 4
	
	assert tmaps[tkey][rr('logicalTable')][rr('tableName')] == 'Student'
	
	assert tmaps[tkey][rr('subjectMap')][rr('graphMap')][rr('template')] == 'http://example.com/graph/Student/{\"ID\"}/{\"Name\"}'
	
	assert tmaps[tkey][rr('subjectMap')][rr('template')] == 'http://example.com/Student/{\"ID\"}/{\"Name\"}'
	
def test_create_write_out8a(R2RMLTC0008a, Student2, outputfile_8a):
		rml = Rml()
		# load one rml and 1 or more csvs
		rml.loadFile(R2RMLTC0008a, [Student2])
		
		tmaps = rml.tmaps()
		
		tkey = ''
		for key in tmaps.keys():
			tkey = key
		
		context_template = tmaps[tkey][rr('subjectMap')][rr('graphMap')][rr('template')] 
		
		logical_table = tmaps[tkey][rr('logicalTable')][rr('tableName')]
		
		csvinfo = rml.get_csvInfo_by_tablename(logical_table)
		
		rdr = csvinfo.get_restarted_reader()
		next(rdr) # skip the headers
		context_uri = ''
		
		for row in rdr:
			context_uri = rml.get_Uri_From_Template(context_template, row)
			
		print('context_uri = ' + str(context_uri))
		
		assert context_uri == 'http://example.com/graph/Student/10/Venus%20Williams'
		
		rml.create_triples()
		rml.write_file(outputfile_8a, format="nquads")
		g = Dataset()
		g.parse(outputfile_8a, format="nquads") 
		i = 0
		for s, p, o, c in g.quads((None, None, None, None)):
			i += 1
			print(f"{s} is the subject")
			print(f"{p} is a predicate")
			print(f"{o} is an object")
			print(f"{c} is an graph")
		assert i == 4
		
		#  Venus's name is 'Venus Williams'
		i = 0
		for s, p, o, c in g.quads((URIRef('http://example.com/Student/10/Venus%20Williams'), FOAF.name, Literal('Venus Williams'), URIRef(context_uri))):
			i += 1
		assert i == 1
		
		#  Venus is a Person
		i = 0
		for s, p, o, c in g.quads((URIRef('http://example.com/Student/10/Venus%20Williams'), RDF.type, FOAF.Person, URIRef(context_uri))):
			i += 1	
		assert i == 1
		
		#  Venus' Sport is tennis
		i = 0
		for s, p, o, c in g.quads((URIRef('http://example.com/Student/10/Venus%20Williams'), URIRef('http://example.com/Sport'), Literal('Tennis'), URIRef(context_uri))):
			i += 1	
		assert i == 1
		
		#  Venus' id is 10
		i = 0
		for s, p, o, c in g.quads((URIRef('http://example.com/Student/10/Venus%20Williams'), URIRef('http://example.com/id'), Literal(10), URIRef(context_uri))):
			i += 1	
		assert i == 1
		
		assert len(rml.errors) == 0
		
def test_template_to_uri():
	template = 'p://a/{\"col1\"}/{\"col2\"}'
	row = {}
	row['col1'] = 'b b'
	row['col2'] = 'c'
	rml = Rml()
	uri = rml.get_Uri_From_Template(template, row)
		
	assert uri == 'p://a/b%20b/c'
	
def test_tmaps8b(R2RMLTC0008b, Student2, outputfile_8b):
	# use rml triples directly as config file parsed structure
	rml = Rml()
	rml.loadFile(R2RMLTC0008b, [Student2])
	
	tmaps = rml.tmaps()
	
	tkey = ''
	for key in tmaps.keys():
		tkey = key
		
		
	t1 = "http://example.com/base/TriplesMap1"
	t2 = "http://example.com/base/TriplesMap2"
	print(tmaps[t1].keys()) 
	print(tmaps[t2].keys())
	
	assert rr('subjectMap') in tmaps[t1]
	assert rr('subjectMap') in tmaps[t2]
	
	
	assert "http://example.com/base/TriplesMap1" in tmaps
	
	assert "http://example.com/base/TriplesMap2" in tmaps

	assert "http://example.com/base/RefObjectMap1" in tmaps 

	rom = "http://example.com/base/RefObjectMap1"
	
	assert tmaps[rom][rr('parentTriplesMap')] == rml.base + "TriplesMap2"
	
	
	
def test_create_write_out8b(R2RMLTC0008b, Student2, outputfile_8b):
		rml = Rml()
		# load one rml and 1 or more csvs
		rml.loadFile(R2RMLTC0008b, [Student2])
		
		tmaps = rml.tmaps()
		
		# test some config values
		
		rml.create_triples()
		print(rml.errors)
		rml.write_file(outputfile_8b, format="ttl")
		g = Graph()
		g.parse(outputfile_8b, format="ttl") 
		
		# check triple count
		i = 0
		for s, p, o in g.triples((None, None, None)):
			i += 1
			print(f"{s} is the subject")
			print(f"{p} is a predicate")
			print(f"{o} is an object")
		assert i == 5
		
		# check VW's sport is Tennis
		i = 0
		for s, p, o in g.triples((URIRef('http://example.com/Student/10/Venus%20Williams'), URIRef('http://example.com/Sport'), None)):
			i += 1
			assert str(o) == "http://example.com/Tennis"
		assert i == 1
		
		assert len(rml.errors) == 0
		
	
def test_tmaps8c(R2RMLTC0008c, Student2, outputfile_8c):
	# use rml triples directly as config file parsed structure
	rml = Rml()
	rml.loadFile(R2RMLTC0008c, [Student2])
	
	tmaps = rml.tmaps()
	
	tkey = ''
	for key in tmaps.keys():
		tkey = key 
		

	predlist = str(tmaps[tkey]['poms'][0][rr('predicate')]).split(',')
	
	assert len('nocomma'.split(',')) == 1
	for nc in 'nocomma'.split(','):
		assert nc == 'nocomma'
	
	
	assert 'http://xmlns.com/foaf/0.1/name' in predlist
	assert 'http://example.com/name' in predlist
	assert len(predlist) == 2
	
def test_create_write_out8c(R2RMLTC0008c, Student2, outputfile_8c):
		rml = Rml()
		# load one rml and 1 or more csvs
		rml.loadFile(R2RMLTC0008c, [Student2])
		
		tmaps = rml.tmaps()
		
		# test some config values
		
		rml.create_triples()
		print(rml.errors)
		rml.write_file(outputfile_8c, format="ttl")
		g = Graph()
		g.parse(outputfile_8c, format="ttl") 
		
		# check triple count
		i = 0
		for s, p, o in g.triples((None, None, None)):
			i += 1
			print(f"{s} is the subject")
			print(f"{p} is a predicate")
			print(f"{o} is an object")
		assert i == 2
		
		# check VW's FOAF.name
		i = 0
		for s, p, o in g.triples((URIRef('http://example.com/Student/10/Venus%20Williams'), FOAF.name, None)):
			i += 1
		assert i == 1
		
		# check VW's ex.name
		i = 0
		for s, p, o in g.triples((URIRef('http://example.com/Student/10/Venus%20Williams'), URIRef('http://example.com/name'), None)):
			i += 1
		assert i == 1
				
		assert len(rml.errors) == 0
		
def test_tmaps9a(R2RMLTC0009a, Student3, Sport, outputfile_9a):
	# use rml triples directly as config file parsed structure
	rml = Rml()
	rml.loadFile(R2RMLTC0009a, [Student3, Sport])
	
	tmaps = rml.tmaps()
	
	tkey1 =  "http://example.com/base/TriplesMap1"
	
	tkey2 =  "http://example.com/base/TriplesMap2" 
	
	assert tkey1 in tmaps.keys()
	assert tkey2 in tmaps.keys()
	
	ppom = {}
	for pom in tmaps[tkey1]['poms']:
		if pom[rr('predicate')] == 'http://example.com/ontology/practises':
			ppom = pom
		else:
			print('not found pom')
			
			
	assert ppom[rr('objectMap')][rr('parentTriplesMap')] == tkey2

	assert ppom[rr('objectMap')][rr('joinCondition')][rr('child')] == 'Sport'
	
	assert ppom[rr('objectMap')][rr('joinCondition')][rr('parent')] == 'ID'
	
	assert tmaps[tkey2]['poms'][0][rr('objectMap')][rr('column')] == 'Name'
	
	assert len(tmaps[tkey1]['poms']) == 2
	assert len(tmaps[tkey2]['poms']) == 1
	assert rr('parentTriplesMap') not in  tmaps[tkey2]['poms'][0][rr('objectMap')]
	
	assert tmaps[tkey1][rr('logicalTable')][rr('tableName')] == 'Student'
	
	assert tmaps[tkey2][rr('logicalTable')][rr('tableName')] == 'Sport'
		

def test_create_write_out9a(R2RMLTC0009a, Student3, Sport, outputfile_9a):
		rml = Rml()
		# load one rml and 1 or more csvs
		rml.loadFile(R2RMLTC0009a, [Student3, Sport])
		
		tmaps = rml.tmaps()
		
		# test some config values
		for x in rml.csvInfoList:
			print(x.tablename)
		rml.create_triples()
		print(rml.errors)
		rml.write_file(outputfile_9a, format="ttl")
		g = Graph()
		g.parse(outputfile_9a, format="ttl") 
		
		# check triple count
		i = 0
		for s, p, o in g.triples((None, None, None)):
			i += 1
			print(f"{s} is the subject")
			print(f"{p} is a predicate")
			print(f"{o} is an object")
		assert i == 4
		
		# check VW's FOAF.name
		i = 0
		for s, p, o in g.triples((URIRef('http://example.com/resource/student_10'), FOAF.name, Literal('Venus Williams'))):
			i += 1
		assert i == 1
		
		# check DM's FOAF.name
		i = 0
		for s, p, o in g.triples((URIRef('http://example.com/resource/student_20'), FOAF.name, Literal('Demi Moore'))):
			i += 1
		assert i == 1
		
		# check VW practices Tennis
		i = 0
		for s, p, o in g.triples((URIRef('http://example.com/resource/student_10'), URIRef('http://example.com/ontology/practises'), URIRef('http://example.com/resource/sport_100'))):
			i += 1
		assert i == 1
		
		# check VW practices Tennis
		i = 0
		for s, p, o in g.triples((URIRef('http://example.com/resource/sport_100'), URIRef('http://www.w3.org/2000/01/rdf-schema#label'), Literal('Tennis'))):
			i += 1
		assert i == 1

def test_load_create_write_out15a(R2RMLTC0015a, labels_en, labels_es, outputfile_15a):
	rml = Rml()
	# load one rml and 1 or more csvs
	rml.loadFile(R2RMLTC0015a, [labels_en, labels_es])
	rml.create_triples()
	rml.write_file(outputfile_15a)
	g = Graph()
	g.parse(outputfile_15a, format="ttl")
	i = 0
	for s, p, o in g.triples((None, RDFS.label, Literal('Irlanda', lang = 'es'))):
		i += 1
		print(f"{s} is the subject")
		print(f"{p} is a predicate")
		print(f"{o} is an object")
		
	assert i == 1
	
	
def test_create_write_date(Daterml, Datecsv,  outputfile_date_ttl):
		rml = Rml()
		
		options = CsvOptions(dateformat='%d/%m/%Y')
		
		# load one rml and 1 or more csvs
		rml.loadFile(Daterml, [Datecsv], options)
		
		
		rml.create_triples()
		print(rml.errors)
		rml.write_file(outputfile_date_ttl, format="ttl")
		g = Graph()
		g.parse(outputfile_date_ttl, format="ttl") 
		
		# check triple count
		i = 0
		for s, p, o in g.triples((None, None, Literal('2021-01-31',datatype=XSD.date))):
			i += 1
			print(f"{s} is the subject")
			print(f"{p} is a predicate")
			print(f"{o} is an object")
		assert i == 1
		
			
def test_create_write_dateutf(Datermlutf, Dateutfcsv,  outputfile_dateutf_ttl):
		rml = Rml()
		
		options = CsvOptions(dateformat='%d/%m/%Y', encoding='utf-32')
		
		# load one rml and 1 or more csvs
		rml.loadFile(Datermlutf, [Dateutfcsv], options)
		
		
		rml.create_triples()
		print(rml.errors)
		rml.write_file(outputfile_dateutf_ttl, format="ttl")
		g = Graph()
		g.parse(outputfile_dateutf_ttl, format="ttl") 
		
		# check triple count
		i = 0
		for s, p, o in g.triples((None, None, Literal('2021-01-31',datatype=XSD.date))):
			i += 1
			print(f"{s} is the subject")
			print(f"{p} is a predicate")
			print(f"{o} is an object")
		assert i == 1
		
			
def test_create_write_separator(seprml, sepcsv, outputfile_sep_ttl):
	rml = Rml()
	
	options = CsvOptions(dateformat='%d/%m/%Y', delimiter='|')
	# load one rml and 1 or more csvs
	rml.loadFile(seprml, [sepcsv], options)
	
	
	rml.create_triples()
	print(rml.errors)
	rml.write_file(outputfile_sep_ttl, format="ttl")
	g = Graph()
	g.parse(outputfile_sep_ttl, format="ttl")
	print(XSD.date)
	# check triple count
	i = 0
	for s, p, o in g.triples((None, None, Literal('2021-01-31',datatype=XSD.date))):
		i += 1
		
	assert i == 1
				
