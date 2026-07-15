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
# TITLE
# ==========================================================
st.title("🏠 iGarage")
st.subheader("Buy & sell locally. Cashless.")
# ==========================================================
# SIDEBAR MENU
# ==========================================================
menu = st.sidebar.selectbox(
    "Menu",
    [
        "Browse Items",
        "Sell Item",
        "My Order Confirmation"
    ]
)
# ==========================================================
# SIDEBAR INFORMATION
# ==========================================================
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
    query = supabase.table(
        "garage_listings"
    ).select("*").eq(
        "status",
        "active"
    )
    listings = query.execute().data
    for item in listings:
        if filter_mode == "Buy Now":
            if item["purchase_mode"] not in ["buy_now", "both"]:
                continue
        if filter_mode == "Reserve":
            if item["purchase_mode"] not in ["reserve", "both"]:
                continue
        st.divider()
        st.subheader(item["title"])
        st.write(item["description"])
        st.write(
            f"💰 Price: ${item['price']}"
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
            "Payment options:",
            item["purchase_mode"]
        )
        if item["image_urls"]:
            for img in item["image_urls"]:
                st.image(img, width=150)
        if st.button(
            f"Buy {item['title']}",
            key=item["id"]
        ):
            order_token = str(uuid.uuid4())
            supabase.table(
                "garage_orders"
            ).insert({
                "listing_id": item["id"],
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
                "Order created!"
            )
            st.write(
                "Show order token:",
                order_token
            )
# ==========================================================
# SELL ITEM
# ==========================================================

if page == "Sell Item":

    st.header("Post Your Item")


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


    # Exchange method
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



    # Selling method
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



    # Images
    photos = st.file_uploader(
        "Upload up to 5 pictures",
        accept_multiple_files=True,
        type=[
            "png",
            "jpg",
            "jpeg"
        ]
    )


    if st.button("Post Item"):


        if not title or not seller_email:

            st.error(
                "Please enter title and email"
            )

        else:

            image_urls = []


            # Upload images
            for photo in photos[:5]:

                file_name = (
                    str(uuid.uuid4())
                    + "_"
                    + photo.name
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
                        SUPABASE_URL
                        + "/storage/v1/object/public/"
                        + "garage_images/"
                        + file_name
                    )


                    image_urls.append(
                        image_url
                    )


                except Exception as e:

                    st.error(
                        "Image upload failed"
                    )

                    st.write(e)



            # Save listing
            supabase.table(
                "garage_listings"
            ).insert({

                "title": title,

                "description": description,

                "price": price,

                "city": "Vancouver",

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
        order = supabase.table(
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
            "Trade confirmed!"
        )
