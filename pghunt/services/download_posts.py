import os, csv
from pghunt import celery, app
from pghunt.models import Post


@celery.task
def get_data(user_id, file_fn):
    filepath = os.path.join(app.root_path, 'static/pg_data', file_fn)
    posts = Post.query.filter_by(user_id=user_id)
    posts_list = []
    for post in posts:
        curr_post = []
        curr_post.append(post.title)
        curr_post.append(str(post.created_at))
        curr_post.append(post.price)
        curr_post.append(post.contact)
        curr_post.append(post.address)
        curr_post.append(post.pg_pic)
        posts_list.append(curr_post)

    columns = ['Title', 'Date', 'Price', 'Contact', 'Address', 'Picture']
    with open(filepath, 'w') as pg_list:
        write = csv.writer(pg_list)
        write.writerow(columns)
        write.writerows(posts_list)
    return posts_list