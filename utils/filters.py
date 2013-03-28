# Jinja2 filters

from jinja2 import evalcontextfilter, Markup
import re

# hashtag: take a #hashtag and convert it to <a href="[base_url]/hashtag" class="tag">#hashtag</a>
@evalcontextfilter
def hashtag(eval_ctx, value, index, slug, base_url):
    result = convert_hashtags(value, index, slug, base_url)

    if eval_ctx.autoescape:
        result = Markup(result)

    return result

def convert_hashtags(value, index, slug, base_url):
    url = '%s%s%s' % (index, slug, base_url)

    return re.sub(r"#(\w+)", r'<a href="%s/\1" class="tag">#\1</a>' % url, value)
