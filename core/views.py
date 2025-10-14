from django.shortcuts import render
from django.urls import reverse
from catalog.models import Product, Category, Tag


def home(request):
    products = (
        Product.objects.filter(is_active=True)
        .select_related("category")
        .prefetch_related("tags")
    )
    featured_products = products.filter(is_featured=True)[:6]
    hero_product = featured_products[0] if featured_products else None
    new_arrivals = products.order_by("-created_at")[:6]

    handcrafted_tag = Tag.objects.filter(slug="handcrafted").first()
    matching_sets = (
        products.filter(tags=handcrafted_tag) if handcrafted_tag else featured_products
    )
    matching_sets = matching_sets.distinct()[:4]

    primary_categories = (
        Category.objects.filter(is_active=True, parent__isnull=True)
        .order_by("sort_order", "name")
        .values("name", "slug", "description")
    )
    category_map = {c["slug"]: c for c in primary_categories}

    wear_collections = [
        {
            "key": "earrings",
            "title": "Earrings",
            "subtitle": "Studs, drops & climbers",
            "description": category_map.get("earrings", {}).get(
                "description",
                "From everyday ease to ceremonial sparkle, each pair is balanced for comfort.",
            ),
            "image": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=900&q=80",
            "cta_url": reverse("catalog:product_list") + "?division=earrings",
            "available": "earrings" in category_map,
        },
        {
            "key": "necklaces",
            "title": "Necklaces & Chains",
            "subtitle": "Layering links & pendants",
            "description": category_map.get("necklaces", {}).get(
                "description",
                "Hand-finished accents in gold, silver and pearl for statement necklines.",
            ),
            "image": "https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?auto=format&fit=crop&w=900&q=80",
            "cta_url": reverse("catalog:category", args=["necklaces"])
            if "necklaces" in category_map
            else reverse("catalog:product_list"),
            "available": "necklaces" in category_map,
        },
        {
            "key": "bracelets",
            "title": "Bracelets & Bangles",
            "subtitle": "Stackable memories",
            "description": category_map.get("bracelets", {}).get(
                "description",
                "Polished cuffs and beaded strands that celebrate movement.",
            ),
            "image": "https://images.unsplash.com/photo-1518544801976-3e159e06faa9?auto=format&fit=crop&w=900&q=80",
            "cta_url": reverse("catalog:category", args=["bracelets"])
            if "bracelets" in category_map
            else reverse("catalog:product_list"),
            "available": "bracelets" in category_map,
        },
        {
            "key": "rings",
            "title": "Rings",
            "subtitle": "Symbols & everyday bands",
            "description": category_map.get("rings", {}).get(
                "description",
                "Timeless silhouettes for proposals, milestones and self-celebration.",
            ),
            "image": "https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?auto=format&fit=crop&w=900&q=80",
            "cta_url": reverse("catalog:category", args=["rings"])
            if "rings" in category_map
            else reverse("catalog:product_list"),
            "available": "rings" in category_map,
        },
    ]

    service_promises = [
        {
            "icon": "ph-truck",
            "title": "Complimentary delivery",
            "description": "Free shipping across Kenya with real-time updates and insured packaging.",
        },
        {
            "icon": "ph-credit-card",
            "title": "Flexible payments",
            "description": "Pay via M-Pesa, card or secure cash on delivery — no currency switching.",
        },
        {
            "icon": "ph-rose",
            "title": "Care for life",
            "description": "Lifetime cleaning and complimentary adjustments for TAC pieces.",
        },
    ]

    story_stats = [
        {"value": "200+", "label": "Artisans empowered", "detail": "Kenyan beadwork, metal and weaving collectives"},
        {"value": "35", "label": "Communities", "detail": "Partner sites from the coast to the highlands"},
        {"value": "72h", "label": "Bespoke turnaround", "detail": "Initial concepts delivered after consultation"},
        {"value": "100%", "label": "Locally sourced", "detail": "Materials traced through community suppliers"},
    ]

    journal_entries = [
        {
            "category": "Community",
            "title": "Meet the women metal smiths of Kibera",
            "summary": "How TAC commissions translate into sustainable incomes for Nairobi makers.",
            "url": "#",
        },
        {
            "category": "Styling",
            "title": "Layering nude tones with statement metals",
            "summary": "Pairing Dusty Rose stones with muted textiles for effortless shine.",
            "url": "#",
        },
        {
            "category": "Gifting",
            "title": "Corporate gifting that celebrates heritage",
            "summary": "Curated sets for leadership retreats, anniversaries and executive thank-yous.",
            "url": "#",
        },
    ]

    corporate_highlights = [
        {
            "title": "Tailored gift suites",
            "description": "Curate matching sets with bespoke engraving or brand colour stories.",
        },
        {
            "title": "Sustainable sourcing",
            "description": "Materials tracked from co-ops with transparent impact reporting.",
        },
        {
            "title": "White-glove fulfilment",
            "description": "Personalised notes, premium wrap and scheduled deliveries for VIP recipients.",
        },
    ]

    fallback_hero_images = [
        "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=1080&q=80",
        "https://images.unsplash.com/photo-1500043201393-22f936026727?auto=format&fit=crop&w=1080&q=80",
        "https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?auto=format&fit=crop&w=1080&q=80",
    ]

    hero_slides = []

    def hero_image(product, fallback_url):
        if not product:
            return fallback_url
        image = getattr(product, "primary_image", None)
        return image or fallback_url

    def hero_alt(product, default_text):
        name = getattr(product, "name", None) if product else None
        return name or default_text

    primary_slide_product = hero_product or (new_arrivals[0] if new_arrivals else None)
    hero_slides.append({
        "eyebrow": "Heritage · Craft · Soul",
        "title": primary_slide_product.name if primary_slide_product else "Earth-forged African jewellery for celebrations of culture and kinship.",
        "description": primary_slide_product.short_description if primary_slide_product and primary_slide_product.short_description else "From beadwork in Maai Mahiu to brass ateliers in Nairobi, each TAC piece honours our communities with bold silhouettes and enduring materials.",
        "primary": {
            "text": "Shop the collection",
            "url": reverse("catalog:product_detail", args=[primary_slide_product.slug]) if primary_slide_product else reverse("catalog:product_list"),
        },
        "secondary": {
            "text": "Discover our ateliers",
            "url": "#community",
        },
        "chips": [
            {"label": "Hand-finished in Kenya"},
            {"label": "Warm brass · Reclaimed horn", "variant": "ghost"},
            {"label": "Community investment in every order", "variant": "ghost"},
        ],
        "image": hero_image(primary_slide_product, fallback_hero_images[0]),
        "image_alt": hero_alt(primary_slide_product, "Brass and bead jewellery set"),
        "badge_title": "Nguvu ya Jamii",
        "badge_lines": [
            "200+ artisans across Kenya shape TAC pieces.",
            "Each order funds apprenticeships & fair wages.",
        ],
        "overlays": [
            {
                "image": fallback_hero_images[1],
                "style": "top:12%;right:-40px;transform:rotate(-6deg);",
            },
            {
                "image": fallback_hero_images[2],
                "style": "bottom:8%;left:-40px;transform:rotate(7deg);",
            },
        ],
    })

    secondary_product = next((p for p in new_arrivals if p != primary_slide_product), None)
    hero_slides.append({
        "eyebrow": "Statement · Colour · Motion",
        "title": "Marrying Maasai bead palettes with modern brass geometry.",
        "description": "Layer vibrant chokers with sculpted cuffs inspired by coastal architecture. Build a wardrobe that translates ceremonies into contemporary silhouettes.",
        "primary": {
            "text": "Build your stack",
            "url": reverse("catalog:product_list") + "?division=bracelets",
        },
        "secondary": {
            "text": "Request styling edit",
            "url": "#journal",
        },
        "chips": [
            {"label": "Vibrant hues", "variant": "ghost"},
            {"label": "Bead weaving collectives"},
            {"label": "Limited seasonal drops", "variant": "ghost"},
        ],
        "image": hero_image(secondary_product, fallback_hero_images[1]),
        "image_alt": hero_alt(secondary_product, "Layered African beaded bangles"),
        "badge_title": "Limited drop",
        "badge_lines": [
            "Only 60 sets crafted this season.",
            "Complimentary resizing & care.",
        ],
        "overlays": [
            {
                "image": fallback_hero_images[0],
                "style": "top:16%;left:-45px;transform:rotate(5deg);",
            },
            {
                "image": fallback_hero_images[2],
                "style": "bottom:10%;right:-35px;transform:rotate(-8deg);",
            },
        ],
    })

    hero_slides.append({
        "eyebrow": "Gifting · Legacy",
        "title": "Corporate and ceremonial gifts that tell an African story.",
        "description": "Commission bespoke suites for leadership retreats, anniversaries, and partners. Each parcel ships with artisan notes, provenance, and sustainable packaging.",
        "primary": {
            "text": "Start a gifting brief",
            "url": "mailto:hello@tacaccessories.com",
        },
        "secondary": {
            "text": "Browse matching sets",
            "url": "#matching-sets",
        },
        "chips": [
            {"label": "Impact reports"},
            {"label": "Custom engraving", "variant": "ghost"},
            {"label": "Signature packaging"},
        ],
        "image": fallback_hero_images[2],
        "image_alt": "Corporate gifting presentation",
        "badge_title": "Karibu",
        "badge_lines": [
            "White-glove fulfilment & timed delivery.",
            "Story cards in English & Kiswahili.",
        ],
        "overlays": [
            {
                "image": fallback_hero_images[1],
                "style": "top:18%;right:-38px;transform:rotate(-10deg);",
            },
            {
                "image": fallback_hero_images[0],
                "style": "bottom:12%;left:-32px;transform:rotate(6deg);",
            },
        ],
    })

    context = {
        "featured_products": featured_products,
        "hero_slides": hero_slides,
        "new_arrivals": new_arrivals,
        "matching_sets": matching_sets,
        "wear_collections": wear_collections,
        "service_promises": service_promises,
        "story_stats": story_stats,
        "journal_entries": journal_entries,
        "corporate_highlights": corporate_highlights,
    }
    return render(request, "home.html", context)
