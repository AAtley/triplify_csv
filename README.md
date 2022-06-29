triplify\_csv
=============

Features
========

Generates RDF triples or quads in Turtle or NQuad syntax from one or more CSV files and a configuration file.

Installation
============

triplify\_csv can be installed from PyPI using 'pip':

```
pip install triplify_csv
```

Usage
=====

triplify\_csv installs as both a package and command line interface tool

**Example of using the package**

	from TriplifyCsv import Rml, CsvOptions
	
	# config mapping files are .ttl files
	configfile = 'myconfig.ttl'
	
	# csv files should be .csv files
	csvfile1, csvfile2 = 'mycsv1.csv', 'mycsv2.csv'
	
	# output file must have either a .ttl extension for turtle triples
	# or a .nq extension for quads
	outputfile = 'mytriples.ttl'
	
	rml = Rml()
	
	# default date format of dates in your CSV files is '%Y-%m-%d'
	# default csv delimiter is ','
	# override the defaults by setting options
	options = CsvOptions(dateformat='%d/%m/%Y', delimiter='|')
	
	# load one rml and one or more csvs
	rml.loadFile(configfile, [csvfile1,csvfile2], options)
	 
	rml.create_triples()
	
	# "nquads" for named graphs need a .nq extension
	# here we are generating triples so .ttl for turtle syntax
	rml.write_file(outputfile, format="ttl")



**Example of CLI use - help text**

To display full help text on the options enter the following at the command line

```
triplify_csv --help
```


**Example of CLI use - making triples** The same example as the one in code above as a CLI call instead ...

```
triplify_csv -m 'myconfig.ttl' -c 'mycsv1.csv' -c 'mycsv2.csv' -o 'mytriples.ttl'
```

**How to make your configuration file**

The configuration file contains a set of mappings for triplify\_csv to follow to set the subjects, predicates and objects or literal values of your triples or nquads from the data in one or more CSV files. These mappings are RDF triples in the turtle syntax. The terms that can be used are a subset of the terms defined in the R2RML standard.

R2RML was not designed for this purpose. R2RML is '.. a language for expressing customized mappings from relational databases to RDF datasets.' (see [https://www.w3.org/TR/r2rml/](https://www.w3.org/TR/r2rml/) ). Triplify\_csv uses a subset of R2RML to express customised mappings from CSV files to RDF datasets. Where R2RML refers to the tables of a database using 'rr:logicalTable' this should be understood in the triplify\_csv use of R2RML as referring to the name (without '.csv') of a corresponding csv file. 'rr:sqlQuery', the term of the R2RML language that lets you express mappings from database queries to RDF isn't supported in the triplify\_csv usage. Also, there is no need to support 'rr:sqlVersion'.

For a complete list of what parts of the R2RML language are supported see the examples in the /tests folder and refer to the R2RML test cases document ([https://www.w3.org/TR/rdb2rdf-test-cases/](https://www.w3.org/TR/rdb2rdf-test-cases/)). As of version 0.2.0 the test cases supported are

- R2RMLTC0007a - Typing resources by relying on rdf:type predicate
- R2RMLTC0007b - Assigning triples to Named Graphs
- R2RMLTC0007c - One column mapping, using rr:class
- R2RMLTC0007d - One column mapping, specifying an rr:predicateObjectMap with rdf:type
- R2RMLTC0007e - One column mapping, using rr:graphMap and rr:class
- R2RMLTC0007f - One column mapping, using rr:graphMap and specifying an rr:predicateObjectMap with rdf:type
- R2RMLTC0007g - Assigning triples to the default graph
- R2RMLTC0007h - Assigning triples to a non-IRI named graph
- R2RMLTC0008a - Generation of triples to a target graph by using rr:graphMap and rr:template
- R2RMLTC0008b - Generation of triples referencing object map
- R2RMLTC0008c - Generation of triples by using multiple predicateMaps within a rr:predicateObjectMap
- R2RMLTC0009a - Generation of triples from foreign key relations
- R2RMLTC0015a - Generation of language tags for plain literals from a CSV 'table' with language information
	- note: this test uses a separate CSV file for each language and differs from the original test case (in the [rdf-test-cases page](https://www.w3.org/TR/rdb2rdf-test-cases/)) which uses 'rr:sqlQuery' to select tags in each language from a single table.

Copyright © 2015 W3C® (MIT, ERCIM, Keio, Beihang). This software or document includes material copied from or derived from 'R2RML: RDB to RDF Mapping Language' [http://www.w3.org/TR/2012/REC-r2rml-20120927/](http://www.w3.org/TR/2012/REC-r2rml-20120927/) and 'R2RML and Direct Mapping Test Cases' [http://www.w3.org/TR/2012/NOTE-rdb2rdf-test-cases-20120814/](http://www.w3.org/TR/2012/NOTE-rdb2rdf-test-cases-20120814/)

**Simple config file example** Suppose you have a CSV file containing details of contacts (example CSV below) and you want to generate RDF data from this using FOAF, the R2RML config file might look like this ...

	@prefix rr: <http://www.w3.org/ns/r2rml#> .
	@prefix foaf: <http://xmlns.com/foaf/0.1/> .
	@prefix ex: <http://example.com/> .
	@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
	@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
	@base <http://example.com/base/> .
	
	<TriplesMap1> a rr:TriplesMap;
	rr:logicalTable [ rr:tableName "\"Contacts\"" ];
	
	rr:subjectMap [ rr:template "http://example.com/Contact/{\"ID\"}/{\"Name\"}";
	 rr:class foaf:Person;
	];
	
	rr:predicateObjectMap [ rr:predicate ex:id ;
	 rr:objectMap [ rr:column "\"ID\"" ;  ] ;
	];
	
	rr:predicateObjectMap [ rr:predicate foaf:name ;
	 rr:objectMap [ rr:column "\"Name\"" ; ] ;
	];
	
	rr:predicateObjectMap [ rr:predicate foaf:interest ;
	  rr:objectMap [ rr:column "\"Interest\"" ; ] ;
	];
	
	.



Create a CSV file called 'Contacts.csv' using commas as delimiters between the following values (shown here in a table) ...

ID  | Name | Interest
:---- | :---- | :--------
10 | John Smith | https://en.m.wikipedia.org/wiki/Tennis
20 | Joe Bloggs | https://en.m.wikipedia.org/wiki/Golf
30 | Mr Bun | https://en.m.wikipedia.org/wiki/Spam_(food) 


Now, with triplify_csv installed save the R2RML config file as 'contactsmap.ttl' and the csv file as 'Contacts.csv' and generate the output containing your triples to a file called 'contactstriples.ttl' (for example) with the following command ...

```
triplify_csv -m 'contactsmap.ttl' -c 'Contacts.csv' -o 'contactstriples.ttl'
```

The resulting triples in turtle syntax in the 'contactstriples.ttl' file would look like this ...


	@prefix ex: <http://example.com/> .
	@prefix foaf: <http://xmlns.com/foaf/0.1/> .
	@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
	
	<http://example.com/Contact/10/John%20Smith> a foaf:Person ;
	    ex:id 10 ;
	    foaf:interest "https://en.m.wikipedia.org/wiki/Tennis" ;
	    foaf:name "John Smith" .
	
	<http://example.com/Contact/20/Joe%20Bloggs> a foaf:Person ;
	    ex:id 20 ;
	    foaf:interest "https://en.m.wikipedia.org/wiki/Golf" ;
	    foaf:name "Joe Bloggs" .
	
	<http://example.com/Contact/30/Mr%20Bun> a foaf:Person ;
	    ex:id 30 ;
	    foaf:interest "https://en.m.wikipedia.org/wiki/Spam\_(food)" ;
	    foaf:name "Mr Bun" .


