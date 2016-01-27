import rethinkdb as r
from tornado import gen
from tornado import ioloop
import random

r.set_loop_type("tornado")
connection = r.connect(db='pilot', host='localhost', port=28015)

@gen.engine
def init():
    conn = yield connection
    print "Connecting"
    try:
        print "Creating DB"
        yield r.db_create("pilot").run(conn)
    except:
        print "database already exists"

    try:
        print "Creating tables"
        conn.use('pilot')
        yield r.table_create('deauth').run(conn)
        yield r.table_create('instagram').run(conn)
        yield r.table_create('tumblr').run(conn)
        yield r.table_create('reddit').run(conn)
        yield r.table_create('twitter').run(conn)
        yield r.table_create('spotify').run(conn)
        yield r.table_create('facebook').run(conn)
        yield r.table_create('users').run(conn)
        yield r.table_create('google').run(conn)
    except:
        print "tables already exist"
ioloop.IOLoop().instance().add_callback(init)

@gen.coroutine
def user_insert(data):
    conn = yield connection
    result = yield r.table('users').insert(
            data,
            conflict = "update",
            ).run(conn)
    raise gen.Return(result)

@gen.coroutine
def get_user(id):
    conn = yield connection
    result = yield r.table('users').get(id).run(conn)
    raise gen.Return(result)

@gen.coroutine
def get_user_from_email(email):
    conn = yield connection
    result = yield r.table('users').filter({"email":email}).run(conn)
    if(len(result.items)>0):
        raise gen.Return(result.items[0])
    else:
        raise gen.Return(None)

@gen.coroutine
def save_token(provider, user_id, token_data):
    conn = yield connection
    data = {"user_id": user_id, "token": token_data}
    result = yield r.table(provider).insert(
            data,
            conflict='update').run(conn)
    raise gen.Return(result)

@gen.coroutine
def google_user(data):
    conn = yield connection
    #start grabbing user ID
    result = yield r.table('google').insert(
            data,
            conflict='update',
            ).run(conn)
    raise gen.Return(result)

@gen.coroutine
def deny(provider, share, user_id):
    conn = yield connection
    result = yield r.table(provider).insert(
            {"id": user_id, "missing_reason": share},
            conflict='update',
            ).run(conn)
    raise gen.Return(result)

@gen.coroutine
def pop_deauth_request(id):
    conn = yield connection
    result = yield r.table('deauth').get(id).run(conn)
    # now remove it
    deleteResult = yield r.table('deauth').get(id).delete().run(conn)
    raise gen.Return(result)

@gen.coroutine
def create_deauth_request(id, user_id):
    conn = yield connection
    result = yield r.table('deauth').insert(
    {"id": id, "user_id": user_id},
    conflict='update'
    ).run(conn)
    raise gen.Return(result)

@gen.coroutine
def delete_user_data(id):
    conn = yield connection
    tables = ['google','facebook','spotify','reddit','tumblr','instagram','twitter']
    lastResult = None
    for table in tables:
        print table
        lastResult = yield r.table(table).filter({'user_id':id}).delete().run(conn)
        print lastResult
    lastResult = yield r.table('users').get(id).delete().run(conn)
    raise gen.Return(lastResult)