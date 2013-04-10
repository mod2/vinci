database_file = 'data/database.db'
log_file = 'data/log.log'
index_dir = 'data/index.idx'
openid_store = 'data/openid_store'
debug = True
secret_key = 'Some random string of characters. KEEP IT SECRET.'
results_per_page = 10
default_sort_order = 'date_desc' # date_asc, date_desc
default_search_order = 'relevance' # relevance, date_asc, date_desc

# main admin user
admin = {
    'username': 'example@example.com',
    'display': 'test_admin'
}

notebook_access = {
    #'test': ['user email 1', 'user email 2'],
}

default_plugins = [ 'youtube', 'hashtags', 'md', 'sp' ]

plugins = {
    'checklist': {
        'css': ['checklist.css']
    },
    'grid': {
        'css': ['grid.css']
    },
    'pedigree': {
        'js': ['pedigree.js'],
        'css': ['pedigree.css']
    },
    'chess': {
        'css': ['chess.css']
    },
    'poetry': {
        'css': ['poetry.css']
    },
}
