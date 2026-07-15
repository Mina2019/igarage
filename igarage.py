# ==========================================================
# iGarage
# Local Cashless Marketplace
# Streamlit + Supabase
# ==========================================================

import streamlit as st
from supabase import create_client
from datetime import datetime
import uuid
import re

# ==========================================================
# SUPABASE CONNECTION
# ==========================================================

SUPABASE_URL = "https://xbdlzzjparnvrsvsjfca.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhiZGx6empwYXJudnJzdnNqZmNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc5MzQ0NDYsImV4cCI6MjA5MzUxMDQ0Nn0.h0AxxjVJZWpTCkywH-Et30TCn4nKQwGXfvmPbVmgZJo"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ==========================================================
# PAGE SETTINGS
# ==========================================================

st.set_page_config(
    page_title="iGarage",
    page_icon="🏠",
    layout="wide"
)
# ==========================================================
# HEADER
# ==========================================================

st.title("🏠 iGarage")
st.subheader("Buy & sell locally. Cashless.")


# ==========================================================
# SIDEBAR
# ==========================================================

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Browse Items",
        "Sell Item",
        "My Ads",
        "Seller Confirmation",
        "Buyer Confirmation"
    ]
)


st.sidebar.divider()

st.sidebar.info(
    "💳 iGarage Platform Fee\n\n"
    "$1 per completed transaction"
)

# ==========================================================
# BROWSE ITEMS
# ==========================================================

if menu == "Browse Items":

    st.header("Available Items")


    filter_mode = st.selectbox(
        "Filter",
        [
            "All",
            "Buy Now",
            "Reserve"
        ]
    )


    listings = supabase.table(
        "garage_listings"
    ).select("*").eq(
        "status",
        "active"
    ).execute().data


    for item in listings:


        if filter_mode == "Buy Now":

            if item["purchase_mode"] not in [
                "buy_now",
                "both"
            ]:
                continue


        if filter_mode == "Reserve":

            if item["purchase_mode"] not in [
                "reserve",
                "both"
            ]:
                continue


        st.divider()


        col1, col2 = st.columns(
            [1, 2]
        )


        with col1:

            if item["image_urls"]:

                st.image(
                    item["image_urls"][0],
                    width=200
                )


        with col2:

            st.subheader(
                item["title"]
            )


            st.write(
                item["description"]
            )


            st.write(
                f"💰 Item price: ${item['price']}"
            )


            st.write(
                "💳 iGarage fee: $1"
            )


            st.write(
                f"Total: ${item['price'] + 1}"
            )


            if item["exchange_type"] == "meet":

                st.success(
                    "📍 Meet at Metropolis at Metrotown"
                )

            else:

                st.warning(
                    "🏠 Pickup from seller"
                )


            st.write(
                "Payment option:",
                item["purchase_mode"]
            )

           
            if st.button(
                "Buy Now",
                key=item["id"]
            ):

                order_token = str(
                    uuid.uuid4()
                )

                supabase.table(
                    "garage_orders"
                ).insert({

                    "listing_id":
                        item["id"],

                    "buyer_email":
                        "buyer@example.com",

                    "seller_email":
                        item["seller_email"],

                    "item_price":
                        item["price"],

                    "platform_fee":
                        1,

                    "total_paid":
                        item["price"] + 1,

                    "order_status":
                        "paid",

                    "order_token":
                        order_token

                }).execute()


                st.success(
                    "✅ Order Created!"
                )


                st.write(
                    f"**Seller Email:** {item['seller_email']}"
                )


                if item["exchange_type"] == "meet":

                    st.info(
                        "📍 Meet at Metropolis at Metrotown.\n\n"
                        "Please email the seller to arrange a convenient meeting time."
                    )

                else:

                    st.info(
                        "🏠 Pickup from seller.\n\n"
                        "Please email the seller to arrange a pickup time."
                    )

        
# ==========================================================
# SELL ITEM
# ==========================================================

if menu == "Sell Item":

    st.header(
        "Post Your Item"
    )


    title = st.text_input(
        "Item title"
    )


    description = st.text_area(
        "Description"
    )


    price = st.number_input(
        "Price ($)",
        min_value=1
    )


    seller_email = st.text_input(
        "Your email"
    )


    exchange = st.selectbox(
        "Exchange Method",
        [
            "Meet at Metropolis at Metrotown",
            "Pickup from seller"
        ]
    )


    if exchange == "Meet at Metropolis at Metrotown":

        exchange_type = "meet"

    else:

        exchange_type = "pickup"



    purchase = st.selectbox(
        "Selling Method",
        [
            "Buy Now only",
            "Reserve only",
            "Both"
        ]
    )


    if purchase == "Buy Now only":

        purchase_mode = "buy_now"

    elif purchase == "Reserve only":

        purchase_mode = "reserve"

    else:

        purchase_mode = "both"



    photos = st.file_uploader(
        "Upload up to 5 pictures",
        accept_multiple_files=True,
        type=[
            "png",
            "jpg",
            "jpeg"
        ]
    )


    if st.button(
        "Post Item"
    ):


        # ==========================
        # CHECK EMAIL
        # ==========================

        if not seller_email.strip():

            st.error(
                "Please enter your email."
            )

            st.stop()


        if not re.match(
            r"^[^@]+@[^@]+\.[^@]+$",
            seller_email
        ):

            st.error(
                "Please enter a valid email address."
            )

            st.stop()



        image_urls = []


        # ==========================
        # UPLOAD IMAGES
        # ==========================

        if photos:

            for photo in photos[:5]:

                file_name = (
                    f"{uuid.uuid4()}_{photo.name}"
                )


                try:

                    supabase.storage.from_(
                        "garage_images"
                    ).upload(
                        file_name,
                        photo.getvalue(),
                        {
                            "content-type":
                            photo.type
                        }
                    )
                    image_url = (
                        f"{SUPABASE_URL}"
                        "/storage/v1/object/public/"
                        f"garage_images/{file_name}"
                    )
                    image_urls.append(
                        image_url
                    )
                except Exception as e:
                    st.error(
                        "Image upload failed"
                    )
                    st.exception(e)
                    st.stop()
        # ==========================
        # SAVE LISTING
        # ==========================
        listing_token = str(uuid.uuid4())
        
        result = supabase.table(
            "garage_listings"
        ).insert({
            "title":
                title,
            "description":
                description,
            "price":
                price,
            "city":
                "Vancouver",
            "exchange_type":
                exchange_type,
            "purchase_mode":
                purchase_mode,
            "seller_email":
                seller_email,
            "listing_token": listing_token,
            "image_urls":
                image_urls
        }).execute()
        st.success(
            "✅ Item posted successfully!"
        )
        st.write(
            "Seller email saved:",
            seller_email
        )


# ==========================================================
# MY ADS
# ==========================================================

if menu == "My Ads":
    st.header("My Ads")
    seller_email = st.text_input(
        "Enter your seller email"
    )
    if st.button("Show My Ads"):
        ads = supabase.table(
            "garage_listings"
        ).select("*").eq(
            "seller_email",
            seller_email
        ).execute().data
        if not ads:
            st.warning(
                "No ads found."
            )
        for ad in ads:
            st.divider()
            st.subheader(
                ad["title"]
            )
            st.write(
                f"💰 Price: ${ad['price']}"
            )
            if ad["image_urls"]:
                st.image(
                    ad["image_urls"][0],
                    width=150
                )
            st.write(
                    f"🆔 Listing ID: {ad['listing_token']}"
                )
         
            if st.button(
                "🗑 Delete Ad",
                key=f"delete_{ad['id']}"
            ):
                supabase.table(
                    "garage_listings"
                ).delete().eq(
                    "id",
                    ad["id"]
                ).execute()
                st.success(
                    "Ad deleted successfully!"
                )
                st.rerun()

# ==========================================================
# SELLER CONFIRMATION
# ==========================================================

if menu == "Seller Confirmation":

    st.header("Confirm Transaction")

    token = st.text_input("Transaction ID")

    if st.button("Find Transaction"):

        listing = supabase.table(
                "garage_listings"
            ).select("*").eq(
                "listing_token",
                token
            ).execute().data

        if len(listing) == 0:

            st.error("Listing not found.")

        else:

            listing = listing[0]

            st.success("Listing found!")

            st.write(f"Item: {listing['title']}")
            st.write(f"Price: ${listing['price']}")
            st.write(f"Seller: {listing['seller_email']}")

            if st.button("✅ item delivered to buyer"):

                st.success("Delivery confirmed. Waiting for buyer confirmation.")

# ==========================================================
# BUYER CONFIRMATION
# ==========================================================

if menu == "Buyer Confirmation":

    st.header("Buyer Confirmation")

    listing_token = st.text_input(
        "Enter Listing ID"
    )

    if st.button("Find Listing"):

        listing = supabase.table(
            "garage_listings"
        ).select("*").eq(
            "listing_token",
            listing_token
        ).execute().data


        if len(listing) == 0:

            st.error(
                "Listing not found."
            )

        else:

            listing = listing[0]

            st.success(
                "Listing found!"
            )

            st.write(
                f"Item: {listing['title']}"
            )

            st.write(
                f"Price: ${listing['price']}"
            )

            st.write(
                f"Seller: {listing['seller_email']}"
            )


            st.divider()


            st.write(
                "Seller has delivered the item?"
            )


            if st.button(
                "✅ I Received the Item"
            ):

                st.success(
                    "Buyer confirmation completed!"
                )
