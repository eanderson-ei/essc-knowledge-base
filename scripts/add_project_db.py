import pandas as pd
from graph_database import import_projects_db, relate_projects_to_reports

# get columns that contain nodes
node_columns = [
        'Country',
        'Income Group',
        'Subagency',
        'Category',
        'Subcategory',
        'Implementing Partner',
        'Sector',
        'Subsector',
        'Fiscal Year',
        'Aid Type',
        'USG Sector',
        'Regional Info',
        'Country Info',
        'J2SR Roadmap',
        'CDCS'
    ]

# get columns that contain project properties
project_columns = [
    'Project Name',
    'Project Name - Local Language\r\n(if applicable)',
    'Start Date',
    'End Date',
    'Transaction Type',
    'Current Amount',
    'Constant Amount',
    'Reported Results',
    'Description'
]

df = pd.read_csv('data/inputs/projects.csv', index_col='Project Number')

import_projects_db(df, node_columns, project_columns)

# this section is hanging on a Guatemala report, see alt cypher
# procedure in README

report_properties = [
        'Report_Title',
        'Link'
    ]

dff = pd.read_csv('data/inputs/reports.csv', index_col=['Project_Number', 'Filename'])
dff = dff.loc[dff.index.dropna()]  # drop na filenames to avoid duplicate multi-index

# dff.to_csv('data/outputs/multiindexreports.csv')

relate_projects_to_reports(dff, report_properties)
