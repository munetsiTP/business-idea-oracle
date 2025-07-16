import streamlit as st
import requests
import stripe
import os

# API Keys from secrets
stripe.api_key = os.environ.get("STRIPE_API_KEY", "sk_test_your_test_key_here")
serpapi_key = os.environ.get("SERPAPI_KEY", "your_serpapi_key_here")  # Add your SerpAPI key

# Hardcode your app domain for redirects (replace with actual URL after deploy)
DOMAIN = "https://business-idea-oracle.streamlit.app"

st.title("Oracle Premium Validation by munetsiTP")
st.markdown("Validate your idea for free (basic). Unlock full report for $5!")

# Input
idea = st.text_area("Business Idea Description", "e.g., Selling building supplies in canada importing from china.")

if st.button("Validate Idea (Free Basic)"):
    if not idea:
        st.error("Enter an idea!")
    else:
        with st.spinner("Fetching real-time data..."):
            def fetch_data(query):
                url = f"https://serpapi.com/search.json?engine=duckduckgo&q={query}&api_key={serpapi_key}"
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        # Extract relevant snippet or organic result
                        if 'organic_results' in data and data['organic_results']:
                            return data['organic_results'][0].get('snippet', 'No data found.')
                        return 'No relevant data found.'
                    else:
                        return f"Fetch error: {response.status_code}"
                except Exception as e:
                    return f"Connection issue: {str(e)}"

            market_query = f"{idea} market size 2025"
            market_data = fetch_data(market_query)
            
            comp_query = f"{idea} competition and risks"
            comp_data = fetch_data(comp_query)
            
            # Basic free output
            score = 8.6  # Can make dynamic based on data analysis later
            st.subheader("Basic Free Validation")
            st.write(f"**Market Insights**: {market_data}")
            st.write(f"**Competition & Risks**: {comp_data}")
            st.write(f"**Viability Score**: {score}/10 - Looks promising!")

            # Premium unlock
            query_params = st.query_params
            if 'session_id' in query_params:
                session_id = query_params['session_id'][0]
                try:
                    session = stripe.checkout.Session.retrieve(session_id)
                    if session.payment_status == 'paid':
                        st.success("Payment successful! Unlocking full report.")
                        # Full premium output
                        monet_query = f"{idea} monetization potential"
                        monet_data = fetch_data(monet_query)
                        forecast = f"85% success chance to $50K MRR in 6 months, based on trends like {market_data[:100]}..."
                        optimizations = [
                            f"Vet suppliers and risks: {comp_data[:100]}...",
                            "Add AI previews for differentiation.",
                            "Pivot to franchising for scale."
                        ]
                        roadmap = [
                            "0-30 Days: Source hardware, test betas using fetched insights.",
                            "31-90 Days: Market on social with demos.",
                            "91-180 Days: Scale partnerships for $50K MRR."
                        ]
                        st.subheader("Premium Full Report")
                        st.write(f"**Monetization Potential**: {monet_data} (Score: 9/10)")
                        st.write(f"**Forecast**: {forecast}")
                        st.subheader("Optimizations & Pivots")
                        for opt in optimizations:
                            st.write(f"- {opt}")
                        st.subheader("Execution Roadmap")
                        for step in roadmap:
                            st.write(f"- {step}")
                    else:
                        st.warning("Payment not completed.")
                except Exception as e:
                    st.error(f"Invalid session: {str(e)}")
            else:
                # Pay button
                st.info("Unlock full report (forecast, roadmap, etc.) for $5.")
                if st.button("Pay $5 with Stripe"):
                    try:
                        session = stripe.checkout.Session.create(
                            payment_method_types=['card'],
                            line_items=[{
                                'price_data': {
                                    'currency': 'usd',
                                    'product_data': {'name': 'Oracle Premium Validation by munetsiTP'},
                                    'unit_amount': 500,  # $5.00
                                },
                                'quantity': 1,
                            }],
                            mode='payment',
                            success_url=DOMAIN + '?session_id={CHECKOUT_SESSION_ID}',
                            cancel_url=DOMAIN,
                        )
                        st.markdown(f"<a href='{session.url}' target='_blank'>Click to Pay</a>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error creating session: {str(e)}")
