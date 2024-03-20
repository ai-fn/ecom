from django.contrib.syndication.views import Feed
from django.core import serializers
from django.http import HttpResponse
from django.http import Http404, HttpResponse
from shop.models import Category, Product
from rest_framework.views import APIView
from django.template import TemplateDoesNotExist, loader
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils.timezone import get_default_timezone, is_naive, make_aware
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import get_language
from django.utils.encoding import iri_to_uri
from django.utils.http import http_date
from django.conf import settings


def add_domain(domain, url, secure=False):
    protocol = "https"  # if secure else "http"

    if url.startswith("//"):
        # Support network-path reference (see #16753) - RSS requires a protocol
        url = f"{protocol}:{url}"
    elif not url.startswith(("http://", "https://", "mailto:")):
        url = iri_to_uri(f"{protocol}://{domain}{url}")
    return url

class CustomFeed:

    def __call__(self, request, *args, **kwargs) -> None:
        self.domain = request.GET.get('domain')
        
        self.base_domain = getattr(settings, "BASE_DOMAIN", "krov.market")
        try:
            obj = self.get_object(request, *args, **kwargs)
        except ObjectDoesNotExist:
            raise Http404("Feed object does not exist.")
        feedgen = self.get_feed(obj, request)
        response = HttpResponse(content_type="application/xml")
        if hasattr(self, "item_pubdate") or hasattr(self, "item_updateddate"):
            # if item_pubdate or item_updateddate is defined for the feed, set
            # header so as ConditionalGetMiddleware is able to send 304 NOT MODIFIED
            response.headers["Last-Modified"] = http_date(
                feedgen.latest_post_date().timestamp()
            )
        feedgen.write(response, "utf-8")
        return response
        
    def _get_domain(self):
        return f"{self.domain}.{self.base_domain}" if self.domain else self.base_domain

    def get_feed(self, obj, request):
        """
        Return a feedgenerator.DefaultFeed object, fully populated, for
        this feed. Raise FeedDoesNotExist for invalid parameters.
        """
        current_site = get_current_site(request)

        domain = self._get_domain()
        link = self._get_dynamic_attr("link", obj)
        link = add_domain(domain, link, request.is_secure())

        feed = self.feed_type(
            title=self._get_dynamic_attr("title", obj),
            subtitle=self._get_dynamic_attr("subtitle", obj),
            link=link,
            description=self._get_dynamic_attr("description", obj),
            language=self.language or get_language(),
            feed_url=add_domain(
                domain,
                self._get_dynamic_attr("feed_url", obj) or request.path,
                request.is_secure(),
            ),
            author_name=self._get_dynamic_attr("author_name", obj),
            author_link=self._get_dynamic_attr("author_link", obj),
            author_email=self._get_dynamic_attr("author_email", obj),
            categories=self._get_dynamic_attr("categories", obj),
            feed_copyright=self._get_dynamic_attr("feed_copyright", obj),
            feed_guid=self._get_dynamic_attr("feed_guid", obj),
            ttl=self._get_dynamic_attr("ttl", obj),
            **self.feed_extra_kwargs(obj),
        )

        title_tmp = None
        if self.title_template is not None:
            try:
                title_tmp = loader.get_template(self.title_template)
            except TemplateDoesNotExist:
                pass

        description_tmp = None
        if self.description_template is not None:
            try:
                description_tmp = loader.get_template(self.description_template)
            except TemplateDoesNotExist:
                pass

        for item in self._get_dynamic_attr("items", obj):
            context = self.get_context_data(
                item=item, site=current_site, obj=obj, request=request
            )
            if title_tmp is not None:
                title = title_tmp.render(context, request)
            else:
                title = self._get_dynamic_attr("item_title", item)
            if description_tmp is not None:
                description = description_tmp.render(context, request)
            else:
                description = self._get_dynamic_attr("item_description", item)
            link = add_domain(
                domain,
                self._get_dynamic_attr("item_link", item),
                request.is_secure(),
            )
            enclosures = self._get_dynamic_attr("item_enclosures", item)
            author_name = self._get_dynamic_attr("item_author_name", item)
            if author_name is not None:
                author_email = self._get_dynamic_attr("item_author_email", item)
                author_link = self._get_dynamic_attr("item_author_link", item)
            else:
                author_email = author_link = None

            tz = get_default_timezone()

            pubdate = self._get_dynamic_attr("item_pubdate", item)
            if pubdate and is_naive(pubdate):
                pubdate = make_aware(pubdate, tz)

            updateddate = self._get_dynamic_attr("item_updateddate", item)
            if updateddate and is_naive(updateddate):
                updateddate = make_aware(updateddate, tz)

            feed.add_item(
                title=title,
                link=link,
                description=description,
                unique_id=self._get_dynamic_attr("item_guid", item, link),
                unique_id_is_permalink=self._get_dynamic_attr(
                    "item_guid_is_permalink", item
                ),
                enclosures=enclosures,
                pubdate=pubdate,
                updateddate=updateddate,
                author_name=author_name,
                author_email=author_email,
                author_link=author_link,
                comments=self._get_dynamic_attr("item_comments", item),
                categories=self._get_dynamic_attr("item_categories", item),
                item_copyright=self._get_dynamic_attr("item_copyright", item),
                **self.item_extra_kwargs(item),
            )
        return feed


class CategoriesFeed(CustomFeed, Feed):
    title = "Categories"
    link = "/categories/"
    description = "List of product categories."

    def items(self):
        return Category.objects.all()

    def item_id(self, item):
        return item.id

    def item_parentId(self, item):
        return item.parent.id

    def item_title(self, item):
        return item.name
    
    def item_link(self, item):
        return reverse("shop:product_list_by_category", args=[item.slug])


class ProductsFeed(CustomFeed, Feed):
    title = "Offers"
    link = "/offers/"
    description = "List of product offers."

    def items(self):
        return Product.objects.all()

    def item_productId(self, item):
        return item.id

    def item_categoryId(self, item):
        return item.category.id

    def item_name(self, item):
        return item.name

    def item_link(self, item):
        return reverse("shop:product_detail", args=[item.category.slug, item.slug])


class AllFeedsXMLAPIView(APIView):

    queryset = Product.objects.all()

    def get(self, request, *args, **kwargs):
        products_feeds = CategoriesFeed().items()
        categories_feeds = ProductsFeed().items()

        # Serialize feed items to XML
        tmp = list(products_feeds)
        tmp.extend(list(categories_feeds))
        latest_entries_xml = serializers.serialize('xml', tmp)

        # Combine XML representations of feed items
        return HttpResponse(latest_entries_xml, content_type='application/xml')