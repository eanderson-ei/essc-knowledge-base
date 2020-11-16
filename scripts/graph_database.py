"""save from gui to graph database"""
from py2neo import Graph, Node, Relationship, NodeMatcher


# database info
PORT = 'bolt://localhost:7687'
PASSWORD = 'incentives'

# connect to database
graph = Graph(PORT, auth=('neo4j', PASSWORD))

# create matcher
matcher = NodeMatcher(graph)

# add keywords
def update_tags(title, keywords=None):
    # begin transaction
    tx = graph.begin()
    
    # create node for report title
    report = Node('Report', name=title, 
                  primary_key='name', primary_label='Report')
    tx.merge(report, 'Report', 'name')

    if keywords:
        for keyword in keywords:
            # create node for keyword
            tag = Node('Tag', name=keyword, 
                    primary_key='name', primary_label='Tag')
            tx.merge(tag, 'Tag', 'name')


            # create relationships between report title and keyword
            # use value as relationship property 'strength'
            report_tag = Relationship(tag, "TAGGED_IN", report, 
                                    strength=keywords.get(keyword))
            tx.create(report_tag)
        
    tx.commit()


def update_summary(title, summary):
    # match node for report title
    report = matcher.match('Report', name=title).first()
    
    # add summary as property
    if report:
        report['summary'] = summary
    else:
        print(f'{report} not found in database')
        
    # commit (run as single transaction)
    graph.push(report)
           

def import_projects_db(df, node_columns, project_columns):
    """add projects and associate with reports"""
    # add project nodes
    project_dict = df[project_columns].to_dict('index')
    tx = graph.begin()
    
    for project_id, properties in project_dict.items():
        project = Node('Project', project_number=project_id,
                       primary_key='project_number',
                       primary_label='Project',
                       **properties)
        tx.merge(project, 'Project', 'project_number')
    
    tx.commit()    
    
    # add nodes for project db entities
    tx = graph.begin()
        
    for column in df[node_columns]:
        node_set = df[column].dropna().unique().astype(str)
        for node in node_set:
            new_node = Node(column, name=node,
                            primary_key='name',
                            primary_label=column)
            tx.merge(new_node, column, 'name')
    
    tx.commit()
    
    # add relationships to projects
    tx = graph.begin()
    
    entity_dict = df[node_columns].to_dict()
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
       
    # relate keywords to projects
    #TODO: read keywords from keywords column and link one-by-one to projects
    
    
def relate_projects_to_reports(df, report_properties):
    """add relationship between projects and reports
    add links and report titles as properties"""
    
    # update properties
    report_dict = df[report_properties].to_dict('index')
    
    tx = graph.begin()
    for (project_number, report_name), properties in report_dict.items():
        # add properties
        report = matcher.match('Report', name=report_name).first()
        if report:
            report.update(**properties)
            graph.push(report)
        
        # create relationships
        project = matcher.match('Project', project_number=project_number).first()
        
        if project and report:
            relationship = Relationship(report, 'ABOUT', project)
            tx.create(relationship)
    tx.commit()
    
    
def delete_bad_tags(bad_kws):
    """deletes bad tags from list"""
    tx = graph.begin()
    
    for kw in bad_kws:
        tags = matcher.match('Tag', name=kw)
        for tag in tags:
            graph.delete(tag)
    
    tx.commit()
