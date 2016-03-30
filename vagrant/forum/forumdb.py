#
# Database access functions for the web forum.
#

# TODO: You MUST get rid of the bad SQL calls that can easily be hacked and
# create a safer query

import time
import psycopg2
import bleach

## Get posts from database.
def GetAllPosts():
    '''Get all the posts from the database, sorted with the newest first.

    Returns:
      A list of dictionaries, where each dictionary has a 'content' key
      pointing to the post content, and 'time' key pointing to the time
      it was posted.
    '''
    conn = psycopg2.connect("dbname=forum")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT content, time FROM posts ORDER BY time DESC"
    )
    result = cursor.fetchall()
    print bleach.clean(result[0][0]);
    posts = [{'content': str(row[0]), 'time': str(row[1])} for row in result]
    conn.close()
    return posts

## Add a post to the database.
def AddPost(content):
    '''Add a new post to the database.

    Args:
      content: The text content of the new post.
    '''
    conn = psycopg2.connect("dbname=forum")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO posts VALUES (%s)", (bleach.clean(content),)
    )
    conn.commit()
    conn.close()
