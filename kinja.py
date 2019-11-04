from bs4 import BeautifulSoup
import urllib.request
import re
import os
import time
#import psycopg2

img_format = "https://i.kinja-img.com/gawker-media/image/upload/{}.{}"

embed_providers = {
    'instagram': "https://www.instagram.com/p/{}/",
    'twitter': 'https://twitter.com/statuses/{}',
    'youtube': "https://www.youtube.com/watch?v={}",
    'vimeo': "https://vimeo.com/{}"
}

## For videos, we're looking for something that looks like:
## <div class="align--bleed has-video media-large video-embed embed-frame ooo3c9-0 ekkpks">
##   <span class="flex-video widescreen">
##      <iframe ... data-recommend-id="youtube://1OADXNGnJok>

def embed_to_url(provider, media_id):
    if provider in embed_providers:
        return embed_providers[provider].format(media_id)
    return None

def extract_author_nodes(div):
    return filter(lambda child: child.name == 'p' or child.name == 'figure' \
                  or child.name == 'aside' \
                  or child.name == 'ul' \
                  or child.name == 'section' \
                  or child.name == 'blockquote' \
                  or child.name.startswith('h') \
                  or (child.name == 'div' and 'embed-frame' in child.attrs['class']) \
                  or (child.name == 'div' and 'video-embed' in child.attrs['class']),
                  div.children)

def video_embed_to_url(video_str):
    ## vimeo://119907540 or youtube://1OADXNGnJok
    import re
    m = re.match('(\w+)://(.+)', video_str)

    if m:
        new_url = embed_to_url(m.group(1), m.group(2))
        if new_url:
            return new_url
    return video_str

def other_embed_to_url(embed_str):
    ## instagram-xxxxx
    import re
    m = re.match('(\w+)-(.+)', embed_str)

    if m:
        new_url = embed_to_url(m.group(1), m.group(2))
        if new_url:
            return new_url
    return embed_str

def p_html(node):
    return str(node)

def p_text(node):
    return node.text

def header_html(node):
    return str(node)

def header_text(node):
    return 'Header: {}'.format(node.text)

def ul_html(node):
    return str(node)

def ul_text(node):
    items = node.findAll('li')
    return '\n'.join(map(lambda i: i.text, items))

def blockquote_html(node):
    return str(node)

def blockquote_text(node):
    (html, text) = doc_author_content(node, 'ignoreme', False)
    return 'Quote: {}'.format(text)

def section_html(node):
    return str(node)

def section_text(node):
    return 'Attribution: {}'.format(node.find('h4').text)

def aside_html(node):
    a_tag = node.find('a')
    if not a_tag:
        return '<p>Aside: {}</p>'.format(node.text)
    else:
        url = a_tag.attrs['href']
        return f'<a href="{url}">{url}</a>'

def aside_text(node):
    a_tag = node.find('a')
    if not a_tag:
        return 'Aside: {}'.format(node.text)
    else:
        url = a_tag.attrs['href']
        return f'URL: {url}'

def figcaption_html(node):
    return '<figcaption>{}</figcaption>'.format(node.text)

def figure_img_id(node):
    return node.attrs['data-id']

def figure_img_format(node):
    return node.attrs['data-format'].lower()

def video_div_to_video_str(node):
    iframe = node.find('iframe')
    return iframe.attrs['data-recommend-id']

def embed_div_to_embed_str(node):
    iframe = node.find('iframe')
    return iframe.attrs['id']

def img_url(data_id, extension):
    return img_format.format(data_id, extension)

def youtube_url(data_id):
    return youtube_format.format(data_id)

def div_text(node):
    if 'video-embed' in node.attrs['class']:
        url = video_embed_to_url(video_div_to_video_str(node))
        return f'Video: {url}\n'
    if 'embed-frame' in node.attrs['class']:
        url = other_embed_to_url(embed_div_to_embed_str(node))
        return f'Embed: {url}\n'
    return 'Unknown embed'

def div_html(node):
    if 'video-embed' in node.attrs['class']:
        url = video_embed_to_url(video_div_to_video_str(node))
    elif 'embed-frame' in node.attrs['class']:
        url = other_embed_to_url(embed_div_to_embed_str(node))

    return f'<p><a href="{url}">{url}</a></p>'

def figure_html(node):
    captions = node.findAll('figcaption')
    captions_html = ''.join(list(map(figcaption_html, captions)))
    return '''<figure><img src='{}' />{}</figure>'''.format(
    img_url(figure_img_id(node), figure_img_format(node)),
    captions_html)

def figure_text(node):
    captions = node.findAll('figcaption')
    captions_text = '\n'.join(list(map(lambda c: c.text, captions)))
    return '''
Image: {}
{}
'''.format(img_url(figure_img_id(node), figure_img_format(node)), captions_text)

def retrieve_image(node, directory):
    image_name = figure_img_id(node)
    image_extension = figure_img_format(node)
    url = img_url(image_name, image_extension)
    img = urllib.request.urlopen(url).read()
    ## XXX: Fix this with Python's OS path wrapper logic
    local_file = '{}/{}.{}'.format(directory, image_name,
                                   image_extension)
    with open(local_file, 'wb') as imagefh:
        imagefh.write(img)

def node_author_content(node, directory,
                        output_format, retrieve_images=False):
    if retrieve_images and node.name == 'figure':
        retrieve_image(node, directory)
    ## Special case all of the possible headers
    if node.name.startswith('h'):
        return eval('header_{}(node)'.format(output_format))

    return eval('{}_{}(node)'.format(node.name, output_format))

## div.js_expandable-container
def doc_author_content(content, directory,
                       retrieve_images=False):
    html = ''
    text = ''
    for child in extract_author_nodes(content):
        html = html + node_author_content(child, directory, 'html', retrieve_images)
        text = text + node_author_content(child, directory, 'text', False) + '\n'
    return (html, text)

def year_month(timestr):
    ## 2018-07-23T08:50:00-04:00
    import re
    m = re.match('(\d{4})-(\d{2})', timestr)

    if m:
        return (m.group(1), m.group(2))
    return 'unknown-unknown'

## For testing
def one_off(url):
    page = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(page, "html.parser")
    content = soup.find('div', {'class': 'js_expandable-container'})
    return doc_author_content(content, 'irrelevant', False)

def main(url, nextOne, grab_images):
    keepGoing = True
    while keepGoing:
        print(nextOne)
        keepGoing = False
        page = urllib.request.urlopen(url + nextOne).read()
        soup = BeautifulSoup(page, "html.parser")
        pageLinks = []
        for link in soup.findAll("a", {"class": "js_link sc-1out364-0 fwjlmD"}):
            if link.find("h1"):
                l = link.get("href")
                if l not in pageLinks:
                    pageLinks.append(l)
        for link in soup.findAll("a"):
            if link.get("href") and link.get("href").startswith("?startIndex=") == True and link.get("href") != nextOne:
                nextOne = link.get("href")
                keepGoing = True
        for a in pageLinks:
            try:
                articlePage = urllib.request.urlopen(a).read()
                print('Fetched: {}'.format(a))
                time.sleep(1)
            except urllib.error.HTTPError as e:
                print("Error fetching article: " + a)
                print(e)
            else:
                pageSoup = BeautifulSoup(articlePage, "html.parser")
                isotime = pageSoup.find('time').attrs['datetime']
                (year, month) = year_month(isotime)
                filepath = year + "/" + month + "/"
                preTitle = pageSoup.title.text
                realTitle = preTitle
                if pageSoup.p is not None:
                    if preTitle == "Jezebel":
                        preTitle = pageSoup.p.text
                        if preTitle is None:
                            preTitle = "No_title_available"
                if len(preTitle) > 50:
                    preTitle = preTitle[:50]
                preTitle = preTitle.replace(" ", "_")
                postTitle = "".join([c for c in preTitle if re.match(r"\w", c)])
                fullTitle = filepath + postTitle

                notitle = 1
                while os.path.exists(fullTitle):
                    fullTitle = fullTitle + str(notitle)
                    notitle += 1

                try:
                    os.makedirs(fullTitle)
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise

                try:
                    content = pageSoup.find('div', {'class': 'js_expandable-container'})
                    (html, text) = doc_author_content(content, fullTitle, grab_images)
                except:
                    print('Sorry, problems parsing {}, skipping'.format(a))
                    continue

                with open('{}/{}.txt'.format(fullTitle, 'contents'), 'w') as f:
                    f.write("HEADLINE: " + realTitle + "\n")
                    f.write("Published: " + isotime + "\n")
                    f.write("Original URL : " + a + "\n\n")
                    f.write(text + "\n")

                with open('{}/{}.html'.format(fullTitle, 'contents'), 'w') as f:
                    f.write('<html><head><title>{}</title></head><body><h1>{}</h1>'.format(realTitle, realTitle))
                    f.write('<p>Published: {} at <a href="{}">{}</a></p>\n'.format(isotime, a, a))
                    f.write(html)
                    f.write('</body></html>\n')

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Retrieve Kinja content')
    parser.add_argument('username',
                        help='The username for the author')
    parser.add_argument('--continue', dest='next',
                        help='Pick up where a previous ran left off by passing the "?startIndex=" value last seen',
                        default="")
    parser.add_argument('--images', action='store_true',
                        help='Beta: grab your images alongside your document')

    args = parser.parse_args()
    main('https://kinja.com/{}'.format(args.username), args.next, args.images)
