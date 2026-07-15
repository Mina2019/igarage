# ==========================================================
# iGarage
# Local Cashless Marketplace
# Streamlit + Supabase
# ==========================================================

import streamlit as st
from supabase import create_client
from datetime import datetime
import uuid


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
        "My Order Confirmation"
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


                st.success("✅ Order Created!")
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
        image_urls = []
        # Upload images
        for photo in photos[:5]:
            file_name = f"{uuid.uuid4()}_{photo.name}"
            try:
                result = supabase.storage.from_("garage_images").upload(
                    file_name,
                    photo.getvalue(),
                    {
                        "content-type": photo.type,
                        "upsert": "true"
                    }
                )

                image_url = (
                    f"{SUPABASE_URL}/storage/v1/object/public/"
                    f"garage_images/{file_name}"
                )

                image_urls.append(image_url)

                st.success(f"Uploaded {photo.name}")

            except Exception as e:

                st.error("Image upload failed")
                st.exception(e)
                st.stop()
        supabase.table(
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
            "image_urls":
                image_urls
        }).execute()
        st.success(
            "✅ Item posted successfully!"
        )
# ==========================================================
# CONFIRM TRANSACTION
# ==========================================================
if menu == "My Order Confirmation":
    st.header(
        "Confirm Trade"
    )
    token = st.text_input(
        "Enter order token"
    )
    if st.button(
        "Confirm Trade Completed"
    ):
        supabase.table(
            "garage_orders"
        ).update({
            "order_status":
                "completed",
            "completed_at":
                datetime.now().isoformat()
        }).eq(
            "order_token",
            token
        ).execute()


        st.success(
            "✅ Trade confirmed!"
        )
