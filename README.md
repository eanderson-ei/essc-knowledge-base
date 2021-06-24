# README

This project houses the Latin America & Caribbean (LAC) Environment & Energy S C (ESSC) knowledge base. The knowledge base uses NLP and a graph database to facilitate discovery of Mission projects and related documents.

Project Epics describe the discrete steps required for buildout, Stories within each Epic describe required components for that Epic.

**TODO**

Try subbing 'bolt+s' for 'neo4j+s'  in the URI with the Aura database.

### Project Epics

1. [Generate keywords to use as a tagging system from a sample of documents](#1.-tag-system)
2. [Automate tagging of documents and upload to graph database for initial build out](#2.-initial-buildout)
3. [Internal automatic tagging of new documents and keyword search of the graph database](#3.-internal-update-and-search)
4. [Host all functionality on a web platform, allow external upload, and user search](#4.-web-platform)
5. Facilitate discovery of related content though manual graph exploration (asp.)
6. Dashboard to display metrics on environment and energy activities (asp.)

### Resources

- See the Project Description here ([link](https://docs.google.com/document/d/1cfgZEfb0J5gQ3X0CsNXNijHO3IlewLzTGm2BZNOGJxs/edit?usp=sharing)).
- Scoping Sheet ([link](https://docs.google.com/document/d/1i3VdKv_tujqSEX_N9zAzUxc-Cc8_d8eSk-CAhNlqJ3A/edit?usp=sharing))
- Energy Project Data Sheet ([link](https://docs.google.com/spreadsheets/d/1z6cpQGhFQclxufvS1hr8XuSSEEVXAL_Zc8hJGeBm8P4/edit?usp=sharing)): current database of project metadata and links to resources. The Writeups & Reports tab is main for the reports and writeups. Copy/paste to `data/reports.csv` if updates are needed.
- Use Case Exercise ([link](https://docs.google.com/spreadsheets/d/1w95aic2kBmFRKmEIapeyBtqR9cPyhn-ZNaUP0i5RZvw/edit?usp=sharing)): original use case exercise from Sue

### Roles

* Sue Hoye: Approver
* Claire Price: helping improve metadata for projects, find missing information, draft project descriptions.
* Izzie: helper and search phrase lead

## 1. Tag System

The tag system will take as input a representative subset of PDF resources from the Energy Project Data Sheet and recommend, using TextRank, the entities that have the highest 'importance' within the corpus. These tags will then be cleaned with human review and hyperparameter tuning, and augmented to support expected use cases. 

The first run of the system was attempted using a simple GUI interface with google sheet backend. After the initial proof-of-concept, Izzie downloaded all linked reports, writeups and factsheets and an automated process was run against the entire corpus.

The PDF reader used for this project is `tika`, which requires Java to be installed (setting up another user would require python, java, SQLStudio).

### Stories

1. Read report
2. Convert PDF to text
3. Convert text to tags
4. Summarize text
5. Save summary, project number, filename, link and notes to graph database
6. Upload list of tags and associated file name to graph database, relate tag to report title
7. Upload project numbers, project names, and file names to database (to link files and projects)
8. Use graph algorithms to rank tags (consider centrality, importance, etc.) or rank based on number of relationships
9. Export tags to Excel for ranking, review, and augmentation with topical tags

To exclude specific entity types, add them to the not_entity_types in analyze() of text_rank. See [docs](https://spacy.io/api/annotation#named-entities) for list of entity types.

[PyTextRank](https://spacy.io/universe/project/spacy-pytextrank) may be an alternative to what we have, but appears to be less customizable.

Instead of choosing the top 7 sentences, the top X% of sentences could be chosen ([implementation](https://www.presentslide.in/2019/08/text-summarization-python-spacy-library.html)). In Annual Reports and similar reports that cover many topics, a sentence based summary will not be perfect, but can help the reader understand the type of content included. In some cases, the summaries will even be misleading, connecting un-related topics by placing the sentences near each other. Summarization works best when the report is focused on a single case study.

#### How to extract tags

```cypher
// TOP TAGS
MATCH(n:Tag)-[r]-() 
RETURN n.name, count(r) as result 
order by result desc
```

#### How to upload regions, project numbers, and filenames

1. Copy the write ups and reports tab of the Google sheet into a csv, save to `data/`

2. In Neo4j Desktop (within this Project), click Add File and upload the csv

3. Click the 3-dot menu for the file and select copy url

4. In Neo4j Browser, use the following cypher to test the csv

   ```cypher
   LOAD CSV WITH HEADERS FROM "<paste url here>" as row RETURN row
   ```

5. Use the following cypher to load regions and projects

   ```cypher
   LOAD CSV WITH HEADERS FROM "http://localhost:11001/project-5810fc37-0742-4c0b-b0d7-238646cc50ea/reports.csv" as row
   MERGE(p:Project {name: row.Project_Number})
   MERGE(r:Region {name: row.Region})
   RETURN p, r
   ```

6. Create relationships with Projects and Regions

   ```cypher
   LOAD CSV WITH HEADERS FROM "http://localhost:11001/project-5810fc37-0742-4c0b-b0d7-238646cc50ea/reports.csv" as row
   MATCH(p:Project {name: row.Project_Number})
   MATCH(r:Region {name: row.Region})
   MERGE(p)-[:LOCATED_IN]->(r)
   ```

7. Create relationships between Projects and Reports

   ```cypher
   LOAD CSV WITH HEADERS FROM "http://localhost:11001/project-5810fc37-0742-4c0b-b0d7-238646cc50ea/reports.csv" as row
   MATCH(p:Project {name: row.Project_Number})
   MATCH(f:Report {name: row.Filename})
   MERGE(f)-[:ABOUT]->(p)
   ```

#### How to create relationships between projects

creates bi-directional relationships between projects where projects have reports that share tags with a property of the number of shared tags

```cypher
MATCH (p:Project)<-[:ABOUT]-(r:Report)<-[:TAGGED_IN]-(t:Tag)-[:TAGGED_IN]->(r2:Report)-[:ABOUT]->(p2:Project)
WHERE p['name'] <> p2['name']
WITH p, p2, COUNT(*) AS count
CREATE (p)-[r:SHARES_TAGS]->(p2)
SET r.count = count
```

### Graph Data Science

To add the graph data science gallery, open the Graph Apps Gallery from the Open split button and click install under the Graph Data Science Playground. If nothing happens, copy the link that opens when you click the square icon (right-most) and paste into the install file or link bar that comes up when you click the four squares button in the sidebar. You also need to install the APOC library (see Add Plugin card at bottom of Neo4j desktop for the project).

You can then find the Graph Data Science Library in the Open split button. Follow the connection guide to get connected the first time.

#### PageRank

Using the graph data science playground, use PageRank with the following parameters:

* Label: Project
* Relationship Type: SHARES_TAGS
* Relationship Orientation: Natural
* Weight Property: count

Write results to 'pagerank' property

#### Louvain Communities

Using the graph data science playground, use Louvain with the following parameters:

* Label: Project
* Relationship Type: SHARES_TAGS
* Relationship Orientation: Undirected
* Weight Property: count
* Seed property: None
* Intermediate Communities: False
* Community Node Limit: 50

Write results to 'louvain' property

## 2. Initial Buildout

One the tag system is finalized, the new tags will need to be uploaded to the NLP model and all available documents tagged and saved to a graph database

Use the [EntityRuler](https://spacy.io/usage/rule-based-matching#entityruler) (can read files from JSONL) to add tags to the entity recognition model.

### Stories

1. Update NLP model (using `spacy`, this would be accomplished with entity ruler; otherwise training the model would require >200 explicit instances) with custom tags and consolidated entities.

   - `outputs/top_tags_initial_full.csv` holds initial tags and consolidated tags for first 2,500ish tags. Used code DELETE to signify tags that should be deleted.

   - `data/custom_tags.csv` includes tags provided by Sue
2. Build graph database (local)
3. Read in PDFs & txt files and add tag cloud to graph database (automate process from Epic #1 using filenames column as iterator; include entity types)
4. Drop bad tags
5. Read in summaries
   1. Read to csv (how to handle commas?)
   2. Edit for clarity
   3. Add to database
6. Add project database
7. Write initial search terms for Neo4j Bloom (new searches will be added with more user testing in Epic #3)
8. Train Izzie(?) on use of Neo4j Bloom for search of products, exploration, and how to build new Cypher queries (Izzie is taking a class on SQL)

### Custom Tags

Conservation, deforestation, conservation crime, private sector engagement, plastics, ocean plastics, livelihoods, indigenous peoples, energy auction, clean energy, illegal logging, illegal fishing, fisheries, Amazon Vision, gender, women, vulnerable population, wildlife trafficking, climate change, innovation, self-reliance, conservation enterprise, water, farming, NMR, natural resource management, improving governance, governance, urban, Great Power Competition 

These tags were added to `data/custom_tags.csv` and read into a JSONL file with `scripts/create_pattern_file`

### Tag Optimization

After reading in all reports, tags were exported and reviewed. Over 3,000 unique tags were generated.

#### Issues

* Punctuation is not working correctly in the pattern matching with USAID/Haiti (for example). 
* Upside-down question mark is coming up a lot. Maybe just drop all punctuation?
* Spanish words like Cuales and Como are showing up (must not be part of stop words)
* The entity matcher may be slightly stochastic, in that different variations of common names are showing up after loading the EntityRuler (e.g., the Nature Conservancy). Is there a way to overwrite entities if they contain the pattern at all, maybe with some REGEX pattern? How to figure out which entities need this ahead of time?
* Tags that are only used once have a higher likelihood of being unnecessary, however a majority of tags are only used once and there are hundreds of potentially interesting entities included. 
* Try reducing window size and scaling number of keywords to the size of the text
* Some tags include bullet points--those should be handled somehow
* Checking entities against wikidata's knowledge base may be a way to weed out unhelpful tags
* duplication between entities that start with 'the' and those that don't ('the Environmental Defense Fund', 'Environmental Defense Fund')

#### Attempted Solutions

The `scripts/automated_tag_generate.py` was edited to sample 5 reports from `reports/` to test different solutions.

* drop `(`, `)`, `/` before tokenization
* drop all punctuation except periods before tokenizing `re.sub(r'[^\w\s.-], ' ', <text>)`
* reduce keywords to 15 (from 30)
* decrease window size to 4 (from 8)
* decrease coefficient to .65 (from .85)
* delete 'the' before token with regex
* put custom tags after NER in pipeline, but keep aggregates before

Of the above, only dropping select punctuation and decreasing the coefficient seems to really add value.

Once the tagging system was refined, tags were exported and any final aggregation was done. The `create_pattern_file.py` file will append from the exported tags any synonyms provided in a column titled 'alt'. 

Use the keyword `DELETE` to id any tags that are spurious. Filter for DELETE (copy into new csv), add the new csv to the project, match any nodes associated with DELETE keyword, and delete.

## 3. Internal Update and Search

After the initial build out, Izzie will be responsible for (1) responding to search requests and (2) adding new products as they come out. Ultimately, the web interface will be needed to make this available to everyone, but this provides a useful check-in point for ensuring value of the project.

### Stories

1. Set Izzie up to automatically update knowledge graph with new products from GUI (expanded in Epic #2).
2. Develop search terms as needed to respond to requests for information
3. Add Sue's News Digest to the graph each week

## 4. Web Platform

To allow users to explore and upload new documents to the system, an interface for search and automated tagging is needed. If this can't be done on Heroku (see Tech Problems), EI may need to "own" adding files until a solution can be found. Uploading new documents is less important than making search available (some searches may be confidential).

### Stories

1. Host graph on Heroku (GrapheneDB)
2. Replicate Movies Database site subbing in ESSC graph database (simple proof of concept)
3. Add Cypher queries to search to replicate functionality from Bloom
4. Convert Projects Sheet to graph database and link search results to project

#### Tech Problems

- [ ] Can `tika` be used on Heroku? If not, how will PDFs be parsed? It appears that Java can be installed on Heroku using a specific buildpack ([link](https://help.heroku.com/2FSHO0RR/how-can-i-add-java-to-a-non-java-app)).

## 5. Facilitate Discovery

A primary use case of the knowledge graph is discovery by exploration of relationships. If a graph can be hosted on the web for exploration, that may be ideal. Otherwise, we can serve all connected documents and projects, use NLP to discover similar documents, or allow filtering by tags to find connections relevant to the user.

### Stories

1. *Need to figure out tech that can host graphs and whether worth paying or not* (see Linkurious or GraphGists)
2. Display rendered html from spacy to highlight entities upon upload.
3. Show related projects and reports based on entities identified upon upload.

#### Tech Problems

- [x] Host interactive graph on the web (Linkurious, GraphGists)

### Use Case Example

This use case example is for a related project for another client. It is aspirational but illustrates the breadth of need. ("Like wanting a pizza delivery without wanting a restaurant")

![img](file:///C:/Users/Erik/AppData/Local/Temp/msohtmlclip1/01/clip_image001.png)

## Contents

*Note that some of the contents of this repo are copied directly with minor edits from the `ei-knowledge-graph` repo*

**scripts/**

* **add_project_db.py**: reads a copy of the LAC ESSC energy database (as a csv in `data/`), creates nodes for entities, and adds properties to Project nodes.
* **auto_tag_generator.py**: reads reports from `reports/` as .txt or .pdf files, summarizes, tags, and uploads to graph database.
* **create_pattern_file.py**: creates a JSONL file for spacy's entity ruler to add custom tags and consolidate common enities. Uses the `TOP TAGS` query export from neo4j, add column `alt` and specify desired label for any duplicate entities.
* **delete_bad_tags.py**: deletes unwanted tags from graph database. Reads bad tags from `data/inputs/bad_tags.csv`.
* **graph_database.py**: handles all graph database operations.
* **gui_tag_generator.py**: a GUI interface for uploading one or more files and generating tags. Upload all files from a project to get the project's top tags.
* **text_rank.py**: implements a page rank algorithm to extract keywords from text. Defaults to 20 keywords per run. 
*  **text_summary.py**: extracts top 7 sentences from the text as summary.

**reports/**: contains all reports for initial set up of graph database. Must be .pdf or .txt.

**data/**

* **inputs/**
  * **bad_tags.csv**: list of tags to delete
  * **custom_tags.csv**: list of tags to add to entities with spacy's entity ruler. Read to `entity-patterns.jsonl` for import to spacy.
  *  **entity-patterns.jsonl**: newline delimitted json file to add patterns to spacy's entity ruler
  * **projects.csv**: copy of LAC ESSC Energy Database `Sheet 1`
  * **reports.csv**: copy of LAC ESSC Energy Database `reports & writeups` sheet
* **outputs/**: directory to save `TOP TAGS` and other exports from neo4j database

**cypher/cypher.txt**: stores plain text cypher queries for reference

 **assets/**: icon for GUI

## Usage

1. Re-create virtual environment (`conda create --name essc-knowledge-base`) (if spacy fails, you may need to downgrade python `conda install python=3.8`)
2. Download english and spanish models
   1. `python -m spacy download en_core_web_sm`
   2. `python -m spacy download es_core_news_sm`
3. Download 
4. Create a Neo4j database
5. Open database (should be on port 7...), or update 
6. Compile pattern file (run `create_pattern_file.py`)
7. Update location of reports in  auto_tag_generator.py, line 64
   1. `if f in os.listdir('<reports>')`
   2. (`E:/data/essc-knowledge-base/data/reports_eng`)
8. Copy project database from google sheet into `data/projects.csv`
9. Read in project database (run `add_project_db.py`)
10. Delete bad tags (run `delete_bad_tags.py`)
11. upload regions, project numbers, and filenames (see guidance above)
12. create connections between projects (see guidance above)
13. run data science algorithms pagerank and louvain on graph (see guidance above)
14. upload projects database (run `add_project_db.py`)

Note: different machines are parsing the columns with `\n` differently. If you get KeyErrors, it's likely that the column name should be changed from `\n` to `\n\r` or vis versa, print the column names to see.

## Tips & Tricks

[Why use conda-forge?](https://stackoverflow.com/questions/39857289/should-conda-or-conda-forge-be-used-for-python-environments) It's not super clear, but may better ensure compatibility if using conda-forge rather than the default channel, and it has more packages than the default channel. You can add the conda-forge channel to your list of channels as the priority channel so that you don't have to constantly type `-c conda-forge`.

```bash
conda config --add channels conda-forge
```

#### Set up Graph

```python
from py2neo import Graph

PORT = 'bolt://localhost:7687'
PASSWORD = 'incentives'

graph = Graph(PORT, auth=('neo4j', PASSWORD))
```

#### Run as transaction

```python
tx = graph.begin()
# code
tx.commit()
```

Note some commands are transactions, and you shouldn't use both at the same time (e.g., update properties of node with graph.push()). If you have up to 20,000 operations to run you can batch those with one transaction. This is both safe and efficient. Over 20,000 you may run into a memory issue and you'll need to periodically commit as you are running (committing each of significantly more than 20,000 transaction might take a long time).

#### Add nodes

```python
tx = graph.begin()
new_node = Node('<LABEL>', <id_property>=<>,
                primary_key='<id_property>',
                primary_label='<LABEL>')
tx.merge(new_node, '<LABEL', '<id_property>')
tx.commit()
```

You can also use a dictionary to add properties. Any kwargs are read as properties, any args are read as labels. This can be helpful when reading from a pandas dataframe (see Import from DataFrame rows below).

```python
new_node = Node('<LABEL>', <id_property>=<>,
                primary_key='<id_property>',
                primary_label='<LABEL>',
               **property_dict)
```

#### Query Graph

[Cypher Query Cheatsheet](https://gist.github.com/DaniSancas/1d5265fc159a95ff457b940fc5046887)

To get data from the graph

```python
results = graph.run("<CYPHER QUERY>")  # returns cursor to stream results
for result in results:
    # do something
```

Instead of streaming results, data can be read to a list of dictionaries 

```python
results = graph.run(
    f"""
    MATCH(n:Node)-[]-()
    WHERE n.name = "{<name>}"
    RETURN n.name, n.prop_1, n.prop_2
    """
).data()
# returns:
[
    {'n.name': '', 'n.prop_1': '', 'n.prop_2': ''},
    {'n.name': '', 'n.prop_1': '', 'n.prop_2': ''},
    ...
]
```

If your graph has spaces in the properties, use indexing:

```python
results = graph.run(
    f"""
    MATCH(n:Node)-[]-()
    WHERE n.name = "{<name>}"
    RETURN n['my name'], n['my prop_1'], n['my prop_2']
    """
).data()
```

If labels have spaces, use backticks 

```python
results = graph.run(
    f"""
    MATCH(n:`My Node`)-[]-()
    WHERE n.name = "{<name>}"
    RETURN n['my name'], n['my prop_1'], n['my prop_2']
    """
).data()
```

If you need relationships from one central node to multiple other nodes, use OPTIONAL MATCH:

```python
results = graph.run(
	f"""
	MATCH(n:Node)-[]-(o:other_node)
	WHERE n.name="{<name>}"
	OPTIONAL MATCH (o)-[]-(p)
	WHERE p:<Label1> OR p:<Label2>
	RETURN n.name, o.name, labels(p), p.name
	"""
).data()
```

This query gives you nodes with labels Label1 or Label2 related to node with label node that is connected through other_node. Note that in the above example the identifying property for all additional nodes must be the same, namely `name`.

#### Export to DataFrame

Note that nodes may not conform well to pandas expectations, and unexpected errors can occur.

```python
df = pd.DataFrame(graph.data("MATCH (a:Person) RETURN a.name, a.born"))
# returns:
a.born              a.name
0    1964        Keanu Reeves
1    1967    Carrie-Anne Moss
2    1961  Laurence Fishburne
3    1960        Hugo Weaving

# Alternatively
df = graph.run("MATCH (a:Person) RETURN a.name, a.born").to_data_frame()
```

#### Import nodes from DataFrame columns

If lists of nodes of the same type are stored in DataFrame columns, you can create a unique list from each column and create a node using that list with the label as the column header. Labels may contain spaces.

```python
tx = graph.begin()
for column in df.columns:
    node_set = df[column].unique().astype(str)  # some data types not supported as labels
    for node in node_set:
        new_node = Node(column, <id_property>=node,
                       primary_key='<id_property>',
                       primary_label=column)
        tx.merge(new_node, column, '<id_property>')
tx.commit()
```

https://stackoverflow.com/questions/45738180/neo4j-create-nodes-and-relationships-from-pandas-dataframe-with-py2neo

#### Import nodes from DataFrame rows

Alternatively, if the nodes correspond to rows and columns are properties (you should find this with tidy datasets), read the df with the primary label as the index column, convert to a dictionary, and iterate through the dictionary items to add nodes. Note that the index column must be unique.

```python
df = pd.read_csv('path/to/data', index_col='<id_property>')
node_dict = df.to_dict('index')

tx = graph.begin()
for node, properties in node_dict.items():
    node = Node('<LABEL>', <id_property>=node,
                primary_key='<id_property>',
                primary_label='<LABEL>',
                **properties)
     tx.merge(node, '<LABEL>', '<id_property>')
tx.commit()
# needs to be tested
```

Using `**properties` passes the dictionary of properties, where each column is a key and the data in the cell is a value, to the Node object.

#### Match Nodes

```python
[(a["name"], a["born"]) for a in graph.nodes.match("Person").limit(3)]

# returns
[('Laurence Fishburne', 1961),
 ('Hugo Weaving', 1960),
 ('Lilly Wachowski', 1967)]
```

#### Update properties (one property)

This runs as a transaction, so don't wrap in transaction. Note that updates to properties occur only locally until pushed using `graph.push`.

```python
node = matcher.match('<LABEL>', <id_property>=<>).first()
if node:
    node[<property>] = <>
    graph.push(node)
```

#### Update properties (multiple properties)

```python
node = matcher.match('<LABEL>', <id_property>=<>).first()
if node:
    node.update(**properties)
    graph.push(node)
```



#### Add relationships from DataFrame columns

Where nodes are stored in columns, and nodes have already been imported, you can use either `df.iterrows()` or convert the DataFrame to a dictionary to relate all nodes in a single row. 

```python
from py2neo import NodeMatcher
matcher = NodeMatcher(graph)

df = pd.read_csv('path/to/data', index_col='<id_property>')
entity_dict = df.to_dict()

tx = graph.begin()
    for node_label, node_dict in entity_dict.items():
        for project_id in entity_dict[node_label]:
            project_node = matcher.match('Project', 
                                         project_number=project_id).first()
            entity_node = matcher.match(
                node_label, name=node_dict.get(project_id)).first()
            if project_node and entity_node:
                relationship = Relationship(project_node, "IN", entity_node)
                tx.create(relationship)
        
    tx.commit()
```

How this works:

The `entity_dict` looks like:

```python
{
    'Country': {'AID-512-A-00-08-00005': 'Brazil', 
             	'AID-512-A-00-08-00015': 'Brazil', 
             	'AID-512-A-10-00004': 'Brazil', 
             	'AID-512-A-11-00004': 'Brazil', 
             	'AID-512-A-16-00001': 'Brazil'}, 
 	'Income Group': {'AID-512-A-00-08-00005': 'Upper Middle Income Country', 
                  	'AID-512-A-00-08-00015': 'Upper Middle Income Country', 
                  	'AID-512-A-10-00004': 'Upper Middle Income Country', 
                  	'AID-512-A-11-00004': 'Upper Middle Income Country', 
                  	'AID-512-A-16-00001': 'Upper Middle Income Country'}
}
```

Each column has the relationship required between the index (in this case a project number) and the node of the type contained in that column. You can create all of the relationships required and then repeat the process by specifying a new index column, if needed.

For each column (node_label), we use the dictionary associated to match each project id and each node. If a match is found for both, we create a relationship. Don't forget to commit the transaction.

You can use another dictionary to specify the label for the relationship if you want to have different relationship labels for different columns. Simply lookup the relationship name in place of "IN".

#### Delete nodes from list

```python
tx = graph.begin()
for node in bad_node_list:
    node_matches = matcher.match('<LABEL>', <id_property>=node)
    for node in node_matches:
        graph.delete(node)
tx.commit()
```

#### Using objects

```python
from py2neo.ogm import GraphObject, Property
class Person(GraphObject):
	name = Property()
	born = Property()
	
[(a.name, a.born) for a in Person.match(graph).limit(3)]

# returns
[('Laurence Fishburne', 1961),
 ('Hugo Weaving', 1960),
 ('Lilly Wachowski', 1967)]
```

#### Connect to web hosted database on Aura

Create and account and create your database

Store the credentials in a `json` file in your `secrets/` directory

Copy the connection URI from the database card (under Databases)

Use the code below to connect with neo4j

```python
from neo4j import GraphDatabase
import json 

with open('secrets/aura_creds.json') as f:
    creds = json.load(f)

URI = creds.get('URI')
USERNAME = creds.get('USERNAME')
PASSWORD = creds.get('PASSWORD')

graph = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
```

Note that it appears that py2neo does not support the protocol used by Aura. If your app simply queries data from the database with cypher, neo4j is sufficient. If you need more advanced functionality, and don't want to learn neo4j to that extent, check this [stack overflow topic](https://stackoverflow.com/questions/64880029/connect-to-neo4j-aura-cloud-database-with-py2neo) to see if anyone can help.

## Learning Resources

https://github.com/akash-kaul/Using-scispaCy-for-Named-Entity-Recognition

https://towardsdatascience.com/using-scispacy-for-named-entity-recognition-785389e7918d

https://medium.com/towards-artificial-intelligence/text-mining-in-python-steps-and-examples-78b3f8fd913b

https://towardsdatascience.com/named-entity-recognition-with-nltk-and-spacy-8c4a7d88e7da

https://medium.com/analytics-vidhya/automated-keyword-extraction-from-articles-using-nlp-bfd864f41b34 # step by step NLP pipeline for keyword extraction

https://towardsdatascience.com/textrank-for-keyword-extraction-by-python-c0bae21bcec0 # Full implementation of keyword extraction using TextRank algorithm

[rake_nltk](https://pypi.org/project/rake-nltk/) and [multi_rake](https://pypi.org/project/multi-rake/) for rapid automated keyword extraction

https://prodi.gy/features/named-entity-recognition

https://medium.com/neo4j/py2neo-v4-2bedc8afef2

### SQL Alchemy

The benefit of SQL Alchemy is that you can quickly switch from using SQLite to Postgres between local dev and deployment. 

