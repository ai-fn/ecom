import datetime
import os
from django.conf import settings
from django.utils import timezone
from django.utils.http import http_date
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from xml.etree import ElementTree as ET

from account.models import CityGroup


class SitemapService:

    @classmethod
    def _get_latest_lastmod(cls, current_lastmod, new_lastmod):
        """
        Returns the latest `lastmod` where `lastmod` can be either a date or a
        datetime.
        """
        if not isinstance(new_lastmod, datetime.datetime):
            new_lastmod = datetime.datetime.combine(new_lastmod, datetime.time.min)
        if timezone.is_naive(new_lastmod):
            new_lastmod = timezone.make_aware(new_lastmod, datetime.timezone.utc)
        return (
            new_lastmod
            if current_lastmod is None
            else max(current_lastmod, new_lastmod)
        )

    @classmethod
    def collect(cls, city_name: str, domain: str, sitemaps: dict, save_to_file: bool = False):

        maps = sitemaps.values()

        lastmod = None
        all_sites_lastmod = True
        urls = []
        for site in maps:
            if callable(site):
                site = site(domain=domain)

            urls.extend(site.get_urls(page=1, site=None, protocol="https"))
            if all_sites_lastmod:
                site_lastmod = getattr(site, "latest_lastmod", None)
                if site_lastmod is not None:
                    lastmod = cls._get_latest_lastmod(lastmod, site_lastmod)
                else:
                    all_sites_lastmod = False
        if all_sites_lastmod:
            headers = (
                {"Last-Modified": http_date(lastmod.timestamp())} if lastmod else None
            )
        else:
            headers = None

        xml = cls._generate_xml(urls)
        if save_to_file:
            return cls._save_as_xml_file(xml, city_name)

        return {
            "xml": xml,
            "headers": headers,
            "content_type": "application/xml",
        }
    
    @classmethod
    def get_xml_file_path(cls, cg_name: str) -> str:
        return os.path.join(settings.SITEMAP_DIR, cg_name, "sitemap.xml")

    @classmethod
    def _save_as_xml_file(cls, content: str, domain: str):
        path = cls.get_xml_file_path(domain)

        default_storage.save(path, content=ContentFile(content.encode('utf-8')))

    @classmethod
    def _generate_xml(cls, urls: list):
        sitemap = ET.Element(
            "urlset",
            {
                "xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9",
                "xmlns:xhtml": "http://www.w3.org/1999/xhtml",
            },
        )
        for url in urls:
            url_el = ET.SubElement(sitemap, "url")
            loc = ET.SubElement(url_el, "loc")
            loc.text = url.get("location")
            if val := url.get("lastmod"):
                el = ET.SubElement(url_el, "lastmod")
                el.text = val.strftime("%Y-%m-%d")

            if val := url.get("changefreq"):
                el = ET.SubElement(url_el, "changefreq")
                el.text = val

            if val := url.get("priority"):
                el = ET.SubElement(url_el, "priority")
                el.text = url["priority"]

            for alternate in url.get("alternates", []):
                ET.SubElement(
                    url_el,
                    "{http://www.w3.org/1999/xhtml}link",
                    rel="alternate",
                    hreflang=alternate.hreflang,
                    location=alternate.location,
                )

        return ET.tostring(sitemap, encoding="utf-8", xml_declaration=True).decode(
            "utf-8"
        )
