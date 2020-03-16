import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

from .names import get_full_name
import random
from datetime import datetime

from functools import wraps
from time import time

def timeit(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    str_args    = ', '.join(str(arg) for arg in args)
    str_kwargs  = ', '.join(f"{k}={v}" for k,v in kwargs.items())
    args_kwargs = f"{str_args}, {str_kwargs}" if args and kwargs else f"{str_args}{str_kwargs}"
    
    print(f'{f.__name__}({args_kwargs}) called')
    ts = time()
    result = f(*args, **kwargs)
    te = time()
    print(f'{f.__name__} took: {te-ts:.4f} sec')
    return result
  return wrap


def random_date(first_date, second_date):
    first_timestamp = int(first_date.timestamp())
    second_timestamp = int(second_date.timestamp())
    random_timestamp = random.randint(first_timestamp, second_timestamp)
    return datetime.fromtimestamp(random_timestamp).date()

@anvil.server.callable
def add_rows(n=1000):
  for i in range(n):
    gender = random.choice(['male', 'female'])
    
    row = {
    'gender' : gender,
    'name' : get_full_name(gender),
    'progress' : random.randint(0,100),
    'rating' : random.randint(0,5),
    'col' : random.choice('blue green yellow red'.split()),
    'driver' : random.choice([True, False]),
    'dob' : random_date(datetime(1950, 1, 1), datetime.now())
    }
    app_tables.data.add_row(**row)
  
@anvil.server.callable
@timeit
def get_rows():
  rows = []
  for row in app_tables.data.search()[:20]:
    row_dict = dict(row)
    row_dict['id'] = row.get_id()
    row_dict['dob'] = row['dob'].strftime("%d/%m/%Y")
    rows.append(row_dict)
  
  return rows

@anvil.server.callable
def get_table_search():
  return app_tables.data.search()



"""
[
    {'name':"Oli baba", 'progress':12, 'gender':"male", 'rating':1, 'col':"red" },
    {'id':2, 'name':"Mary May", 'progress':1, 'gender':"female", 'rating':2, 'col':"blue" },
    {'id':3, 'name':"Christine Lobowski", 'progress':42, 'gender':"female", 'rating':0, 'col':"green" },
    {'id':4, 'name':"Brendon Philips", 'progress':100, 'gender':"male", 'rating':1, 'col':"orange" },
    {'id':5, 'name':"Margret Marmajuke", 'progress':16, 'gender':"female", 'rating':5, 'col':"yellow"},
    {'id':6, 'name':"Oli B", 'progress':12, 'gender':"male", 'rating':1, 'col':"red" },
    {'id':7, 'name':" May", 'progress':1, 'gender':"female", 'rating':2, 'col':"blue" },
    {'id':8, 'name':" Lobowski", 'progress':42, 'gender':"female", 'rating':0, 'col':"green" },
    {'id':9, 'name':"N", 'progress':100, 'gender':"male", 'rating':1, 'col':"orange" },
    {'id':10, 'name':"Marmajuke", 'progress':16, 'gender':"female", 'rating':5, 'col':"yellow"},
]"""