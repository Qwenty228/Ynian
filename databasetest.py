from corgidb import CorgiDB as cd

# Connect CorgiDB to db.sqlite
cdb = cd(database_path='database/db.sqlite')


# Create a Table
tb = cdb.utils.create_table(
    name="Favorite_songs",
    columns=[("user_id"     , str),
            ("song_url"      , str),
])


# Let's add some data to the table
tb.insert(data={
    "user_id" : "Atinat Pramoj",
    "song_url": 'super mario oddysi'
})

