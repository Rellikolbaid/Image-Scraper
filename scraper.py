import urllib
import urllib2
import urlparse
import random
import errno
import os
from bs4 import BeautifulSoup


# Stops program from auto executing the main() function,
# allowing the developer to run specific functions for testing.
dev_mode = False

# List of top level domains for validating urls in some functions.
TLD = [tld.strip() for tld in open('TLD.txt', 'r')]


class Images:
    """Contains methods for dealing with scraped images.
    """
    def __init__(self):
        # Directory for storing downloading images
        self.image_dir = os.path.join(os.path.dirname(__file__), 'images')
    
    def get_image_links(self, html, url):
        """Returns list of image URLs
        Parses string containing html and returns list
        of image URLs on that page
        """
        global TLD
        links = []
        # Used to check if the url has a domain name in it.
        hasTLD = False
        soup = BeautifulSoup(html)
        tags = soup.findAll('img')
        for tag in tags:
            src = tag.get('src')
            # Checks to make sure the url contains 'http://' and hostname.
            src = fix_src(url, src)
            # Avoid duplicates and blanks.
            if src in links:
                continue
            if src == '':
                continue
            links.append(src)
        return set(links)

    def download_image(self, url):
        """Downloads image from URL and places it in directory
        with the same hostname 
        """
        hostname = urlparse.urlparse(url).hostname.split('.')[-2]
        # Gets the name for directory, ex: www.google.com becomes 'google'.
        try:
            os.mkdir(os.path.join(self.image_dir, '%s' %hostname))
        # Avoid raising WindowsError but still raise other exceptions.
        except OSError, exc:
            if exc.errno != errno.EEXIST:
                raise
            
        filename = url.split('/')[-1]
        directory = os.path.join(self.image_dir, hostname)
        
        try:
            # If image directory doesn't exist, create it.
            if not os.path.exists(self.image_dir):
                os.makedir(self.image_dir)

            # If image doesn't already exist, download it with original filename.
            if not os.path.exists(os.path.join(directory, filename)):
                urllib.urlretrieve(url, os.path.join(directory, filename))
                print 'DOWNLOADING: %s' % url
            # If there's a duplicate, change filename to allow download.
            elif os.path.exists(os.path.join(directory, filename)):
                i = str(random.randint(1, 10000))
                urllib.urlretrieve(url, os.path.join(directory, i + filename))
                print 'DOWNLOADING: %s' % url
        except IOError:
            if dev_mode:
                print '\n Exception raised in download_image function'
                print 'url:', url, '\n'
            else:
                pass

    def get_image_dir(self):
        return self.image_dir
        

class Links:
    def get_links(self, html, url):
        """Returns list of link URLs
        Parses string containing HTML of a webpage that
        returns list of links to other pages 
        """
        soup = BeautifulSoup(html)
        tags = soup.find_all('a')
        links = []
        for tag in tags:
            href = tag.get('href')
            if href == None:
                continue
            elif 'http' not in href:
                href = url + href
            links.append(href)
        return set(links)


def fix_src(url, src):
    """Returns full url as a string.
    Solves problems caused by relative paths.
    Assumes strings for both inputs, url must
    include http:// and Top Level Domain.
    """
    fixed_url = ''
    hasTLD = False
    if 'http' not in src:
        for domain in TLD:
            if (domain + '/') in src:
                hasTLD = True
        if hasTLD == False:
            fixed_url = url + src    
        else:
            fixed_url = 'http://' + src.lstrip('/')
        return fixed_url
    return src

def html_to_string(url):
    """Returns a string of HTML
    Opens URL, places HTML into a string variable and
    returns variable with all of the HTML
    """
    try:
        return urllib2.urlopen(url).read()
    except:
        return 'Error parsing url'


def main():
    """Runs all of the functions in a loop to create a
    continunally running program. Recieves user input
    through the console about what to scrape.
    """
    while True:
        url = raw_input("Enter full URL of page to parse: ")
        if url == '':
            print 'Invalid URL.'
            continue
        try:
            # Make sure http:// is in the users URL
            if 'http://' not in url:
                url = 'http://' + url
            # Check list of top level domains, if none are in the url,
            # raise exception to print the error
            hasTLD = False
            for domain in TLD:
                if domain in url:
                    hasTLD = True
            if not hasTLD:
                raise NameError
            
            html = html_to_string(url)
        except:
            print 'Invalid URL.'
            continue

        print "Which URLs do you want from the page?"
        print "Enter either 'links',  'images' or 'all': " 
        userInput = raw_input()
        userInput = userInput.lower()
        # Ask user what they want from the page entered
        if userInput == 'links':
            print '\n ### LINKS ### \n'
            linkURLs = links.get_links(html, url)
            for link in linkURLs:
                print link
    
        elif userInput == 'images':
            # List of image URLs from entered page
            imageLinks = images.get_image_links(html, url)
            print "Do you want to download the files or have a list returned?"
            print "Enter 'download' or 'list'"
            userInput = raw_input()
            if userInput == 'download':
                print '\n ### DOWNLOADING IMAGES ### \n'
                for link in imageLinks:
                    images.download_image(link)
                print '\n ### DOWNLOADING COMPLETE ### \n'
            elif userInput == 'list':
                print '\n ### IMAGES ### \n'
                for link in imageLinks:
                    print link
            else:
                print 'Invalid choice'
        else:
            print 'Invalid choice.'
            continue
    

if __name__ == "__main__":
    images = Images()
    links = Links()
    if dev_mode:
        print 'DEV MODE SCRAPER OPTIONS:'
        devInput = raw_input('Run main loop? Y/N: ')
        if devInput == 'Y' or 'y':
            main()
        else:
            pass
    if not dev_mode:
        main()
