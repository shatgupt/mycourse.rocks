from htmlparsing import Text, Attr
from toapi import Api, Item
from http.cookiejar import CookieJar
from toapi.log import logger
from colorama import Fore
import urllib.request
import cchardet


# This class overrides fetch of toapi to avoid Cloudflare connection
# aborted errors with simple requests.get(url) to ASU webapp
class AsuApi(Api):
    def __init__(self, site: str = "", browser: str = None) -> None:
        super().__init__(site, browser)

    def fetch(self, url: str) -> str:
        html = self._storage.get(url)
        if html is not None:
            return html
        if self.browser is not None:
            html = self.browser.get(url)
        else:
            req = urllib.request.Request(
                url,
                None,
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Charset": "utf-8;q=0.7,*;q=0.3",
                    "Accept-Language": "en-US,en;q=0.8",
                    "Connection": "keep-alive",
                },
            )
            cj = CookieJar()
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
            response = opener.open(req)
            content = response.read()
            charset = cchardet.detect(content)
            html = content.decode(charset["encoding"] or "utf-8")
        logger.info(Fore.GREEN, "Sent", f"{url} {len(html)}")
        self._storage[url] = html
        logger.info(Fore.BLUE, "Storage", f"Set<{url}>")
        return html


api = AsuApi()
app = api.app


# https://webapp4.asu.edu/catalog/coursedetails?r=83239
@api.site("https://webapp4.asu.edu")
@api.route(
    "/class/{c}",
    "/catalog/coursedetails?r={c}",
)
class Class(Item):
    department = Text("h2")
    course = department
    title = department
    # school = Text(".row > .col-md-7 > span > a")
    # instructor = Attr(".nametip", "title")
    _tmp_course = None

    def clean_department(self, value):
        if not self._tmp_course:
            self._tmp_course = value.split()
            print(f"self._tmp_course = {self._tmp_course}")
        return self._tmp_course[0]
    
    def clean_course(self, value):
        if not self._tmp_course:
            self._tmp_course = value.split()
        return self._tmp_course[1]
    
    def clean_title(self, value):
        if not self._tmp_course:
            self._tmp_course = value.split()
        return ' '.join(self._tmp_course[3:])

    # def clean_school(self, value):
    #     return value.strip()
    
    # def clean_instructor(self, value):
    #     return value.split('|')[1]


# https://webapp4.asu.edu/catalog/coursedetails?r=83239
@api.site("https://webapp4.asu.edu")
@api.route(
    "/classseats/{c}",
    "/catalog/coursedetails?r={c}",
)
class ClassSeats(Item):
    total_seats = Text("#details-side-panel > span")
    open_seats = total_seats
    _tmp_seats = None

    def clean_total_seats(self, value):
        if not self._tmp_seats:
            self._tmp_seats = value.split()
        return int(self._tmp_seats[4])

    def clean_open_seats(self, value):
        if not self._tmp_seats:
            self._tmp_seats = value.split()
        return int(self._tmp_seats[2])


# https://webapp4.asu.edu/catalog/myclasslistresults?t=2187&s=CSE&n=355&hon=F&promod=F&e=open&page=1
@api.site("https://webapp4.asu.edu")
@api.list("#CatalogList > tbody > tr")
@api.route(
    "/courseseats/{d}/{c}",
    "/catalog/myclasslistresults?t=2187&s={d}&n={c}&hon=F&promod=F&e=open&page=1",
)
class CourseSeats(Item):
    class_num = Text(".classNbrColumnValue > .course-details-link")
    total_seats = Text(".availableSeatsColumnValue")
    open_seats = total_seats
    _tmp_seats = None

    def clean_class_num(self, value):
        return value.strip()

    def clean_total_seats(self, value):
        if not self._tmp_seats:
            self._tmp_seats = value.split()
        return int(self._tmp_seats[2])

    def clean_open_seats(self, value):
        if not self._tmp_seats:
            self._tmp_seats = value.split()
        return int(self._tmp_seats[0])


if __name__ == '__main__':
    api.run(debug=True, host="0.0.0.0", port=5000)
